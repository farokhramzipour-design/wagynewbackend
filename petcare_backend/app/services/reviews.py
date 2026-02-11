from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking
from app.models.providers import Provider
from app.models.reviews import Review, ReviewMedia


def _validate_rating(rating: int) -> None:
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="invalid_rating")


async def create_review(session: AsyncSession, *, payload: dict) -> Review:
    _validate_rating(payload["rating"])

    booking = await session.get(Booking, payload["booking_id"])
    if not booking:
        raise HTTPException(status_code=404, detail="booking_not_found")

    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="booking_not_completed")

    if payload["reviewer_user_id"] not in {booking.owner_user_id}:
        # Allow provider user to review if policy extends; current default owner-only
        provider = await session.get(Provider, booking.provider_id)
        if not provider or payload["reviewer_user_id"] != provider.user_id:
            raise HTTPException(status_code=403, detail="reviewer_not_allowed")

    if payload["reviewee_user_id"] == payload["reviewer_user_id"]:
        raise HTTPException(status_code=400, detail="reviewee_invalid")

    existing = await session.scalar(select(Review).where(Review.booking_id == booking.booking_id))
    if existing:
        return existing

    review = Review(
        booking_id=payload["booking_id"],
        reviewer_user_id=payload["reviewer_user_id"],
        reviewee_user_id=payload["reviewee_user_id"],
        rating=payload["rating"],
        review_text=payload.get("review_text"),
        moderation_status="pending",
        response_text=None,
        is_public=payload.get("is_public", True),
        helpful_count=0,
    )
    session.add(review)
    await session.flush()

    await _update_provider_metrics(session, booking.provider_id)
    return review


async def moderate_review(session: AsyncSession, *, review_id: int, moderation_status: str) -> Review:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")

    review.moderation_status = moderation_status
    await session.flush()
    return review


async def respond_to_review(session: AsyncSession, *, review_id: int, response_text: str | None) -> Review:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")

    review.response_text = response_text
    await session.flush()
    return review


async def update_review_visibility(
    session: AsyncSession, *, review_id: int, is_public: bool
) -> Review:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")

    review.is_public = is_public
    await session.flush()
    return review


async def add_review_media(session: AsyncSession, *, review_id: int, media_id: int) -> ReviewMedia:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")

    record = ReviewMedia(review_id=review_id, media_id=media_id)
    session.add(record)
    await session.flush()
    return record


async def list_review_media(session: AsyncSession, *, review_id: int) -> list[ReviewMedia]:
    return (
        await session.scalars(
            select(ReviewMedia).where(ReviewMedia.review_id == review_id)
        )
    ).all()


async def get_review(session: AsyncSession, *, review_id: int) -> Review:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="review_not_found")
    return review


async def list_reviews(
    session: AsyncSession, *, provider_id: int, service_type_id: int | None
) -> list[Review]:
    query = (
        select(Review)
        .join(Booking, Booking.booking_id == Review.booking_id)
        .where(Booking.provider_id == provider_id)
    )
    if service_type_id is not None:
        query = query.where(Booking.service_type_id == service_type_id)
    return (await session.scalars(query.order_by(Review.created_at.desc()))).all()


async def _update_provider_metrics(session: AsyncSession, provider_id: int) -> None:
    provider = await session.get(Provider, provider_id)
    if not provider:
        return

    avg_rating = await session.scalar(
        select(func.avg(Review.rating))
        .join(Booking, Booking.booking_id == Review.booking_id)
        .where(Booking.provider_id == provider_id)
    )
    total_completed = await session.scalar(
        select(func.count(Booking.booking_id)).where(
            Booking.provider_id == provider_id, Booking.status == "completed"
        )
    )
    repeat_clients = await session.scalar(
        select(func.count(func.distinct(Booking.owner_user_id)))
        .where(Booking.provider_id == provider_id, Booking.status == "completed")
    )

    provider.average_rating = avg_rating
    provider.total_completed_bookings = total_completed
    provider.repeat_clients_count = repeat_clients
