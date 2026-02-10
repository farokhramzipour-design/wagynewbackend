from sqlalchemy import select

from app.models.reviews import Review
from app.repositories.base import BaseRepository


class ReviewsRepository(BaseRepository):
    async def get_by_booking(self, booking_id: int) -> Review | None:
        return await self.session.scalar(select(Review).where(Review.booking_id == booking_id))

    async def create(self, payload: dict) -> Review:
        review = Review(**payload)
        self.session.add(review)
        await self.session.flush()
        return review
