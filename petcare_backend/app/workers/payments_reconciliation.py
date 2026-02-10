from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment


async def reconcile_pending_payments(session: AsyncSession) -> list[int]:
    """
    Placeholder reconciliation job.
    Fetches pending payments and returns their IDs for downstream gateway sync.
    """
    cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
    pending = (
        await session.scalars(
            select(Payment.payment_id).where(
                Payment.status == "pending",
                Payment.created_at < cutoff,
            )
        )
    ).all()
    return pending
