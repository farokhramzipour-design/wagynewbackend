from datetime import datetime

from pydantic import BaseModel


class MediaCreate(BaseModel):
    owner_user_id: int | None = None
    media_type: str
    storage_key: str
    url: str
    mime_type: str | None = None
    size_bytes: int | None = None


class MediaOut(BaseModel):
    media_id: int
    owner_user_id: int | None = None
    media_type: str
    storage_key: str
    url: str
    mime_type: str | None = None
    size_bytes: int | None = None
    created_at: datetime


class MediaUploadOut(BaseModel):
    media: MediaOut
    upload_url: str
