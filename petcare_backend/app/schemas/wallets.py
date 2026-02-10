from datetime import datetime

from pydantic import BaseModel


class WalletOut(BaseModel):
    wallet_id: int
    user_id: int
    currency_code: str
    balance_minor: int
    updated_at: datetime | None = None


class WalletTransactionOut(BaseModel):
    wallet_tx_id: int
    wallet_id: int
    amount_minor: int
    reason: str | None = None
    related_payment_id: int | None = None
    created_at: datetime
