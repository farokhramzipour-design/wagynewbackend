from sqlalchemy import select

from app.models.geo import City, Country, Currency, Province
from app.models.payments import PaymentGateway
from app.models.services import ServiceType
from app.repositories.base import BaseRepository


class GeoRepository(BaseRepository):
    async def list_countries(self) -> list[Country]:
        return (await self.session.scalars(select(Country))).all()

    async def list_provinces(self, country_code: str | None = None) -> list[Province]:
        query = select(Province)
        if country_code:
            query = query.where(Province.country_code == country_code)
        return (await self.session.scalars(query)).all()

    async def list_cities(self, province_id: int | None = None) -> list[City]:
        query = select(City)
        if province_id:
            query = query.where(City.province_id == province_id)
        return (await self.session.scalars(query)).all()


class ReferenceRepository(BaseRepository):
    async def list_currencies(self) -> list[Currency]:
        return (await self.session.scalars(select(Currency))).all()

    async def list_service_types(self) -> list[ServiceType]:
        return (await self.session.scalars(select(ServiceType))).all()

    async def list_payment_gateways(self) -> list[PaymentGateway]:
        return (await self.session.scalars(select(PaymentGateway))).all()
