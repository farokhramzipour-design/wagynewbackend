from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    participant1_user_id: int
    participant2_user_id: int
    booking_id: int | None = None


class ConversationOut(BaseModel):
    conversation_id: int
    participant1_user_id: int
    participant2_user_id: int
    booking_id: int | None = None
    last_message_at: datetime | None = None


class MessageCreate(BaseModel):
    conversation_id: int
    sender_user_id: int
    message_type: str
    body: str | None = None


class MessageOut(BaseModel):
    message_id: int
    conversation_id: int
    sender_user_id: int
    message_type: str
    body: str | None = None
    is_read: bool
    read_at: datetime | None = None
    is_flagged: bool
    flag_reason: str | None = None
    created_at: datetime


class MessageReadUpdate(BaseModel):
    is_read: bool
    read_at: datetime | None = None


class MessageFlagUpdate(BaseModel):
    is_flagged: bool
    flag_reason: str | None = None


class MessageAttachmentCreate(BaseModel):
    message_id: int
    media_id: int
