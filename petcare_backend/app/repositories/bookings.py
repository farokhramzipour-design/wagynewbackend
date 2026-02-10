from sqlalchemy import select

from app.models.bookings import Booking, BookingEvent
from app.repositories.base import BaseRepository


class BookingsRepository(BaseRepository):
    async def get_by_id_for_update(self, booking_id: int) -> Booking | None:
        return await self.session.scalar(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        )

    async def add_event(
        self, booking_id: int, event_type: str, payload: dict | None, actor_type: str, actor_user_id: int | None
    ) -> BookingEvent:
        event = BookingEvent(
            booking_id=booking_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            payload_json=payload,
        )
        self.session.add(event)
        await self.session.flush()
        return event
