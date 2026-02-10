from datetime import datetime

from pydantic import BaseModel


class CharityCaseCreate(BaseModel):
    creator_user_id: int
    title: str
    description: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    currency_code: str
    target_amount_minor: int


class CharityCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    target_amount_minor: int | None = None


class CharityStatusUpdate(BaseModel):
    status: str
    admin_user_id: int


class CharityDonationCreate(BaseModel):
    charity_case_id: int
    donor_user_id: int | None = None
    payment_id: int | None = None
    status: str
    currency_code: str
    amount_minor: int
    donation_reference: str


class CharityUpdateCreate(BaseModel):
    charity_case_id: int
    author_user_id: int | None = None
    body: str
    spent_amount_minor: int | None = None
    currency_code: str | None = None


class CharityUpdateMediaCreate(BaseModel):
    charity_update_id: int
    media_id: int
    sort_order: int | None = None


class CharityUpdateOut(BaseModel):
    charity_update_id: int
    charity_case_id: int
    author_user_id: int | None = None
    body: str
    spent_amount_minor: int | None = None
    currency_code: str | None = None
    created_at: datetime


class CharityCaseOut(BaseModel):
    charity_case_id: int
    creator_user_id: int
    status: str
    title: str
    description: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    currency_code: str
    target_amount_minor: int
    collected_amount_minor: int
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by_user_id: int | None = None
    approved_at: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
