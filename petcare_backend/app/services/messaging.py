from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.models.media import Media
from app.models.messaging import Conversation, Message, MessageAttachment


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


async def create_conversation(
    session: AsyncSession, *, participant1_user_id: int, participant2_user_id: int, booking_id: int | None
) -> Conversation:
    existing = await session.scalar(
        select(Conversation).where(
            Conversation.participant1_user_id == participant1_user_id,
            Conversation.participant2_user_id == participant2_user_id,
            Conversation.booking_id == booking_id,
        )
    )
    if existing:
        return existing

    conversation = Conversation(
        participant1_user_id=participant1_user_id,
        participant2_user_id=participant2_user_id,
        booking_id=booking_id,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def get_conversation(session: AsyncSession, *, conversation_id: int) -> Conversation:
    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation_not_found")
    return conversation


async def list_conversations(session: AsyncSession, *, user_id: int) -> list[Conversation]:
    query = select(Conversation).where(
        or_(
            Conversation.participant1_user_id == user_id,
            Conversation.participant2_user_id == user_id,
        )
    )
    query = query.order_by(Conversation.last_message_at.desc().nullslast())
    return (await session.scalars(query)).all()


async def send_message(
    session: AsyncSession,
    *,
    conversation_id: int,
    sender_user_id: int,
    message_type: str,
    body: str | None,
) -> Message:
    key = f"msg:rate:{sender_user_id}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, 60)
    if current > settings.message_rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="message_rate_limited")

    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation_not_found")

    message = Message(
        conversation_id=conversation_id,
        sender_user_id=sender_user_id,
        message_type=message_type,
        body=body,
        is_read=False,
        is_flagged=False,
    )
    session.add(message)
    conversation.last_message_at = _utcnow()
    await session.commit()
    await session.refresh(message)
    return message


async def list_messages(
    session: AsyncSession,
    *,
    conversation_id: int,
    limit: int,
    cursor_created_at: datetime | None,
    cursor_message_id: int | None,
):
    query = select(Message).where(Message.conversation_id == conversation_id)
    query = query.order_by(Message.created_at.desc(), Message.message_id.desc())

    if cursor_created_at and cursor_message_id:
        query = query.where(
            (Message.created_at < cursor_created_at)
            | (
                (Message.created_at == cursor_created_at)
                & (Message.message_id < cursor_message_id)
            )
        )

    messages = (await session.scalars(query.limit(limit))).all()
    return messages


async def mark_message_read(
    session: AsyncSession, *, message_id: int, is_read: bool, read_at: datetime | None
) -> Message:
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="message_not_found")

    message.is_read = is_read
    message.read_at = read_at if is_read else None
    await session.commit()
    await session.refresh(message)
    return message


async def flag_message(
    session: AsyncSession, *, message_id: int, is_flagged: bool, flag_reason: str | None
) -> Message:
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="message_not_found")

    message.is_flagged = is_flagged
    message.flag_reason = flag_reason if is_flagged else None
    await session.commit()
    await session.refresh(message)
    return message


async def attach_media(
    session: AsyncSession, *, message_id: int, media_id: int
) -> MessageAttachment:
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="message_not_found")

    media = await session.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="media_not_found")

    existing = await session.scalar(
        select(MessageAttachment).where(
            MessageAttachment.message_id == message_id,
            MessageAttachment.media_id == media_id,
        )
    )
    if existing:
        return existing

    attachment = MessageAttachment(message_id=message_id, media_id=media_id)
    session.add(attachment)
    await session.commit()
    await session.refresh(attachment)
    return attachment


async def list_flagged_messages(session: AsyncSession, *, limit: int = 200) -> list[Message]:
    return (
        await session.scalars(
            select(Message)
            .where(Message.is_flagged.is_(True))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
    ).all()


async def resolve_flagged_message(
    session: AsyncSession, *, message_id: int, is_flagged: bool, flag_reason: str | None
) -> Message:
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="message_not_found")

    message.is_flagged = is_flagged
    message.flag_reason = flag_reason if is_flagged else None
    await session.commit()
    await session.refresh(message)
    return message
