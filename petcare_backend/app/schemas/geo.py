from datetime import datetime

from pydantic import BaseModel


class CountryOut(BaseModel):
    country_code: str


class ProvinceOut(BaseModel):
    province_id: int
    country_code: str
    code: str


class CityOut(BaseModel):
    city_id: int
    province_id: int
    name_fa: str


class CurrencyOut(BaseModel):
    currency_code: str
    minor_unit: int
    is_active: bool


class ServiceTypeOut(BaseModel):
    service_type_id: int
    code: str
    default_unit: str
    is_active: bool
    deactivated_at: datetime | None = None


class PaymentGatewayOut(BaseModel):
    gateway_id: int
    code: str
    name: str | None = None
    is_active: bool
