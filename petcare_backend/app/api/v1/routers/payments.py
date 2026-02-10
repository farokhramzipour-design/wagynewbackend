from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.payments import BookingPaymentCreate, PaymentCallback, PayoutCreate, RefundCreate
from app.services.payments import (
    create_payment_for_booking_confirm,
    create_payout,
    create_refund,
    update_payment_from_callback,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/booking")
async def create_booking_payment(
    payload: BookingPaymentCreate, db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        payment = await create_payment_for_booking_confirm(
            db,
            booking_id=payload.booking_id,
            kind=payload.kind,
            gateway_id=payload.gateway_id,
            gateway_transaction_id=payload.gateway_transaction_id,
            raw_response_json=payload.raw_response_json,
        )
    return {"payment_id": payment.payment_id, "status": payment.status}


@router.post("/gateway/callback")
async def gateway_callback(payload: PaymentCallback, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        payment = await update_payment_from_callback(
            db,
            payment_id=payload.payment_id,
            gateway_id=payload.gateway_id,
            gateway_transaction_id=payload.gateway_transaction_id,
            status=payload.status,
            raw_response_json=payload.raw_response_json,
        )
    return {"payment_id": payment.payment_id, "status": payment.status}


@router.post("/refunds")
async def create_refund_endpoint(payload: RefundCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        payment = await create_refund(
            db,
            booking_id=payload.booking_id,
            payer_user_id=payload.payer_user_id,
            payee_user_id=payload.payee_user_id,
            currency_code=payload.currency_code,
            amount_minor=payload.amount_minor,
            gateway_id=payload.gateway_id,
            gateway_transaction_id=payload.gateway_transaction_id,
            raw_response_json=payload.raw_response_json,
            credit_wallet_user_id=payload.credit_wallet_user_id,
        )
    return {"payment_id": payment.payment_id, "status": payment.status}


@router.post("/payouts")
async def create_payout_endpoint(payload: PayoutCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        payment = await create_payout(
            db,
            booking_id=payload.booking_id,
            payer_user_id=payload.payer_user_id,
            payee_user_id=payload.payee_user_id,
            currency_code=payload.currency_code,
            amount_minor=payload.amount_minor,
            gateway_id=payload.gateway_id,
            gateway_transaction_id=payload.gateway_transaction_id,
            raw_response_json=payload.raw_response_json,
        )
    return {"payment_id": payment.payment_id, "status": payment.status}
