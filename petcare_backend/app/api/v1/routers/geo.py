from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.geo import CityOut, CountryOut, CurrencyOut, PaymentGatewayOut, ProvinceOut, ServiceTypeOut
from app.services.geo import (
    list_cities,
    list_countries,
    list_currencies,
    list_payment_gateways,
    list_provinces,
    list_service_types,
)

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/countries", response_model=list[CountryOut])
async def countries(db: AsyncSession = Depends(get_db)):
    records = await list_countries(db)
    return [CountryOut.model_validate(r, from_attributes=True) for r in records]


@router.get("/provinces", response_model=list[ProvinceOut])
async def provinces(country_code: str | None = None, db: AsyncSession = Depends(get_db)):
    records = await list_provinces(db, country_code=country_code)
    return [ProvinceOut.model_validate(r, from_attributes=True) for r in records]


@router.get("/cities", response_model=list[CityOut])
async def cities(province_id: int | None = None, db: AsyncSession = Depends(get_db)):
    records = await list_cities(db, province_id=province_id)
    return [CityOut.model_validate(r, from_attributes=True) for r in records]


@router.get("/currencies", response_model=list[CurrencyOut])
async def currencies(db: AsyncSession = Depends(get_db)):
    records = await list_currencies(db)
    return [CurrencyOut.model_validate(r, from_attributes=True) for r in records]


@router.get("/service-types", response_model=list[ServiceTypeOut])
async def service_types(db: AsyncSession = Depends(get_db)):
    records = await list_service_types(db)
    return [ServiceTypeOut.model_validate(r, from_attributes=True) for r in records]


@router.get("/payment-gateways", response_model=list[PaymentGatewayOut])
async def payment_gateways(db: AsyncSession = Depends(get_db)):
    records = await list_payment_gateways(db)
    return [PaymentGatewayOut.model_validate(r, from_attributes=True) for r in records]
