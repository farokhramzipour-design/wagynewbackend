from sqlalchemy import select

from app.models.availability import (
    ProviderAvailabilityOverride,
    ProviderAvailabilityRule,
    ProviderTimeOff,
)
from app.repositories.base import BaseRepository


class AvailabilityRepository(BaseRepository):
    async def list_rules(self, provider_id: int) -> list[ProviderAvailabilityRule]:
        return (
            await self.session.scalars(
                select(ProviderAvailabilityRule).where(
                    ProviderAvailabilityRule.provider_id == provider_id
                )
            )
        ).all()

    async def list_overrides(self, provider_id: int) -> list[ProviderAvailabilityOverride]:
        return (
            await self.session.scalars(
                select(ProviderAvailabilityOverride).where(
                    ProviderAvailabilityOverride.provider_id == provider_id
                )
            )
        ).all()

    async def list_time_off(self, provider_id: int) -> list[ProviderTimeOff]:
        return (
            await self.session.scalars(
                select(ProviderTimeOff).where(ProviderTimeOff.provider_id == provider_id)
            )
        ).all()
