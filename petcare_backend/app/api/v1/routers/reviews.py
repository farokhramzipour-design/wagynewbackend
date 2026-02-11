from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.reviews import (
    ReviewCreate,
    ReviewMediaCreate,
    ReviewMediaOut,
    ReviewModerate,
    ReviewOut,
    ReviewResponse,
    ReviewVisibilityUpdate,
)
from app.services.reviews import (
    add_review_media,
    create_review,
    get_review,
    list_reviews,
    list_review_media,
    moderate_review,
    respond_to_review,
    update_review_visibility,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut)
async def create_review_endpoint(
    payload: ReviewCreate, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    async with db.begin():
        review = await create_review(db, payload=payload.model_dump())
    return ReviewOut.model_validate(review, from_attributes=True)


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review_endpoint(review_id: int, db: AsyncSession = Depends(get_db)) -> ReviewOut:
    review = await get_review(db, review_id=review_id)
    return ReviewOut.model_validate(review, from_attributes=True)


@router.get("/", response_model=list[ReviewOut])
async def list_reviews_endpoint(
    provider_id: int, service_type_id: int | None = None, db: AsyncSession = Depends(get_db)
) -> list[ReviewOut]:
    reviews = await list_reviews(db, provider_id=provider_id, service_type_id=service_type_id)
    return [ReviewOut.model_validate(r, from_attributes=True) for r in reviews]


@router.post("/{review_id}/moderate", response_model=ReviewOut)
async def moderate_review_endpoint(
    review_id: int, payload: ReviewModerate, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    async with db.begin():
        review = await moderate_review(
            db, review_id=review_id, moderation_status=payload.moderation_status
        )
    return ReviewOut.model_validate(review, from_attributes=True)


@router.post("/{review_id}/response", response_model=ReviewOut)
async def respond_review_endpoint(
    review_id: int, payload: ReviewResponse, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    async with db.begin():
        review = await respond_to_review(
            db, review_id=review_id, response_text=payload.response_text
    )
    return ReviewOut.model_validate(review, from_attributes=True)


@router.post("/{review_id}/visibility", response_model=ReviewOut)
async def update_review_visibility_endpoint(
    review_id: int, payload: ReviewVisibilityUpdate, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    async with db.begin():
        review = await update_review_visibility(db, review_id=review_id, is_public=payload.is_public)
    return ReviewOut.model_validate(review, from_attributes=True)


@router.post("/{review_id}/media", response_model=ReviewMediaOut)
async def add_review_media_endpoint(
    review_id: int, payload: ReviewMediaCreate, db: AsyncSession = Depends(get_db)
) -> ReviewMediaOut:
    async with db.begin():
        record = await add_review_media(db, review_id=review_id, media_id=payload.media_id)
    return ReviewMediaOut.model_validate(record, from_attributes=True)


@router.get("/{review_id}/media", response_model=list[ReviewMediaOut])
async def list_review_media_endpoint(review_id: int, db: AsyncSession = Depends(get_db)):
    records = await list_review_media(db, review_id=review_id)
    return [ReviewMediaOut.model_validate(r, from_attributes=True) for r in records]
