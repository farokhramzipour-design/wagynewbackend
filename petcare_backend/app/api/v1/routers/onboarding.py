from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.schemas.onboarding import (
    ProviderOnboardingSummaryOut,
    ProviderServiceEnable,
    ProviderServiceReviewOut,
    ProviderServiceStatusUpdate,
    ProviderServiceStepComplete,
    ProviderServiceStepProgressOut,
    ProviderServiceStepSave,
    ProviderServiceSubmit,
    ServiceOnboardingFlowCreate,
    ServiceOnboardingFlowOut,
    ServiceOnboardingStepCreate,
    ServiceOnboardingStepOut,
)
from app.services.onboarding import (
    admin_reject_step,
    admin_update_service_status,
    complete_step,
    create_flow,
    create_step,
    enable_service,
    get_provider_onboarding_summary,
    get_active_flow,
    get_service_review_view,
    list_step_progress,
    list_steps,
    save_step_data,
    submit_service,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/flows", response_model=ServiceOnboardingFlowOut)
async def create_flow_endpoint(
    payload: ServiceOnboardingFlowCreate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ServiceOnboardingFlowOut:
    flow = await create_flow(db, payload=payload.model_dump())
    return ServiceOnboardingFlowOut.model_validate(flow, from_attributes=True)


@router.post("/steps", response_model=ServiceOnboardingStepOut)
async def create_step_endpoint(
    payload: ServiceOnboardingStepCreate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ServiceOnboardingStepOut:
    step = await create_step(db, payload=payload.model_dump())
    return ServiceOnboardingStepOut.model_validate(step, from_attributes=True)


@router.get("/flows/{service_type_id}", response_model=ServiceOnboardingFlowOut)
async def get_flow_endpoint(service_type_id: int, db: AsyncSession = Depends(get_db)):
    flow = await get_active_flow(db, service_type_id=service_type_id)
    return ServiceOnboardingFlowOut.model_validate(flow, from_attributes=True)


@router.get("/flows/{flow_id}/steps", response_model=list[ServiceOnboardingStepOut])
async def list_steps_endpoint(flow_id: int, db: AsyncSession = Depends(get_db)):
    steps = await list_steps(db, flow_id=flow_id)
    return [ServiceOnboardingStepOut.model_validate(s, from_attributes=True) for s in steps]


@router.post("/services/enable")
async def enable_service_endpoint(
    payload: ProviderServiceEnable, db: AsyncSession = Depends(get_db)
):
    provider_service = await enable_service(
        db, provider_id=payload.provider_id, service_type_id=payload.service_type_id
    )
    return {"provider_service_id": provider_service.provider_service_id, "status": provider_service.status}


@router.get("/services/{provider_service_id}/steps", response_model=list[ProviderServiceStepProgressOut])
async def list_progress_endpoint(provider_service_id: int, db: AsyncSession = Depends(get_db)):
    progress = await list_step_progress(db, provider_service_id=provider_service_id)
    return [ProviderServiceStepProgressOut.model_validate(p, from_attributes=True) for p in progress]


@router.put("/services/{provider_service_id}/steps/{step_id}", response_model=ProviderServiceStepProgressOut)
async def save_step_endpoint(
    provider_service_id: int,
    step_id: int,
    payload: ProviderServiceStepSave,
    db: AsyncSession = Depends(get_db),
) -> ProviderServiceStepProgressOut:
    progress = await save_step_data(
        db,
        provider_service_id=provider_service_id,
        step_id=step_id,
        data_json=payload.data_json,
    )
    return ProviderServiceStepProgressOut.model_validate(progress, from_attributes=True)


@router.post("/services/{provider_service_id}/steps/{step_id}/complete", response_model=ProviderServiceStepProgressOut)
async def complete_step_endpoint(
    provider_service_id: int,
    step_id: int,
    payload: ProviderServiceStepComplete,
    db: AsyncSession = Depends(get_db),
) -> ProviderServiceStepProgressOut:
    progress = await complete_step(
        db,
        provider_service_id=provider_service_id,
        step_id=step_id,
        data_json=payload.data_json,
    )
    return ProviderServiceStepProgressOut.model_validate(progress, from_attributes=True)


@router.post("/services/submit")
async def submit_service_endpoint(
    payload: ProviderServiceSubmit, db: AsyncSession = Depends(get_db)
):
    provider_service = await submit_service(db, provider_service_id=payload.provider_service_id)
    return {"provider_service_id": provider_service.provider_service_id, "status": provider_service.status}


@router.post("/services/{provider_service_id}/admin/status")
async def admin_update_service_status_endpoint(
    provider_service_id: int,
    payload: ProviderServiceStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    provider_service = await admin_update_service_status(
        db,
        provider_service_id=provider_service_id,
        status=payload.status,
        review_note=payload.review_note,
    )
    return {"provider_service_id": provider_service.provider_service_id, "status": provider_service.status}


@router.post("/services/{provider_service_id}/steps/{step_id}/admin/reject", response_model=ProviderServiceStepProgressOut)
async def admin_reject_step_endpoint(
    provider_service_id: int,
    step_id: int,
    payload: ProviderServiceStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ProviderServiceStepProgressOut:
    progress = await admin_reject_step(
        db, provider_service_id=provider_service_id, step_id=step_id, review_note=payload.review_note
    )
    return ProviderServiceStepProgressOut.model_validate(progress, from_attributes=True)


@router.get("/providers/{provider_id}/summary", response_model=ProviderOnboardingSummaryOut)
async def provider_onboarding_summary_endpoint(
    provider_id: int, db: AsyncSession = Depends(get_db)
) -> ProviderOnboardingSummaryOut:
    data = await get_provider_onboarding_summary(db, provider_id=provider_id)
    return ProviderOnboardingSummaryOut(**data)


@router.get("/services/{provider_service_id}/admin/review", response_model=ProviderServiceReviewOut)
async def provider_service_review_endpoint(
    provider_service_id: int,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ProviderServiceReviewOut:
    data = await get_service_review_view(db, provider_service_id=provider_service_id)
    return ProviderServiceReviewOut(**data)
