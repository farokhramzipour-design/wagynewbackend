from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.media import MediaCreate, MediaUploadOut, MediaOut
from app.services.media import create_upload_url

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload-url", response_model=MediaUploadOut)
async def upload_url(payload: MediaCreate, db: AsyncSession = Depends(get_db)) -> MediaUploadOut:
    media, upload_url = await create_upload_url(db, payload=payload.model_dump())
    return MediaUploadOut(media=MediaOut.model_validate(media, from_attributes=True), upload_url=upload_url)
