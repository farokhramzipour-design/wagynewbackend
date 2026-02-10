import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking, BookingEvent
from app.models.charity import CharityCase
from app.models.providers import Provider
from app.models.reviews import Review
from app.models.users import User

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _log_admin_action(action: str, entity: str, entity_id: int, status: str, admin_user_id: int | None):
    logger.info(
        "admin_action",
        extra={
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "status": status,
            "admin_user_id": admin_user_id,
            "timestamp": _utcnow().isoformat(),
        },
    )


async def set_user_status(
    session: AsyncSession, *, user_id: int, status: str, admin_user_id: int | None
) -> User:
    if status not in {"active", "suspended", "deleted"}:
        raise HTTPException(status_code=400, detail="invalid_status")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    user.status = status
    await session.commit()
    await session.refresh(user)

    _log_admin_action("user_status", "users", user_id, status, admin_user_id)
    return user


async def set_provider_status(
    session: AsyncSession, *, provider_id: int, status: str, admin_user_id: int | None
) -> Provider:
    if status not in {"draft", "pending_review", "approved", "rejected", "suspended"}:
        raise HTTPException(status_code=400, detail="invalid_status")

    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    provider.status = status
    await session.commit()
    await session.refresh(provider)

    _log_admin_action("provider_status", "providers", provider_id, status, admin_user_id)
    return provider


async def set_review_status(
    session: AsyncSession, *, review_id: int, status: str, admin_user_id: int | None
) -> Review:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")

    review.moderation_status = status
    await session.commit()
    await session.refresh(review)

    _log_admin_action("review_moderation", "reviews", review_id, status, admin_user_id)
    return review


async def set_charity_status(
    session: AsyncSession, *, charity_case_id: int, status: str, admin_user_id: int | None
) -> CharityCase:
    case = await session.get(CharityCase, charity_case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    case.status = status
    await session.commit()
    await session.refresh(case)

    _log_admin_action("charity_status", "charity_cases", charity_case_id, status, admin_user_id)
    return case


async def mark_booking_disputed(
    session: AsyncSession,
    *,
    booking_id: int,
    actor_user_id: int | None,
    payload_json: dict | None,
) -> Booking:
    async with session.begin():
        booking = await session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="booking_not_found")

        booking.status = "disputed"
        session.add(
            BookingEvent(
                booking_id=booking.booking_id,
                event_type="disputed_admin",
                actor_type="admin",
                actor_user_id=actor_user_id,
                payload_json=payload_json,
                created_at=_utcnow(),
            )
        )

    return booking
