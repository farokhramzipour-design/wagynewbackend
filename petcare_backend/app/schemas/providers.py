from datetime import datetime

from pydantic import BaseModel, Field


class ProviderDraftCreate(BaseModel):
    user_id: int


class ProviderProfileUpdate(BaseModel):
    headline: str | None = None
    bio: str | None = None
    years_of_experience: int | None = None
    service_radius_km: int | None = None
    is_star_sitter: bool | None = None
    response_rate_percent: int | None = None
    avg_response_time_minutes: int | None = None
    total_completed_bookings: int | None = None
    repeat_clients_count: int | None = None
    average_rating: float | None = None
    featured: bool | None = None


class ProviderHomeUpsert(BaseModel):
    home_type: str | None = None
    has_fenced_yard: bool | None = None
    smoking_household: bool | None = None
    has_children: bool | None = None
    has_pets: bool | None = None
    work_from_home: bool | None = None


class ProviderVerificationCreate(BaseModel):
    type: str
    status: str
    report_media_id: int | None = None
    verified_at: datetime | None = None


class ProviderServiceUpsert(BaseModel):
    service_type_id: int
    is_active: bool
    max_pets: int | None = None


class ProviderServiceRateCreate(BaseModel):
    currency_code: str = Field(..., min_length=3, max_length=3)
    unit: str
    base_amount_minor: int
    duration_minutes: int | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class ProviderRateEstimateRequest(BaseModel):
    pets_count: int = Field(..., ge=1)
    is_puppy: bool = False
    is_holiday: bool = False


class ProviderRateEstimateOut(BaseModel):
    subtotal_minor: int
    total_minor: int
    breakdown_json: dict


class ProviderStatusUpdate(BaseModel):
    status: str
    admin_user_id: int
    reason: str | None = None


class ProviderOut(BaseModel):
    provider_id: int
    user_id: int
    status: str
    headline: str | None = None
    bio: str | None = None
    years_of_experience: int | None = None
    service_radius_km: int | None = None
    is_star_sitter: bool | None = None
    response_rate_percent: int | None = None
    avg_response_time_minutes: int | None = None
    total_completed_bookings: int | None = None
    repeat_clients_count: int | None = None
    average_rating: float | None = None
    featured: bool | None = None


class ProviderServiceCardOut(BaseModel):
    provider_service_id: int
    service_type_id: int
    service_code: str
    status: str
    is_active: bool
    max_pets: int | None = None
    currency_code: str | None = None
    unit: str | None = None
    base_amount_minor: int | None = None
    duration_minutes: int | None = None
    policies_json: dict | None = None


class ProviderProfileViewerOut(BaseModel):
    provider: ProviderOut
    user_profile: dict | None = None
    home: dict | None = None
    services: list[ProviderServiceCardOut]
    provider_verified: bool | None = None
    identity_verified: bool | None = None
