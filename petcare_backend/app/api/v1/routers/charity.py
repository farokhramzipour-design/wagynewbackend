from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.charity import (
    CharityCaseCreate,
    CharityCaseOut,
    CharityCaseUpdate,
    CharityDonationCreate,
    CharityStatusUpdate,
    CharityUpdateCreate,
    CharityUpdateMediaCreate,
    CharityUpdateOut,
)
from app.services.charity import (
    activate_case,
    admin_review_case,
    close_case,
    create_case,
    create_donation,
    create_update,
    create_update_media,
    get_case,
    list_cases,
    list_updates,
    submit_case,
    update_case,
)

router = APIRouter(prefix="/charity", tags=["charity"])


@router.post("/cases", response_model=CharityCaseOut)
async def create_case_endpoint(
    payload: CharityCaseCreate, db: AsyncSession = Depends(get_db)
) -> CharityCaseOut:
    case = await create_case(db, payload=payload.model_dump())
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.patch("/cases/{case_id}", response_model=CharityCaseOut)
async def update_case_endpoint(
    case_id: int, payload: CharityCaseUpdate, db: AsyncSession = Depends(get_db)
) -> CharityCaseOut:
    case = await update_case(db, case_id=case_id, payload=payload.model_dump(exclude_unset=True))
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.post("/cases/{case_id}/submit", response_model=CharityCaseOut)
async def submit_case_endpoint(case_id: int, db: AsyncSession = Depends(get_db)) -> CharityCaseOut:
    case = await submit_case(db, case_id=case_id)
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.post("/cases/{case_id}/admin/review", response_model=CharityCaseOut)
async def admin_review_endpoint(
    case_id: int, payload: CharityStatusUpdate, db: AsyncSession = Depends(get_db)
) -> CharityCaseOut:
    case = await admin_review_case(
        db, case_id=case_id, status=payload.status, admin_user_id=payload.admin_user_id
    )
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.post("/cases/{case_id}/activate", response_model=CharityCaseOut)
async def activate_case_endpoint(case_id: int, db: AsyncSession = Depends(get_db)) -> CharityCaseOut:
    case = await activate_case(db, case_id=case_id)
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.post("/cases/{case_id}/close", response_model=CharityCaseOut)
async def close_case_endpoint(
    case_id: int, payload: CharityStatusUpdate, db: AsyncSession = Depends(get_db)
) -> CharityCaseOut:
    case = await close_case(db, case_id=case_id, status=payload.status)
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.get("/cases", response_model=list[CharityCaseOut])
async def list_cases_endpoint(status: str | None = None, db: AsyncSession = Depends(get_db)):
    cases = await list_cases(db, status=status)
    return [CharityCaseOut.model_validate(c, from_attributes=True) for c in cases]


@router.get("/cases/{case_id}", response_model=CharityCaseOut)
async def get_case_endpoint(case_id: int, db: AsyncSession = Depends(get_db)) -> CharityCaseOut:
    case = await get_case(db, case_id=case_id)
    return CharityCaseOut.model_validate(case, from_attributes=True)


@router.post("/donations")
async def create_donation_endpoint(
    payload: CharityDonationCreate, db: AsyncSession = Depends(get_db)
):
    donation = await create_donation(db, payload=payload.model_dump())
    return {"donation_id": donation.donation_id, "status": donation.status}


@router.post("/updates")
async def create_update_endpoint(payload: CharityUpdateCreate, db: AsyncSession = Depends(get_db)):
    update_record = await create_update(db, payload=payload.model_dump())
    return {"charity_update_id": update_record.charity_update_id}


@router.get("/cases/{case_id}/updates", response_model=list[CharityUpdateOut])
async def list_updates_endpoint(case_id: int, db: AsyncSession = Depends(get_db)):
    records = await list_updates(db, case_id=case_id)
    return [CharityUpdateOut.model_validate(r, from_attributes=True) for r in records]


@router.post("/updates/media")
async def create_update_media_endpoint(
    payload: CharityUpdateMediaCreate, db: AsyncSession = Depends(get_db)
):
    media = await create_update_media(db, payload=payload.model_dump())
    return {"charity_update_media_id": media.charity_update_media_id}
