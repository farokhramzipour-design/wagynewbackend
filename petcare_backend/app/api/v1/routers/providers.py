from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.providers import (
    ProviderDraftCreate,
    ProviderHomeUpsert,
    ProviderOut,
    ProviderProfileUpdate,
    ProviderRateEstimateOut,
    ProviderRateEstimateRequest,
    ProviderServiceRateCreate,
    ProviderServiceUpsert,
    ProviderStatusUpdate,
    ProviderVerificationCreate,
)
from app.services.providers import (
    admin_decide_provider,
    create_provider_draft,
    create_provider_service_rate,
    create_provider_verification,
    estimate_provider_rate,
    submit_provider_review,
    update_provider_profile,
    upsert_provider_home,
    upsert_provider_service,
)

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("/onboard/draft", response_model=ProviderOut)
async def create_draft(payload: ProviderDraftCreate, db: AsyncSession = Depends(get_db)) -> ProviderOut:
    provider = await create_provider_draft(db, user_id=payload.user_id)
    return ProviderOut.model_validate(provider, from_attributes=True)


@router.patch("/{provider_id}/profile", response_model=ProviderOut)
async def update_profile(
    provider_id: int, payload: ProviderProfileUpdate, db: AsyncSession = Depends(get_db)
) -> ProviderOut:
    provider = await update_provider_profile(
        db, provider_id=provider_id, updates=payload.model_dump(exclude_unset=True)
    )
    return ProviderOut.model_validate(provider, from_attributes=True)


@router.put("/{provider_id}/home")
async def upsert_home(
    provider_id: int, payload: ProviderHomeUpsert, db: AsyncSession = Depends(get_db)
):
    home = await upsert_provider_home(
        db, provider_id=provider_id, payload=payload.model_dump(exclude_unset=True)
    )
    return {"provider_id": home.provider_id}


@router.post("/{provider_id}/verifications")
async def add_verification(
    provider_id: int, payload: ProviderVerificationCreate, db: AsyncSession = Depends(get_db)
):
    verification = await create_provider_verification(
        db, provider_id=provider_id, payload=payload.model_dump()
    )
    return {"provider_verification_id": verification.provider_verification_id}


@router.put("/{provider_id}/services")
async def upsert_service(
    provider_id: int, payload: ProviderServiceUpsert, db: AsyncSession = Depends(get_db)
):
    provider_service = await upsert_provider_service(
        db, provider_id=provider_id, payload=payload.model_dump()
    )
    return {"provider_service_id": provider_service.provider_service_id}


@router.post("/services/{provider_service_id}/rates")
async def add_service_rate(
    provider_service_id: int, payload: ProviderServiceRateCreate, db: AsyncSession = Depends(get_db)
):
    rate = await create_provider_service_rate(
        db, provider_service_id=provider_service_id, payload=payload.model_dump()
    )
    return {"rate_id": rate.rate_id}


@router.post("/services/{provider_service_id}/estimate", response_model=ProviderRateEstimateOut)
async def estimate_rate(
    provider_service_id: int,
    payload: ProviderRateEstimateRequest,
    db: AsyncSession = Depends(get_db),
) -> ProviderRateEstimateOut:
    estimate = await estimate_provider_rate(
        db,
        provider_service_id=provider_service_id,
        pets_count=payload.pets_count,
        is_puppy=payload.is_puppy,
        is_holiday=payload.is_holiday,
    )
    return ProviderRateEstimateOut(**estimate)


@router.post("/{provider_id}/submit-review", response_model=ProviderOut)
async def submit_review(provider_id: int, db: AsyncSession = Depends(get_db)) -> ProviderOut:
    provider = await submit_provider_review(db, provider_id=provider_id)
    return ProviderOut.model_validate(provider, from_attributes=True)


@router.post("/{provider_id}/admin/decision", response_model=ProviderOut)
async def admin_decision(
    provider_id: int, payload: ProviderStatusUpdate, db: AsyncSession = Depends(get_db)
) -> ProviderOut:
    provider = await admin_decide_provider(
        db,
        provider_id=provider_id,
        status=payload.status,
        admin_user_id=payload.admin_user_id,
        reason=payload.reason,
    )
    return ProviderOut.model_validate(provider, from_attributes=True)
