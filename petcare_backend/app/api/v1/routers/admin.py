from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.schemas.admin import AdminBookingDispute, AdminStatusUpdate
from app.schemas.charity import CharityDonationOut
from app.schemas.messaging import MessageFlagUpdate, MessageOut
from app.schemas.payments import PaymentOut
from app.schemas.reviews import ReviewOut, ReviewVisibilityUpdate
from app.services.admin import (
    mark_booking_disputed,
    set_charity_status,
    set_provider_status,
    set_review_status,
    set_user_status,
)
from app.services.charity import list_case_donations, list_case_payments
from app.services.messaging import list_flagged_messages, resolve_flagged_message
from app.services.reviews import update_review_visibility

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


@router.post("/reviews/{review_id}/visibility", response_model=ReviewOut)
async def update_review_visibility_admin(
    review_id: int,
    payload: ReviewVisibilityUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ReviewOut:
    async with db.begin():
        review = await update_review_visibility(db, review_id=review_id, is_public=payload.is_public)
    return ReviewOut.model_validate(review, from_attributes=True)


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


@router.get("/messages/flagged", response_model=list[MessageOut])
async def list_flagged_messages_endpoint(
    limit: int = 200,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[MessageOut]:
    messages = await list_flagged_messages(db, limit=limit)
    return [MessageOut.model_validate(m, from_attributes=True) for m in messages]


@router.post("/messages/{message_id}/resolve", response_model=MessageOut)
async def resolve_message_flag_endpoint(
    message_id: int,
    payload: MessageFlagUpdate,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> MessageOut:
    message = await resolve_flagged_message(
        db, message_id=message_id, is_flagged=payload.is_flagged, flag_reason=payload.flag_reason
    )
    return MessageOut.model_validate(message, from_attributes=True)


@router.get("/charity/{case_id}/donations", response_model=list[CharityDonationOut])
async def admin_charity_donations(
    case_id: int,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[CharityDonationOut]:
    donations = await list_case_donations(db, case_id=case_id)
    return [CharityDonationOut.model_validate(d, from_attributes=True) for d in donations]


@router.get("/charity/{case_id}/payments", response_model=list[PaymentOut])
async def admin_charity_payments(
    case_id: int,
    admin_user_id: str | None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[PaymentOut]:
    payments = await list_case_payments(db, case_id=case_id)
    return [PaymentOut.model_validate(p, from_attributes=True) for p in payments]
