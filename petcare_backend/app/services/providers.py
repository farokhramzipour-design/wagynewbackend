import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import ProviderServiceStepProgress, ServiceOnboardingStep
from app.models.providers import (
    Provider,
    ProviderHome,
    ProviderService,
    ProviderServiceRate,
    ProviderVerification,
)
from app.models.services import ServiceType
from app.models.users import UserProfile, UserVerification
from app.services.onboarding import get_active_flow

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


async def create_provider_draft(session: AsyncSession, *, user_id: int) -> Provider:
    existing = await session.scalar(select(Provider).where(Provider.user_id == user_id))
    if existing:
        raise HTTPException(status_code=409, detail="provider_already_exists")

    provider = Provider(user_id=user_id, status="draft")
    session.add(provider)
    await session.commit()
    await session.refresh(provider)
    return provider


async def update_provider_profile(
    session: AsyncSession, *, provider_id: int, updates: dict
) -> Provider:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    for field, value in updates.items():
        setattr(provider, field, value)

    await session.commit()
    await session.refresh(provider)
    return provider


async def upsert_provider_home(
    session: AsyncSession, *, provider_id: int, payload: dict
) -> ProviderHome:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    home = await session.get(ProviderHome, provider_id)
    if not home:
        home = ProviderHome(provider_id=provider_id, **payload)
        session.add(home)
    else:
        for field, value in payload.items():
            setattr(home, field, value)

    await session.commit()
    await session.refresh(home)
    return home


async def create_provider_verification(
    session: AsyncSession, *, provider_id: int, payload: dict
) -> ProviderVerification:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    verification = ProviderVerification(provider_id=provider_id, **payload)
    session.add(verification)
    await session.commit()
    await session.refresh(verification)
    return verification


async def upsert_provider_service(
    session: AsyncSession, *, provider_id: int, payload: dict
) -> ProviderService:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    service_type = await session.get(ServiceType, payload["service_type_id"])
    if not service_type:
        raise HTTPException(status_code=404, detail="service_type_not_found")

    provider_service = await session.scalar(
        select(ProviderService).where(
            ProviderService.provider_id == provider_id,
            ProviderService.service_type_id == payload["service_type_id"],
        )
    )

    if provider_service:
        provider_service.is_active = payload["is_active"]
        provider_service.max_pets = payload.get("max_pets")
    else:
        flow = await get_active_flow(session, service_type_id=payload["service_type_id"])
        provider_service = ProviderService(
            provider_id=provider_id,
            status="incomplete",
            flow_version=flow.version,
            **payload,
        )
        session.add(provider_service)

    await session.commit()
    await session.refresh(provider_service)
    return provider_service


async def create_provider_service_rate(
    session: AsyncSession, *, provider_service_id: int, payload: dict
) -> ProviderServiceRate:
    provider_service = await session.get(ProviderService, provider_service_id)
    if not provider_service:
        raise HTTPException(status_code=404, detail="provider_service_not_found")

    rate = ProviderServiceRate(provider_service_id=provider_service_id, **payload)
    session.add(rate)
    await session.commit()
    await session.refresh(rate)
    return rate


async def estimate_provider_rate(
    session: AsyncSession, *, provider_service_id: int, pets_count: int, is_puppy: bool, is_holiday: bool
) -> dict:
    rate = await session.scalar(
        select(ProviderServiceRate)
        .where(ProviderServiceRate.provider_service_id == provider_service_id)
        .order_by(ProviderServiceRate.created_at.desc())
    )
    if not rate:
        raise HTTPException(status_code=404, detail="rate_not_found")

    subtotal = rate.base_amount_minor
    if pets_count > 1 and rate.additional_pet_amount_minor is not None:
        subtotal += rate.additional_pet_amount_minor * (pets_count - 1)
    if is_puppy and rate.puppy_surcharge_minor is not None:
        subtotal += rate.puppy_surcharge_minor
    total = subtotal
    if is_holiday and rate.holiday_surcharge_percent is not None:
        total += int(subtotal * (rate.holiday_surcharge_percent / 100))

    breakdown = {
        "rate_id": rate.rate_id,
        "base_amount_minor": rate.base_amount_minor,
        "additional_pet_amount_minor": rate.additional_pet_amount_minor,
        "puppy_surcharge_minor": rate.puppy_surcharge_minor,
        "holiday_surcharge_percent": rate.holiday_surcharge_percent,
        "pets_count": pets_count,
        "is_puppy": is_puppy,
        "is_holiday": is_holiday,
    }
    return {"subtotal_minor": subtotal, "total_minor": total, "breakdown_json": breakdown}


async def submit_provider_review(session: AsyncSession, *, provider_id: int) -> Provider:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    if provider.status not in {"draft", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_status_transition")

    provider.status = "pending_review"
    await session.commit()
    await session.refresh(provider)
    return provider


async def admin_decide_provider(
    session: AsyncSession, *, provider_id: int, status: str, admin_user_id: int, reason: str | None
) -> Provider:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    if status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_decision")

    if provider.status != "pending_review":
        raise HTTPException(status_code=400, detail="invalid_status_transition")

    provider.status = status
    await session.commit()
    await session.refresh(provider)

    logger.info(
        "provider_admin_decision",
        extra={
            "provider_id": provider_id,
            "admin_user_id": admin_user_id,
            "status": status,
            "reason": reason,
            "decided_at": _utcnow().isoformat(),
        },
    )
    return provider


async def get_provider_profile(session: AsyncSession, *, provider_id: int) -> dict:
    provider = await session.get(Provider, provider_id)
    if not provider or provider.status != "approved":
        raise HTTPException(status_code=404, detail="provider_not_found")

    user_profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == provider.user_id)
    )
    home = await session.get(ProviderHome, provider_id)

    service_rows = (
        await session.execute(
            select(ProviderService, ServiceType)
            .join(ServiceType, ServiceType.service_type_id == ProviderService.service_type_id)
            .where(
                ProviderService.provider_id == provider_id,
                ProviderService.is_active.is_(True),
                ProviderService.status == "approved",
                ServiceType.is_active.is_(True),
            )
        )
    ).all()

    provider_verified = await session.scalar(
        select(ProviderVerification.provider_verification_id)
        .where(
            ProviderVerification.provider_id == provider_id,
            ProviderVerification.status == "passed",
        )
        .limit(1)
    )
    identity_verified = await session.scalar(
        select(UserVerification.verification_id)
        .where(
            UserVerification.user_id == provider.user_id,
            UserVerification.type == "identity",
            UserVerification.status == "passed",
        )
        .limit(1)
    )

    services = []
    for provider_service, service_type in service_rows:
        rate = await session.scalar(
            select(ProviderServiceRate)
            .where(ProviderServiceRate.provider_service_id == provider_service.provider_service_id)
            .order_by(ProviderServiceRate.created_at.desc())
        )

        policies = await session.scalar(
            select(ProviderServiceStepProgress.data_json)
            .join(
                ServiceOnboardingStep,
                ServiceOnboardingStep.step_id == ProviderServiceStepProgress.step_id,
            )
            .where(
                ProviderServiceStepProgress.provider_service_id
                == provider_service.provider_service_id,
                ProviderServiceStepProgress.status == "completed",
                ServiceOnboardingStep.code == "policies",
            )
        )

        services.append(
            {
                "provider_service_id": provider_service.provider_service_id,
                "service_type_id": provider_service.service_type_id,
                "service_code": service_type.code,
                "status": provider_service.status,
                "is_active": provider_service.is_active,
                "max_pets": provider_service.max_pets,
                "currency_code": rate.currency_code if rate else None,
                "unit": rate.unit if rate else None,
                "base_amount_minor": rate.base_amount_minor if rate else None,
                "duration_minutes": rate.duration_minutes if rate else None,
                "policies_json": policies,
            }
        )

    return {
        "provider": provider,
        "user_profile": user_profile,
        "home": home,
        "services": services,
        "provider_verified": provider_verified is not None,
        "identity_verified": identity_verified is not None,
    }
