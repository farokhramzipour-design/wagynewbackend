from datetime import datetime

from pydantic import BaseModel, Field


class BookingPaymentCreate(BaseModel):
    booking_id: int
    kind: str
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    raw_response_json: dict | None = None


class PaymentCallback(BaseModel):
    payment_id: int | None = None
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    status: str
    raw_response_json: dict | None = None


class RefundCreate(BaseModel):
    booking_id: int
    payer_user_id: int | None = None
    payee_user_id: int | None = None
    currency_code: str = Field(..., min_length=3, max_length=3)
    amount_minor: int
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    raw_response_json: dict | None = None
    credit_wallet_user_id: int | None = None


class PayoutCreate(BaseModel):
    booking_id: int | None = None
    payer_user_id: int | None = None
    payee_user_id: int
    currency_code: str = Field(..., min_length=3, max_length=3)
    amount_minor: int
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    raw_response_json: dict | None = None


class WalletAdjust(BaseModel):
    user_id: int
    currency_code: str = Field(..., min_length=3, max_length=3)
    amount_minor: int
    reason: str | None = None
    related_payment_id: int | None = None


class PaymentAdjustmentCreate(BaseModel):
    booking_id: int | None = None
    payer_user_id: int | None = None
    payee_user_id: int | None = None
    currency_code: str = Field(..., min_length=3, max_length=3)
    amount_minor: int
    status: str = "captured"
    raw_response_json: dict | None = None


class PaymentOut(BaseModel):
    payment_id: int
    booking_id: int | None = None
    payer_user_id: int | None = None
    payee_user_id: int | None = None
    kind: str
    status: str
    currency_code: str
    amount_minor: int
    gateway_id: int | None = None
    gateway_transaction_id: str | None = None
    created_at: datetime | None = None


class BookingLedgerOut(BaseModel):
    booking_id: int
    pricing: dict | None = None
    payments: list[PaymentOut]
    wallet_transactions: list[dict]
