from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.schemas.admin import AdminBookingDispute, AdminStatusUpdate
from app.services.admin import (
    mark_booking_disputed,
    set_charity_status,
    set_provider_status,
    set_review_status,
    set_user_status,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    payload: AdminStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await set_user_status(
        db, user_id=user_id, status=payload.status, admin_user_id=int(admin_user_id) if admin_user_id else None
    )
    return {"user_id": user.user_id, "status": user.status}


@router.post("/providers/{provider_id}/status")
async def update_provider_status(
    provider_id: int,
    payload: AdminStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    provider = await set_provider_status(
        db, provider_id=provider_id, status=payload.status, admin_user_id=int(admin_user_id) if admin_user_id else None
    )
    return {"provider_id": provider.provider_id, "status": provider.status}


@router.post("/reviews/{review_id}/moderation")
async def update_review_status(
    review_id: int,
    payload: AdminStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    review = await set_review_status(
        db, review_id=review_id, status=payload.status, admin_user_id=int(admin_user_id) if admin_user_id else None
    )
    return {"review_id": review.review_id, "moderation_status": review.moderation_status}


@router.post("/charity/{charity_case_id}/status")
async def update_charity_status(
    charity_case_id: int,
    payload: AdminStatusUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    case = await set_charity_status(
        db, charity_case_id=charity_case_id, status=payload.status, admin_user_id=int(admin_user_id) if admin_user_id else None
    )
    return {"charity_case_id": case.charity_case_id, "status": case.status}


@router.post("/bookings/{booking_id}/dispute")
async def admin_dispute_booking(
    booking_id: int,
    payload: AdminBookingDispute,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    booking = await mark_booking_disputed(
        db,
        booking_id=booking_id,
        actor_user_id=int(admin_user_id) if admin_user_id else payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}
