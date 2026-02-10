from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Wallet, WalletTransaction


async def get_wallet(
    session: AsyncSession, *, user_id: int, currency_code: str
) -> Wallet:
    wallet = await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id, Wallet.currency_code == currency_code)
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet_not_found")
    return wallet


async def list_transactions(
    session: AsyncSession,
    *,
    wallet_id: int,
    limit: int,
    cursor_created_at: datetime | None = None,
    cursor_tx_id: int | None = None,
) -> list[WalletTransaction]:
    query = select(WalletTransaction).where(WalletTransaction.wallet_id == wallet_id)
    query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.wallet_tx_id.desc())

    if cursor_created_at and cursor_tx_id:
        query = query.where(
            (WalletTransaction.created_at < cursor_created_at)
            | (
                (WalletTransaction.created_at == cursor_created_at)
                & (WalletTransaction.wallet_tx_id < cursor_tx_id)
            )
        )

    return (await session.scalars(query.limit(limit))).all()
