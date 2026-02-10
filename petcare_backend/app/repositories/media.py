from app.models.media import Media
from app.repositories.base import BaseRepository


class MediaRepository(BaseRepository):
    async def create(self, payload: dict) -> Media:
        media = Media(**payload)
        self.session.add(media)
        await self.session.flush()
        return media

    async def get_by_id(self, media_id: int) -> Media | None:
        return await self.session.get(Media, media_id)
