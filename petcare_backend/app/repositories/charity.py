from sqlalchemy import select

from app.models.charity import CharityCase, CharityDonation
from app.repositories.base import BaseRepository


class CharityRepository(BaseRepository):
    async def get_case_for_update(self, charity_case_id: int) -> CharityCase | None:
        return await self.session.scalar(
            select(CharityCase)
            .where(CharityCase.charity_case_id == charity_case_id)
            .with_for_update()
        )

    async def create_donation(self, payload: dict) -> CharityDonation:
        donation = CharityDonation(**payload)
        self.session.add(donation)
        await self.session.flush()
        return donation
