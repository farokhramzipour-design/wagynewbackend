from datetime import datetime

from sqlalchemy import select

from app.models.messaging import Conversation, Message
from app.repositories.base import BaseRepository


class MessagingRepository(BaseRepository):
    async def get_or_create_conversation(self, payload: dict) -> Conversation:
        convo = await self.session.scalar(
            select(Conversation).where(
                Conversation.participant1_user_id == payload["participant1_user_id"],
                Conversation.participant2_user_id == payload["participant2_user_id"],
                Conversation.booking_id == payload.get("booking_id"),
            )
        )
        if convo:
            return convo
        convo = Conversation(**payload)
        self.session.add(convo)
        await self.session.flush()
        return convo

    async def list_messages(
        self, conversation_id: int, limit: int, cursor: dict | None
    ) -> list[Message]:
        query = select(Message).where(Message.conversation_id == conversation_id)
        query = query.order_by(Message.created_at.desc(), Message.message_id.desc())
        if cursor:
            cursor_created_at: datetime = cursor["created_at"]
            cursor_message_id: int = cursor["message_id"]
            query = query.where(
                (Message.created_at < cursor_created_at)
                | (
                    (Message.created_at == cursor_created_at)
                    & (Message.message_id < cursor_message_id)
                )
            )
        return (await self.session.scalars(query.limit(limit))).all()
