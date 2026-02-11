from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import (
    Booking,
    BookingCancellation,
    BookingEvent,
    BookingPet,
    BookingPricing,
)
from app.core.config import settings
from app.models.pets import Pet
from app.models.providers import ProviderService
from app.services.payments import create_payment_for_booking_confirm


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _add_event(
    *,
    session: AsyncSession,
    booking_id: int,
    event_type: str,
    actor_type: str,
    actor_user_id: int | None,
    payload_json: dict | None,
) -> None:
    session.add(
        BookingEvent(
            booking_id=booking_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
            created_at=_utcnow(),
        )
    )


def _require_transition(current: str, expected: set[str]) -> None:
    if current not in expected:
        raise HTTPException(status_code=400, detail="invalid_status_transition")


async def request_booking(session: AsyncSession, *, payload: dict) -> Booking:
    pets = payload.pop("pets")
    start_dt = payload["start_datetime"]
    end_dt = payload["end_datetime"]
    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="invalid_time_range")

    async with session.begin():
        # validate pets belong to owner
        pet_ids = [p["pet_id"] for p in pets]
        owned_pets = (
            await session.scalars(
                select(Pet.pet_id).where(
                    Pet.pet_id.in_(pet_ids),
                    Pet.owner_user_id == payload["owner_user_id"],
                )
            )
        ).all()
        if len(owned_pets) != len(set(pet_ids)):
            raise HTTPException(status_code=400, detail="pet_owner_mismatch")

        provider_service = await session.scalar(
            select(ProviderService).where(
                ProviderService.provider_id == payload["provider_id"],
                ProviderService.service_type_id == payload["service_type_id"],
                ProviderService.is_active.is_(True),
            )
        )
        if not provider_service:
            raise HTTPException(status_code=404, detail="provider_service_not_found")
        if provider_service.max_pets is not None and len(pets) > provider_service.max_pets:
            raise HTTPException(status_code=400, detail="max_pets_exceeded")

        booking = Booking(
            **payload,
            status="requested",
            requested_at=_utcnow(),
        )
        session.add(booking)
        await session.flush()

        for pet in pets:
            session.add(
                BookingPet(
                    booking_id=booking.booking_id,
                    pet_id=pet["pet_id"],
                    per_pet_notes=pet.get("per_pet_notes"),
                )
            )

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="requested",
            actor_type="owner",
            actor_user_id=payload["owner_user_id"],
            payload_json=None,
        )

    await session.refresh(booking)
    return booking


async def accept_booking(
    session: AsyncSession, *, booking_id: int, actor_type: str, actor_user_id: int | None, payload_json: dict | None
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"requested"})
        booking.status = "accepted"
        booking.accepted_at = _utcnow()

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="accepted",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def decline_booking(
    session: AsyncSession, *, booking_id: int, actor_type: str, actor_user_id: int | None, payload_json: dict | None
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"requested"})
        booking.status = "declined"

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="declined",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def confirm_booking(
    session: AsyncSession,
    *,
    booking_id: int,
    actor_type: str,
    actor_user_id: int | None,
    payload_json: dict | None,
    pricing: dict,
    payment_kind: str | None = None,
    gateway_id: int | None = None,
    gateway_transaction_id: str | None = None,
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"accepted"})
        booking.status = "confirmed"
        booking.confirmed_at = _utcnow()

        existing_pricing = await session.get(BookingPricing, booking.booking_id)
        if existing_pricing:
            raise HTTPException(status_code=409, detail="pricing_already_set")

        session.add(
            BookingPricing(
                booking_id=booking.booking_id,
                currency_code=pricing["currency_code"],
                subtotal_minor=pricing["subtotal_minor"],
                owner_fee_minor=pricing["owner_fee_minor"],
                provider_fee_minor=pricing["provider_fee_minor"],
                total_charge_minor=pricing["total_charge_minor"],
                provider_payout_minor=pricing["provider_payout_minor"],
                breakdown_json=pricing["breakdown_json"],
            )
        )

        if payment_kind:
            await create_payment_for_booking_confirm(
                session,
                booking_id=booking.booking_id,
                kind=payment_kind,
                gateway_id=gateway_id,
                gateway_transaction_id=gateway_transaction_id,
                raw_response_json=None,
            )

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="confirmed",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def start_booking(
    session: AsyncSession, *, booking_id: int, actor_type: str, actor_user_id: int | None, payload_json: dict | None
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"confirmed"})
        booking.status = "started"
        booking.started_at = _utcnow()

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="started",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def complete_booking(
    session: AsyncSession, *, booking_id: int, actor_type: str, actor_user_id: int | None, payload_json: dict | None
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"started"})
        booking.status = "completed"
        booking.completed_at = _utcnow()

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="completed",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def cancel_booking(
    session: AsyncSession,
    *,
    booking_id: int,
    actor_type: str,
    actor_user_id: int | None,
    cancelled_by: str,
    reason: str | None,
    policy_snapshot_json: dict | None,
    refund_minor: int | None,
    payload_json: dict | None,
) -> tuple[Booking, BookingCancellation]:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(
            booking.status, {"requested", "accepted", "confirmed", "started"}
        )
        booking.status = "cancelled"
        booking.cancelled_at = _utcnow()

        cancellation = BookingCancellation(
            booking_id=booking.booking_id,
            cancelled_by=cancelled_by,
            reason=reason,
            policy_snapshot_json=policy_snapshot_json,
            refund_minor=refund_minor,
            created_at=_utcnow(),
        )
        session.add(cancellation)

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="cancelled",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    await session.refresh(cancellation)
    return booking, cancellation


async def dispute_booking(
    session: AsyncSession, *, booking_id: int, actor_type: str, actor_user_id: int | None, payload_json: dict | None
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        _require_transition(booking.status, {"completed", "cancelled"})
        if booking.status == "completed" and booking.completed_at is not None:
            delta = _utcnow() - booking.completed_at
            if delta.total_seconds() > settings.dispute_window_hours * 3600:
                raise HTTPException(status_code=400, detail="dispute_window_closed")
        booking.status = "disputed"

        _add_event(
            session=session,
            booking_id=booking.booking_id,
            event_type="disputed",
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload_json,
        )

    await session.refresh(booking)
    return booking


async def list_booking_events(session: AsyncSession, *, booking_id: int) -> list[BookingEvent]:
    return (
        await session.scalars(
            select(BookingEvent)
            .where(BookingEvent.booking_id == booking_id)
            .order_by(BookingEvent.created_at.asc(), BookingEvent.event_id.asc())
        )
    ).all()
