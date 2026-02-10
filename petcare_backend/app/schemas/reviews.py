from pydantic import BaseModel


class ReviewCreate(BaseModel):
    booking_id: int
    reviewer_user_id: int
    reviewee_user_id: int
    rating: int
    review_text: str | None = None


class ReviewModerate(BaseModel):
    moderation_status: str


class ReviewResponse(BaseModel):
    response_text: str | None = None


class ReviewOut(BaseModel):
    review_id: int
    booking_id: int
    reviewer_user_id: int
    reviewee_user_id: int
    rating: int
    review_text: str | None = None
    moderation_status: str
    response_text: str | None = None
    helpful_count: int


class ReviewMediaCreate(BaseModel):
    media_id: int


class ReviewMediaOut(BaseModel):
    review_media_id: int
    review_id: int
    media_id: int
