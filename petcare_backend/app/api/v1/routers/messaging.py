from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.messaging import (
    ConversationCreate,
    ConversationOut,
    MessageAttachmentCreate,
    MessageCreate,
    MessageFlagUpdate,
    MessageOut,
    MessageReadUpdate,
)
from app.services.messaging import (
    attach_media,
    create_conversation,
    flag_message,
    get_conversation,
    list_conversations,
    list_messages,
    mark_message_read,
    send_message,
)

router = APIRouter(prefix="/messages", tags=["messaging"])


@router.post("/conversations", response_model=ConversationOut)
async def create_conversation_endpoint(
    payload: ConversationCreate, db: AsyncSession = Depends(get_db)
) -> ConversationOut:
    convo = await create_conversation(
        db,
        participant1_user_id=payload.participant1_user_id,
        participant2_user_id=payload.participant2_user_id,
        booking_id=payload.booking_id,
    )
    return ConversationOut.model_validate(convo, from_attributes=True)


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
async def get_conversation_endpoint(
    conversation_id: int, db: AsyncSession = Depends(get_db)
) -> ConversationOut:
    convo = await get_conversation(db, conversation_id=conversation_id)
    return ConversationOut.model_validate(convo, from_attributes=True)


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations_endpoint(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> list[ConversationOut]:
    conversations = await list_conversations(db, user_id=user_id)
    return [ConversationOut.model_validate(c, from_attributes=True) for c in conversations]


@router.post("/send", response_model=MessageOut)
async def send_message_endpoint(
    payload: MessageCreate, db: AsyncSession = Depends(get_db)
) -> MessageOut:
    message = await send_message(
        db,
        conversation_id=payload.conversation_id,
        sender_user_id=payload.sender_user_id,
        message_type=payload.message_type,
        body=payload.body,
    )
    return MessageOut.model_validate(message, from_attributes=True)


@router.get("/list", response_model=list[MessageOut])
async def list_messages_endpoint(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200),
    cursor_created_at: str | None = None,
    cursor_message_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    parsed_cursor: datetime | None = None
    if cursor_created_at:
        parsed_cursor = datetime.fromisoformat(cursor_created_at)

    messages = await list_messages(
        db,
        conversation_id=conversation_id,
        limit=limit,
        cursor_created_at=parsed_cursor,
        cursor_message_id=cursor_message_id,
    )
    return [MessageOut.model_validate(m, from_attributes=True) for m in messages]


@router.patch("/messages/{message_id}/read", response_model=MessageOut)
async def mark_read_endpoint(
    message_id: int, payload: MessageReadUpdate, db: AsyncSession = Depends(get_db)
) -> MessageOut:
    message = await mark_message_read(
        db,
        message_id=message_id,
        is_read=payload.is_read,
        read_at=payload.read_at,
    )
    return MessageOut.model_validate(message, from_attributes=True)


@router.patch("/messages/{message_id}/flag", response_model=MessageOut)
async def flag_message_endpoint(
    message_id: int, payload: MessageFlagUpdate, db: AsyncSession = Depends(get_db)
) -> MessageOut:
    message = await flag_message(
        db,
        message_id=message_id,
        is_flagged=payload.is_flagged,
        flag_reason=payload.flag_reason,
    )
    return MessageOut.model_validate(message, from_attributes=True)


@router.post("/attachments")
async def attach_media_endpoint(
    payload: MessageAttachmentCreate, db: AsyncSession = Depends(get_db)
):
    attachment = await attach_media(
        db, message_id=payload.message_id, media_id=payload.media_id
    )
    return {"message_attachment_id": attachment.message_attachment_id}
