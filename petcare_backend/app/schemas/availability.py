from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel


class AvailabilityRuleCreate(BaseModel):
    provider_id: int
    service_type_id: int | None = None
    day_of_week: int
    start_time: time
    end_time: time
    capacity: int
    is_active: bool


class AvailabilityRuleUpdate(BaseModel):
    service_type_id: int | None = None
    day_of_week: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    capacity: int | None = None
    is_active: bool | None = None


class AvailabilityOverrideCreate(BaseModel):
    provider_id: int
    date: date
    service_type_id: int | None = None
    is_available: bool
    capacity: int | None = None
    note: str | None = None


class AvailabilityOverrideUpdate(BaseModel):
    date: date | None = None
    service_type_id: int | None = None
    is_available: bool | None = None
    capacity: int | None = None
    note: str | None = None


class TimeOffCreate(BaseModel):
    provider_id: int
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = None


class TimeOffUpdate(BaseModel):
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    reason: str | None = None


class AvailabilityCheckRequest(BaseModel):
    provider_id: int
    service_type_id: int
    start_datetime: datetime
    end_datetime: datetime
    requested_units: int
