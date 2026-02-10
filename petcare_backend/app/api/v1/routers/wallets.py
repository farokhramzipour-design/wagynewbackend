from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.wallets import WalletOut, WalletTransactionOut
from app.services.wallets import get_wallet, list_transactions

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.get("/", response_model=WalletOut)
async def get_wallet_endpoint(
    user_id: int, currency_code: str, db: AsyncSession = Depends(get_db)
) -> WalletOut:
    wallet = await get_wallet(db, user_id=user_id, currency_code=currency_code)
    return WalletOut.model_validate(wallet, from_attributes=True)


@router.get("/transactions", response_model=list[WalletTransactionOut])
async def list_transactions_endpoint(
    wallet_id: int,
    limit: int = Query(50, ge=1, le=200),
    cursor_created_at: str | None = None,
    cursor_tx_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    parsed_cursor = datetime.fromisoformat(cursor_created_at) if cursor_created_at else None
    records = await list_transactions(
        db,
        wallet_id=wallet_id,
        limit=limit,
        cursor_created_at=parsed_cursor,
        cursor_tx_id=cursor_tx_id,
    )
    return [WalletTransactionOut.model_validate(r, from_attributes=True) for r in records]
