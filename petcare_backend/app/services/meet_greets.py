from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import MeetGreet
from app.models.messaging import Conversation, Message
from app.models.providers import Provider


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _require_transition(current: str, allowed: set[str]) -> None:
    if current not in allowed:
        raise HTTPException(status_code=400, detail="invalid_status_transition")


def _message_body(status: str, scheduled_at: datetime) -> str:
    return f"meet_greet:{status} at {scheduled_at.isoformat()}"


async def schedule_meet_greet(session: AsyncSession, *, payload: dict) -> MeetGreet:
    meet = MeetGreet(
        owner_user_id=payload["owner_user_id"],
        provider_id=payload["provider_id"],
        scheduled_at=payload["scheduled_at"],
        status="scheduled",
        location_text=payload.get("location_text"),
        notes=payload.get("notes"),
    )
    session.add(meet)
    await session.commit()
    await session.refresh(meet)
    return meet


async def reschedule_meet_greet(
    session: AsyncSession, *, meet_greet_id: int, payload: dict
) -> MeetGreet:
    meet = await session.get(MeetGreet, meet_greet_id)
    if not meet:
        raise HTTPException(status_code=404, detail="meet_greet_not_found")

    _require_transition(meet.status, {"scheduled", "rescheduled"})
    meet.status = "rescheduled"
    meet.scheduled_at = payload["scheduled_at"]
    meet.location_text = payload.get("location_text")
    meet.notes = payload.get("notes")

    await session.commit()
    await session.refresh(meet)
    return meet


async def update_meet_greet_status(
    session: AsyncSession, *, meet_greet_id: int, status: str
) -> MeetGreet:
    meet = await session.get(MeetGreet, meet_greet_id)
    if not meet:
        raise HTTPException(status_code=404, detail="meet_greet_not_found")

    if status == "cancelled":
        _require_transition(meet.status, {"scheduled", "rescheduled"})
    elif status in {"completed", "no_show"}:
        _require_transition(meet.status, {"scheduled", "rescheduled"})
    else:
        raise HTTPException(status_code=400, detail="invalid_status")

    meet.status = status
    await session.commit()
    await session.refresh(meet)
    return meet


async def maybe_send_meet_greet_message(
    session: AsyncSession, *, meet: MeetGreet, status: str
) -> None:
    provider = await session.get(Provider, meet.provider_id)
    if not provider:
        return

    convo = await session.scalar(
        select(Conversation).where(
            Conversation.participant1_user_id == meet.owner_user_id,
            Conversation.participant2_user_id == provider.user_id,
            Conversation.booking_id.is_(None),
        )
    )
    if not convo:
        return

    session.add(
        Message(
            conversation_id=convo.conversation_id,
            sender_user_id=meet.owner_user_id,
            message_type="meet_greet",
            body=_message_body(status, meet.scheduled_at),
            is_read=False,
            is_flagged=False,
        )
    )
    convo.last_message_at = _utcnow()
    await session.commit()
