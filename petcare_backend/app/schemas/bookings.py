from datetime import datetime

from pydantic import BaseModel


class BookingPetCreate(BaseModel):
    pet_id: int
    per_pet_notes: str | None = None


class BookingRequestCreate(BaseModel):
    booking_reference: str
    owner_user_id: int
    provider_id: int
    service_type_id: int
    start_datetime: datetime
    end_datetime: datetime
    pets: list[BookingPetCreate]


class BookingAction(BaseModel):
    actor_type: str
    actor_user_id: int | None = None
    payload_json: dict | None = None


class BookingConfirmRequest(BaseModel):
    actor_type: str
    actor_user_id: int | None = None
    payload_json: dict | None = None
    payment_kind: str | None = None
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    currency_code: str
    subtotal_minor: int
    owner_fee_minor: int
    provider_fee_minor: int
    total_charge_minor: int
    provider_payout_minor: int
    breakdown_json: dict


class BookingCancelRequest(BaseModel):
    actor_type: str
    actor_user_id: int | None = None
    cancelled_by: str
    reason: str | None = None
    policy_snapshot_json: dict | None = None
    refund_minor: int | None = None
    payload_json: dict | None = None


class BookingEventOut(BaseModel):
    event_id: int
    booking_id: int
    event_type: str
    actor_type: str
    actor_user_id: int | None = None
    payload_json: dict | None = None
    created_at: datetime


class BookingCancelOut(BaseModel):
    booking_id: int
    status: str
    cancellation_id: int
    refund_minor: int | None = None
    policy_snapshot_json: dict | None = None
