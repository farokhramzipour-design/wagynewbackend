from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfileCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    avatar_media_id: int | None = None
    bio: str | None = None


class RegisterRequest(BaseModel):
    phone_e164: str = Field(..., min_length=7, max_length=32)
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=128)
    profile: UserProfileCreate | None = None


class UserOut(BaseModel):
    user_id: int
    phone_e164: str
    email: EmailStr | None = None
    status: str
    locale: str
    timezone: str
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class LoginRequest(BaseModel):
    phone_e164: str = Field(..., min_length=7, max_length=32)
    password: str


class OtpRequest(BaseModel):
    phone_e164: str = Field(..., min_length=7, max_length=32)
    provider: str
    reference_id: str | None = None


class OtpVerifyRequest(BaseModel):
    phone_e164: str = Field(..., min_length=7, max_length=32)
    provider: str
    reference_id: str | None = None


class OtpStatusOut(BaseModel):
    status: str
    verified_at: datetime | None = None
