from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


class AvailabilityRuleCreate(BaseModel):
    provider_id: int
    service_type_id: Optional[int] = None
    day_of_week: int
    start_time: time
    end_time: time
    capacity: int
    is_active: bool


class AvailabilityRuleUpdate(BaseModel):
    service_type_id: Optional[int] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class AvailabilityOverrideCreate(BaseModel):
    provider_id: int
    date: date
    service_type_id: Optional[int] = None
    is_available: bool
    capacity: Optional[int] = None
    note: Optional[str] = None


class AvailabilityOverrideUpdate(BaseModel):
    date: Optional[date] = None
    service_type_id: Optional[int] = None
    is_available: Optional[bool] = None
    capacity: Optional[int] = None
    note: Optional[str] = None


class TimeOffCreate(BaseModel):
    provider_id: int
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None


class TimeOffUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = None


class AvailabilityCheckRequest(BaseModel):
    provider_id: int
    service_type_id: int
    start_datetime: datetime
    end_datetime: datetime
    requested_units: int


class ProviderCalendarBookingOut(BaseModel):
    booking_id: int
    service_type_id: int
    status: str
    start_datetime: datetime
    end_datetime: datetime


class ProviderCalendarTimeOffOut(BaseModel):
    time_off_id: int
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None


class ProviderCalendarOverrideOut(BaseModel):
    override_id: int
    date: date
    service_type_id: Optional[int] = None
    is_available: bool
    capacity: Optional[int] = None
    note: Optional[str] = None


class ProviderCalendarOut(BaseModel):
    bookings: list[ProviderCalendarBookingOut]
    time_off: list[ProviderCalendarTimeOffOut]
    overrides: list[ProviderCalendarOverrideOut]
