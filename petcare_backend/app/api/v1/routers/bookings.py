from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.bookings import (
    BookingAction,
    BookingCancelRequest,
    BookingConfirmRequest,
    BookingRequestCreate,
    BookingEventOut,
)
from app.services.bookings import (
    accept_booking,
    cancel_booking,
    complete_booking,
    confirm_booking,
    decline_booking,
    dispute_booking,
    list_booking_events,
    request_booking,
    start_booking,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/request")
async def request_booking_endpoint(
    payload: BookingRequestCreate, db: AsyncSession = Depends(get_db)
):
    booking = await request_booking(db, payload=payload.model_dump())
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/accept")
async def accept_booking_endpoint(
    booking_id: int, payload: BookingAction, db: AsyncSession = Depends(get_db)
):
    booking = await accept_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/decline")
async def decline_booking_endpoint(
    booking_id: int, payload: BookingAction, db: AsyncSession = Depends(get_db)
):
    booking = await decline_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/confirm")
async def confirm_booking_endpoint(
    booking_id: int, payload: BookingConfirmRequest, db: AsyncSession = Depends(get_db)
):
    booking = await confirm_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
        payment_kind=payload.payment_kind,
        gateway_id=payload.gateway_id,
        gateway_transaction_id=payload.gateway_transaction_id,
        pricing={
            "currency_code": payload.currency_code,
            "subtotal_minor": payload.subtotal_minor,
            "owner_fee_minor": payload.owner_fee_minor,
            "provider_fee_minor": payload.provider_fee_minor,
            "total_charge_minor": payload.total_charge_minor,
            "provider_payout_minor": payload.provider_payout_minor,
            "breakdown_json": payload.breakdown_json,
        },
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/start")
async def start_booking_endpoint(
    booking_id: int, payload: BookingAction, db: AsyncSession = Depends(get_db)
):
    booking = await start_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/complete")
async def complete_booking_endpoint(
    booking_id: int, payload: BookingAction, db: AsyncSession = Depends(get_db)
):
    booking = await complete_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/cancel")
async def cancel_booking_endpoint(
    booking_id: int, payload: BookingCancelRequest, db: AsyncSession = Depends(get_db)
):
    booking = await cancel_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        cancelled_by=payload.cancelled_by,
        reason=payload.reason,
        policy_snapshot_json=payload.policy_snapshot_json,
        refund_minor=payload.refund_minor,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.post("/{booking_id}/dispute")
async def dispute_booking_endpoint(
    booking_id: int, payload: BookingAction, db: AsyncSession = Depends(get_db)
):
    booking = await dispute_booking(
        db,
        booking_id=booking_id,
        actor_type=payload.actor_type,
        actor_user_id=payload.actor_user_id,
        payload_json=payload.payload_json,
    )
    return {"booking_id": booking.booking_id, "status": booking.status}


@router.get("/{booking_id}/events", response_model=list[BookingEventOut])
async def booking_events_endpoint(booking_id: int, db: AsyncSession = Depends(get_db)):
    events = await list_booking_events(db, booking_id=booking_id)
    return [BookingEventOut.model_validate(e, from_attributes=True) for e in events]
