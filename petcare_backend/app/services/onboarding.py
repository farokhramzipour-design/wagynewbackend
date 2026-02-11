from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import (
    ProviderServiceStepProgress,
    ServiceOnboardingFlow,
    ServiceOnboardingStep,
)
from app.models.providers import Provider, ProviderService, ProviderVerification


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _validate_step_completion(step: ServiceOnboardingStep, data_json: dict | None) -> None:
    rules = step.completion_rule_json or {}
    required_fields = rules.get("required_fields", [])
    if required_fields:
        if not data_json:
            raise HTTPException(status_code=400, detail="step_data_missing")
        missing = [f for f in required_fields if f not in data_json]
        if missing:
            raise HTTPException(status_code=400, detail={"missing_fields": missing})


async def create_flow(session: AsyncSession, *, payload: dict) -> ServiceOnboardingFlow:
    if payload.get("is_active"):
        await session.execute(
            ServiceOnboardingFlow.__table__.update()
            .where(ServiceOnboardingFlow.service_type_id == payload["service_type_id"])
            .values(is_active=False)
        )
    flow = ServiceOnboardingFlow(**payload)
    session.add(flow)
    await session.commit()
    await session.refresh(flow)
    return flow


async def create_step(session: AsyncSession, *, payload: dict) -> ServiceOnboardingStep:
    step = ServiceOnboardingStep(**payload)
    session.add(step)
    await session.commit()
    await session.refresh(step)
    return step


async def get_active_flow(session: AsyncSession, *, service_type_id: int) -> ServiceOnboardingFlow:
    flow = await session.scalar(
        select(ServiceOnboardingFlow).where(
            ServiceOnboardingFlow.service_type_id == service_type_id,
            ServiceOnboardingFlow.is_active.is_(True),
        )
    )
    if not flow:
        raise HTTPException(status_code=404, detail="flow_not_found")
    return flow


async def list_steps(session: AsyncSession, *, flow_id: int) -> list[ServiceOnboardingStep]:
    return (
        await session.scalars(
            select(ServiceOnboardingStep)
            .where(ServiceOnboardingStep.flow_id == flow_id)
            .order_by(ServiceOnboardingStep.sort_order.asc())
        )
    ).all()


async def enable_service(
    session: AsyncSession, *, provider_id: int, service_type_id: int
) -> ProviderService:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")
    if provider.status != "approved":
        raise HTTPException(status_code=403, detail="provider_not_approved")

    flow = await get_active_flow(session, service_type_id=service_type_id)
    provider_service = await session.scalar(
        select(ProviderService).where(
            ProviderService.provider_id == provider_id,
            ProviderService.service_type_id == service_type_id,
        )
    )
    if provider_service:
        return provider_service

    provider_service = ProviderService(
        provider_id=provider_id,
        service_type_id=service_type_id,
        is_active=True,
        status="incomplete",
        flow_version=flow.version,
    )
    session.add(provider_service)
    await session.flush()

    steps = await list_steps(session, flow_id=flow.flow_id)
    for step in steps:
        session.add(
            ProviderServiceStepProgress(
                provider_service_id=provider_service.provider_service_id,
                step_id=step.step_id,
                status="not_started",
                data_json=None,
            )
        )

    await session.commit()
    await session.refresh(provider_service)
    return provider_service


async def list_step_progress(
    session: AsyncSession, *, provider_service_id: int
) -> list[ProviderServiceStepProgress]:
    return (
        await session.scalars(
            select(ProviderServiceStepProgress).where(
                ProviderServiceStepProgress.provider_service_id == provider_service_id
            )
        )
    ).all()


async def save_step_data(
    session: AsyncSession, *, provider_service_id: int, step_id: int, data_json: dict | None
) -> ProviderServiceStepProgress:
    progress = await session.scalar(
        select(ProviderServiceStepProgress).where(
            ProviderServiceStepProgress.provider_service_id == provider_service_id,
            ProviderServiceStepProgress.step_id == step_id,
        )
    )
    if not progress:
        raise HTTPException(status_code=404, detail="step_progress_not_found")

    progress.data_json = data_json
    if progress.status == "not_started":
        progress.status = "in_progress"

    await _apply_step_side_effects(session, provider_service_id=provider_service_id, step_id=step_id, data_json=data_json)

    await session.commit()
    await session.refresh(progress)
    return progress


async def complete_step(
    session: AsyncSession, *, provider_service_id: int, step_id: int, data_json: dict | None
) -> ProviderServiceStepProgress:
    progress = await session.scalar(
        select(ProviderServiceStepProgress).where(
            ProviderServiceStepProgress.provider_service_id == provider_service_id,
            ProviderServiceStepProgress.step_id == step_id,
        )
    )
    if not progress:
        raise HTTPException(status_code=404, detail="step_progress_not_found")

    step = await session.get(ServiceOnboardingStep, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="step_not_found")

    if data_json is not None:
        progress.data_json = data_json

    _validate_step_completion(step, progress.data_json)
    progress.status = "completed"
    progress.completed_at = _utcnow()

    await _apply_step_side_effects(session, provider_service_id=provider_service_id, step_id=step_id, data_json=progress.data_json)

    await session.commit()
    await session.refresh(progress)
    return progress


async def submit_service(session: AsyncSession, *, provider_service_id: int) -> ProviderService:
    provider_service = await session.get(ProviderService, provider_service_id)
    if not provider_service:
        raise HTTPException(status_code=404, detail="provider_service_not_found")

    if provider_service.status not in {"incomplete", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_status_transition")

    progress = await list_step_progress(session, provider_service_id=provider_service_id)
    required_steps = [p for p in progress if p.status != "completed"]
    if required_steps:
        raise HTTPException(status_code=400, detail="steps_incomplete")

    provider_service.status = "pending_review"
    provider_service.submitted_at = _utcnow()
    await session.commit()
    await session.refresh(provider_service)
    return provider_service


async def admin_update_service_status(
    session: AsyncSession, *, provider_service_id: int, status: str, review_note: str | None
) -> ProviderService:
    provider_service = await session.get(ProviderService, provider_service_id)
    if not provider_service:
        raise HTTPException(status_code=404, detail="provider_service_not_found")

    if status not in {"approved", "rejected", "suspended"}:
        raise HTTPException(status_code=400, detail="invalid_status")

    provider_service.status = status
    provider_service.review_note = review_note
    provider_service.reviewed_at = _utcnow()
    if status == "approved":
        provider_service.approved_at = _utcnow()

    await session.commit()
    await session.refresh(provider_service)
    return provider_service


async def admin_reject_step(
    session: AsyncSession, *, provider_service_id: int, step_id: int, review_note: str | None
) -> ProviderServiceStepProgress:
    progress = await session.scalar(
        select(ProviderServiceStepProgress).where(
            ProviderServiceStepProgress.provider_service_id == provider_service_id,
            ProviderServiceStepProgress.step_id == step_id,
        )
    )
    if not progress:
        raise HTTPException(status_code=404, detail="step_progress_not_found")

    progress.status = "rejected"
    progress.review_note = review_note

    provider_service = await session.get(ProviderService, provider_service_id)
    if provider_service:
        provider_service.status = "incomplete"

    await session.commit()
    await session.refresh(progress)
    return progress


async def _apply_step_side_effects(
    session: AsyncSession, *, provider_service_id: int, step_id: int, data_json: dict | None
) -> None:
    if not data_json:
        return
    step = await session.get(ServiceOnboardingStep, step_id)
    if not step:
        return
    provider_service = await session.get(ProviderService, provider_service_id)
    if not provider_service:
        return

    if step.code == "service_area" and isinstance(data_json.get("radius_km"), int):
        provider_service.service_area_radius_km = data_json.get("radius_km")


async def get_provider_onboarding_summary(
    session: AsyncSession, *, provider_id: int
) -> dict:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    verifications = (
        await session.scalars(
            select(ProviderVerification).where(ProviderVerification.provider_id == provider_id)
        )
    ).all()

    services = (
        await session.scalars(
            select(ProviderService).where(ProviderService.provider_id == provider_id)
        )
    ).all()

    service_summaries = []
    for service in services:
        progress = await list_step_progress(
            session, provider_service_id=service.provider_service_id
        )
        missing_steps = [
            (await session.get(ServiceOnboardingStep, p.step_id)).code
            for p in progress
            if p.status != "completed"
        ]
        service_summaries.append(
            {
                "provider_service_id": service.provider_service_id,
                "service_type_id": service.service_type_id,
                "status": service.status,
                "missing_steps": missing_steps,
            }
        )

    return {
        "provider_id": provider.provider_id,
        "provider_status": provider.status,
        "verifications": [
            {"type": v.type, "status": v.status, "verified_at": v.verified_at}
            for v in verifications
        ],
        "services": service_summaries,
    }


async def get_service_review_view(
    session: AsyncSession, *, provider_service_id: int
) -> dict:
    provider_service = await session.get(ProviderService, provider_service_id)
    if not provider_service:
        raise HTTPException(status_code=404, detail="provider_service_not_found")

    rows = await session.execute(
        select(ProviderServiceStepProgress, ServiceOnboardingStep)
        .join(ServiceOnboardingStep, ServiceOnboardingStep.step_id == ProviderServiceStepProgress.step_id)
        .where(ProviderServiceStepProgress.provider_service_id == provider_service_id)
        .order_by(ServiceOnboardingStep.sort_order.asc())
    )
    steps = []
    for p, step in rows:
        steps.append(
            {
                "step_id": p.step_id,
                "code": step.code,
                "status": p.status,
                "data_json": p.data_json,
                "review_note": p.review_note,
                "completed_at": p.completed_at,
            }
        )

    return {
        "provider_service_id": provider_service.provider_service_id,
        "status": provider_service.status,
        "review_note": provider_service.review_note,
        "steps": steps,
    }
