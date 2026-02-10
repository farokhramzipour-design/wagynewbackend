from datetime import date

from pydantic import BaseModel


class SearchProvidersRequest(BaseModel):
    user_id: int | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    service_type_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    filters_json: dict | None = None
    require_provider_verification_status: str | None = None
    require_user_verification_status: str | None = None
    requested_units: int | None = None
    home_type: str | None = None
    has_fenced_yard: bool | None = None
    smoking_household: bool | None = None
    has_children: bool | None = None
    has_pets: bool | None = None
    work_from_home: bool | None = None


class ProviderSearchResult(BaseModel):
    provider_id: int
    user_id: int
    distance_km: float | None = None
    average_rating: float | None = None
    response_rate_percent: int | None = None
    total_completed_bookings: int | None = None
    featured: bool | None = None
    is_star_sitter: bool | None = None
    score: float


class SearchHistoryOut(BaseModel):
    search_id: int
    user_id: int | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    service_type_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    filters_json: dict | None = None
    results_count: int | None = None


class FavoriteCreate(BaseModel):
    user_id: int
    provider_id: int
