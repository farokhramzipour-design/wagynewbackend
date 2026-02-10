from sqlalchemy import select

from app.models.payments import Payment, Wallet
from app.repositories.base import BaseRepository


class PaymentsRepository(BaseRepository):
    async def get_by_gateway(self, gateway_id: int, gateway_transaction_id: str) -> Payment | None:
        return await self.session.scalar(
            select(Payment).where(
                Payment.gateway_id == gateway_id,
                Payment.gateway_transaction_id == gateway_transaction_id,
            )
        )

    async def create(self, payload: dict) -> Payment:
        payment = Payment(**payload)
        self.session.add(payment)
        await self.session.flush()
        return payment


class WalletsRepository(BaseRepository):
    async def get_for_update(self, wallet_id: int) -> Wallet | None:
        return await self.session.scalar(
            select(Wallet).where(Wallet.wallet_id == wallet_id).with_for_update()
        )

    async def get_by_user_currency(self, user_id: int, currency_code: str) -> Wallet | None:
        return await self.session.scalar(
            select(Wallet).where(Wallet.user_id == user_id, Wallet.currency_code == currency_code)
        )
