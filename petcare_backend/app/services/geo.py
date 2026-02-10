from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo import City, Country, Currency, Province
from app.models.payments import PaymentGateway
from app.models.services import ServiceType


async def list_countries(session: AsyncSession) -> list[Country]:
    return (await session.scalars(select(Country))).all()


async def list_provinces(session: AsyncSession, country_code: str | None = None) -> list[Province]:
    query = select(Province)
    if country_code:
        query = query.where(Province.country_code == country_code)
    return (await session.scalars(query)).all()


async def list_cities(session: AsyncSession, province_id: int | None = None) -> list[City]:
    query = select(City)
    if province_id:
        query = query.where(City.province_id == province_id)
    return (await session.scalars(query)).all()


async def list_currencies(session: AsyncSession) -> list[Currency]:
    return (await session.scalars(select(Currency))).all()


async def list_service_types(session: AsyncSession) -> list[ServiceType]:
    return (await session.scalars(select(ServiceType))).all()


async def list_payment_gateways(session: AsyncSession) -> list[PaymentGateway]:
    return (await session.scalars(select(PaymentGateway))).all()
