from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media


def _build_upload_url(storage_key: str) -> str:
    return f"s3://uploads/{storage_key}"


async def create_upload_url(session: AsyncSession, *, payload: dict) -> tuple[Media, str]:
    media = Media(**payload)
    session.add(media)
    await session.commit()
    await session.refresh(media)
    return media, _build_upload_url(media.storage_key)
