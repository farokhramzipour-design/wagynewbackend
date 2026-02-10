from sqlalchemy import select

from app.models.users import Favorite, SearchHistory
from app.repositories.base import BaseRepository


class SearchRepository(BaseRepository):
    async def write_history(self, payload: dict) -> SearchHistory:
        record = SearchHistory(**payload)
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_favorites(self, user_id: int) -> list[Favorite]:
        return (
            await self.session.scalars(select(Favorite).where(Favorite.user_id == user_id))
        ).all()
