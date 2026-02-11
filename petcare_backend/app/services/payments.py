from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking, BookingPricing
from app.models.payments import Payment, Wallet, WalletTransaction
from app.models.providers import Provider


def _get_payment_by_gateway(
    *, session: AsyncSession, gateway_id: int, gateway_transaction_id: str, kind: str
):
    return select(Payment).where(
        Payment.gateway_id == gateway_id,
        Payment.gateway_transaction_id == gateway_transaction_id,
        Payment.kind == kind,
    )


async def create_payment_for_booking_confirm(
    session: AsyncSession,
    *,
    booking_id: int,
    kind: str,
    gateway_id: int | None,
    gateway_transaction_id: str | None,
    raw_response_json: dict | None,
) -> Payment:
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="booking_not_found")

    pricing = await session.get(BookingPricing, booking_id)
    if not pricing:
        raise HTTPException(status_code=400, detail="pricing_missing")

    provider = await session.get(Provider, booking.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="provider_not_found")

    if gateway_id and gateway_transaction_id:
        existing = await session.scalar(
            _get_payment_by_gateway(
                session=session,
                gateway_id=gateway_id,
                gateway_transaction_id=gateway_transaction_id,
                kind=kind,
            )
        )
        if existing:
            return existing

    existing_booking_payment = await session.scalar(
        select(Payment).where(
            Payment.booking_id == booking_id,
            Payment.kind == kind,
        )
    )
    if existing_booking_payment:
        return existing_booking_payment

    payment = Payment(
        booking_id=booking_id,
        payer_user_id=booking.owner_user_id,
        payee_user_id=provider.user_id,
        kind=kind,
        status="pending",
        currency_code=pricing.currency_code,
        amount_minor=pricing.total_charge_minor,
        gateway_id=gateway_id,
        gateway_transaction_id=gateway_transaction_id,
        raw_response_json=raw_response_json,
    )
    session.add(payment)
    await session.flush()
    return payment


async def update_payment_from_callback(
    session: AsyncSession,
    *,
    payment_id: int | None,
    gateway_id: int | None,
    gateway_transaction_id: str | None,
    status: str,
    raw_response_json: dict | None,
) -> Payment:
    payment = None
    if payment_id is not None:
        payment = await session.get(Payment, payment_id)
    elif gateway_id and gateway_transaction_id:
        payment = await session.scalar(
            select(Payment).where(
                Payment.gateway_id == gateway_id,
                Payment.gateway_transaction_id == gateway_transaction_id,
            )
        )

    if not payment:
        raise HTTPException(status_code=404, detail="payment_not_found")

    payment.status = status
    payment.raw_response_json = raw_response_json
    await session.flush()
    return payment


async def create_refund(
    session: AsyncSession,
    *,
    booking_id: int,
    payer_user_id: int | None,
    payee_user_id: int | None,
    currency_code: str,
    amount_minor: int,
    gateway_id: int | None,
    gateway_transaction_id: str | None,
    raw_response_json: dict | None,
    credit_wallet_user_id: int | None,
) -> Payment:
    if gateway_id and gateway_transaction_id:
        existing = await session.scalar(
            _get_payment_by_gateway(
                session=session,
                gateway_id=gateway_id,
                gateway_transaction_id=gateway_transaction_id,
                kind="refund",
            )
        )
        if existing:
            return existing

    payment = Payment(
        booking_id=booking_id,
        payer_user_id=payer_user_id,
        payee_user_id=payee_user_id,
        kind="refund",
        status="pending",
        currency_code=currency_code,
        amount_minor=amount_minor,
        gateway_id=gateway_id,
        gateway_transaction_id=gateway_transaction_id,
        raw_response_json=raw_response_json,
    )
    session.add(payment)
    await session.flush()

    if credit_wallet_user_id is not None:
        await credit_wallet(
            session,
            user_id=credit_wallet_user_id,
            currency_code=currency_code,
            amount_minor=amount_minor,
            reason="refund",
            related_payment_id=payment.payment_id,
        )

    return payment


async def create_payout(
    session: AsyncSession,
    *,
    booking_id: int | None,
    payer_user_id: int | None,
    payee_user_id: int,
    currency_code: str,
    amount_minor: int,
    gateway_id: int | None,
    gateway_transaction_id: str | None,
    raw_response_json: dict | None,
) -> Payment:
    if gateway_id and gateway_transaction_id:
        existing = await session.scalar(
            _get_payment_by_gateway(
                session=session,
                gateway_id=gateway_id,
                gateway_transaction_id=gateway_transaction_id,
                kind="payout",
            )
        )
        if existing:
            return existing

    payment = Payment(
        booking_id=booking_id,
        payer_user_id=payer_user_id,
        payee_user_id=payee_user_id,
        kind="payout",
        status="paid_out",
        currency_code=currency_code,
        amount_minor=amount_minor,
        gateway_id=gateway_id,
        gateway_transaction_id=gateway_transaction_id,
        raw_response_json=raw_response_json,
    )
    session.add(payment)
    await session.flush()
    return payment


async def create_adjustment(
    session: AsyncSession,
    *,
    booking_id: int | None,
    payer_user_id: int | None,
    payee_user_id: int | None,
    currency_code: str,
    amount_minor: int,
    status: str,
    raw_response_json: dict | None,
) -> Payment:
    payment = Payment(
        booking_id=booking_id,
        payer_user_id=payer_user_id,
        payee_user_id=payee_user_id,
        kind="adjustment",
        status=status,
        currency_code=currency_code,
        amount_minor=amount_minor,
        gateway_id=None,
        gateway_transaction_id=None,
        raw_response_json=raw_response_json,
    )
    session.add(payment)
    await session.flush()
    return payment


async def credit_wallet(
    session: AsyncSession,
    *,
    user_id: int,
    currency_code: str,
    amount_minor: int,
    reason: str | None,
    related_payment_id: int | None,
) -> Wallet:
    wallet = await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id, Wallet.currency_code == currency_code)
    )
    if not wallet:
        wallet = Wallet(user_id=user_id, currency_code=currency_code, balance_minor=0)
        session.add(wallet)
        await session.flush()

    wallet.balance_minor += amount_minor
    session.add(
        WalletTransaction(
            wallet_id=wallet.wallet_id,
            amount_minor=amount_minor,
            reason=reason,
            related_payment_id=related_payment_id,
        )
    )
    await session.flush()
    return wallet


async def list_payments_for_booking(
    session: AsyncSession, *, booking_id: int
) -> list[Payment]:
    return (
        await session.scalars(
            select(Payment)
            .where(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.desc())
        )
    ).all()


async def list_wallet_transactions_for_booking(
    session: AsyncSession, *, booking_id: int
) -> list[WalletTransaction]:
    return (
        await session.scalars(
            select(WalletTransaction)
            .join(Payment, Payment.payment_id == WalletTransaction.related_payment_id)
            .where(Payment.booking_id == booking_id)
            .order_by(WalletTransaction.created_at.desc())
        )
    ).all()


async def get_booking_ledger(
    session: AsyncSession, *, booking_id: int
) -> dict:
    pricing = await session.get(BookingPricing, booking_id)
    payments = await list_payments_for_booking(session, booking_id=booking_id)
    wallet_txs = await list_wallet_transactions_for_booking(session, booking_id=booking_id)
    return {
        "pricing": pricing,
        "payments": payments,
        "wallet_transactions": wallet_txs,
    }
