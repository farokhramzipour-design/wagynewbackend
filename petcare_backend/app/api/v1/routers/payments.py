from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.payments import (
    BookingPaymentCreate,
    BookingLedgerOut,
    PaymentCallback,
    PaymentAdjustmentCreate,
    PaymentOut,
    PayoutCreate,
    RefundCreate,
)
from app.services.payments import (
    create_payment_for_booking_confirm,
    create_adjustment,
    create_payout,
    create_refund,
    get_booking_ledger,
    list_payments_for_booking,
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


@router.post("/adjustments")
async def create_adjustment_endpoint(
    payload: PaymentAdjustmentCreate, db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        payment = await create_adjustment(
            db,
            booking_id=payload.booking_id,
            payer_user_id=payload.payer_user_id,
            payee_user_id=payload.payee_user_id,
            currency_code=payload.currency_code,
            amount_minor=payload.amount_minor,
            status=payload.status,
            raw_response_json=payload.raw_response_json,
        )
    return {"payment_id": payment.payment_id, "status": payment.status}


@router.get("/booking/{booking_id}", response_model=list[PaymentOut])
async def list_booking_payments(
    booking_id: int, db: AsyncSession = Depends(get_db)
) -> list[PaymentOut]:
    payments = await list_payments_for_booking(db, booking_id=booking_id)
    return [PaymentOut.model_validate(p, from_attributes=True) for p in payments]


@router.get("/booking/{booking_id}/ledger", response_model=BookingLedgerOut)
async def booking_ledger_endpoint(
    booking_id: int, db: AsyncSession = Depends(get_db)
) -> BookingLedgerOut:
    data = await get_booking_ledger(db, booking_id=booking_id)
    pricing = data["pricing"]
    return BookingLedgerOut(
        booking_id=booking_id,
        pricing=None
        if pricing is None
        else {
            "currency_code": pricing.currency_code,
            "subtotal_minor": pricing.subtotal_minor,
            "owner_fee_minor": pricing.owner_fee_minor,
            "provider_fee_minor": pricing.provider_fee_minor,
            "total_charge_minor": pricing.total_charge_minor,
            "provider_payout_minor": pricing.provider_payout_minor,
            "breakdown_json": pricing.breakdown_json,
        },
        payments=[PaymentOut.model_validate(p, from_attributes=True) for p in data["payments"]],
        wallet_transactions=[
            {
                "wallet_tx_id": tx.wallet_tx_id,
                "wallet_id": tx.wallet_id,
                "amount_minor": tx.amount_minor,
                "reason": tx.reason,
                "related_payment_id": tx.related_payment_id,
                "created_at": tx.created_at,
            }
            for tx in data["wallet_transactions"]
        ],
    )
