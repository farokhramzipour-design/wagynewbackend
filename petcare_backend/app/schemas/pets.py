from datetime import date, datetime

from pydantic import BaseModel


class PetCreate(BaseModel):
    owner_user_id: int
    name: str
    pet_type: str
    size: str
    gender: str
    weight_kg: float | None = None
    date_of_birth: date | None = None
    primary_photo_media_id: int | None = None
    is_active: bool


class PetUpdate(BaseModel):
    name: str | None = None
    pet_type: str | None = None
    size: str | None = None
    gender: str | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None
    primary_photo_media_id: int | None = None
    is_active: bool | None = None


class PetOut(BaseModel):
    pet_id: int
    owner_user_id: int
    name: str
    pet_type: str
    size: str
    gender: str
    weight_kg: float | None = None
    date_of_birth: date | None = None
    primary_photo_media_id: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class PetVaccinationCreate(BaseModel):
    vaccine_type: str
    vaccination_date: date
    expiry_date: date | None = None
    document_media_id: int | None = None
    verified: bool


class PetVaccinationOut(BaseModel):
    vaccination_id: int
    pet_id: int
    vaccine_type: str
    vaccination_date: date
    expiry_date: date | None = None
    document_media_id: int | None = None
    verified: bool
    created_at: datetime
