from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class MeOut(BaseModel):
    user_id: int
    phone_e164: str
    email: EmailStr | None = None
    status: str
    locale: str
    timezone: str
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class MeUpdate(BaseModel):
    email: EmailStr | None = None
    locale: str | None = None
    timezone: str | None = None


class UserProfileOut(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    avatar_media_id: int | None = None
    bio: str | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    avatar_media_id: int | None = None
    bio: str | None = None


class AddressCreate(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    is_default: bool


class AddressUpdate(BaseModel):
    country_code: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    is_default: bool | None = None


class AddressOut(BaseModel):
    address_id: int
    user_id: int
    country_code: str
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    is_default: bool
    created_at: datetime
    updated_at: datetime | None = None
