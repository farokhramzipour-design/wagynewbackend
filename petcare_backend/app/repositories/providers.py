from sqlalchemy import select

from app.models.providers import Provider, ProviderService, ProviderServiceRate
from app.repositories.base import BaseRepository


class ProvidersRepository(BaseRepository):
    async def get_by_id(self, provider_id: int) -> Provider | None:
        return await self.session.get(Provider, provider_id)

    async def get_by_user_id(self, user_id: int) -> Provider | None:
        return await self.session.scalar(select(Provider).where(Provider.user_id == user_id))

    async def update_status(self, provider_id: int, status: str) -> Provider:
        provider = await self.session.get(Provider, provider_id)
        if not provider:
            raise ValueError("provider_not_found")
        provider.status = status
        await self.session.flush()
        return provider


class ProviderServicesRepository(BaseRepository):
    async def upsert_service(self, provider_id: int, payload: dict) -> ProviderService:
        service_type_id = payload["service_type_id"]
        provider_service = await self.session.scalar(
            select(ProviderService).where(
                ProviderService.provider_id == provider_id,
                ProviderService.service_type_id == service_type_id,
            )
        )
        if provider_service:
            provider_service.is_active = payload["is_active"]
            provider_service.max_pets = payload.get("max_pets")
        else:
            provider_service = ProviderService(provider_id=provider_id, **payload)
            self.session.add(provider_service)
        await self.session.flush()
        return provider_service

    async def add_rate(self, provider_service_id: int, payload: dict) -> ProviderServiceRate:
        rate = ProviderServiceRate(provider_service_id=provider_service_id, **payload)
        self.session.add(rate)
        await self.session.flush()
        return rate
