from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity import CharityCase, CharityDonation, CharityUpdate, CharityUpdateMedia
from app.models.users import UserVerification


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _require_transition(current: str, allowed: set[str]) -> None:
    if current not in allowed:
        raise HTTPException(status_code=400, detail="invalid_status_transition")


async def _require_verified_user(session: AsyncSession, user_id: int) -> bool:
    verification = await session.scalar(
        select(UserVerification).where(
            UserVerification.user_id == user_id, UserVerification.status == "passed"
        )
    )
    return verification is not None


async def create_case(session: AsyncSession, *, payload: dict) -> CharityCase:
    verified = await _require_verified_user(session, payload["creator_user_id"])
    if not verified:
        raise HTTPException(status_code=403, detail="user_not_verified")

    case = CharityCase(
        creator_user_id=payload["creator_user_id"],
        status="draft",
        title=payload["title"],
        description=payload.get("description"),
        province_id=payload.get("province_id"),
        city_id=payload.get("city_id"),
        lat=payload.get("lat"),
        lng=payload.get("lng"),
        currency_code=payload["currency_code"],
        target_amount_minor=payload["target_amount_minor"],
        collected_amount_minor=0,
    )
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


async def update_case(session: AsyncSession, *, case_id: int, payload: dict) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    _require_transition(case.status, {"draft"})
    for field, value in payload.items():
        setattr(case, field, value)

    await session.commit()
    await session.refresh(case)
    return case


async def submit_case(session: AsyncSession, *, case_id: int) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    _require_transition(case.status, {"draft"})
    case.status = "pending_review"
    case.submitted_at = _utcnow()
    await session.commit()
    await session.refresh(case)
    return case


async def admin_review_case(
    session: AsyncSession, *, case_id: int, status: str, admin_user_id: int
) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    if status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_status")

    _require_transition(case.status, {"pending_review"})
    case.reviewed_at = _utcnow()
    case.reviewed_by_user_id = admin_user_id
    if status == "approved":
        case.status = "approved"
        case.approved_at = _utcnow()
    else:
        case.status = "rejected"

    await session.commit()
    await session.refresh(case)
    return case


async def activate_case(session: AsyncSession, *, case_id: int) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    _require_transition(case.status, {"approved"})
    case.status = "active"
    await session.commit()
    await session.refresh(case)
    return case


async def close_case(session: AsyncSession, *, case_id: int, status: str) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    if status not in {"funded", "closed"}:
        raise HTTPException(status_code=400, detail="invalid_status")

    _require_transition(case.status, {"active"})
    case.status = status
    case.closed_at = _utcnow()
    await session.commit()
    await session.refresh(case)
    return case


async def create_donation(session: AsyncSession, *, payload: dict) -> CharityDonation:
    if payload.get("donor_user_id") is not None:
        verified = await _require_verified_user(session, payload["donor_user_id"])
        if not verified:
            raise HTTPException(status_code=403, detail="donor_not_verified")

    case = await session.get(CharityCase, payload["charity_case_id"])
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    if case.status != "active":
        raise HTTPException(status_code=400, detail="case_not_active")

    existing = await session.scalar(
        select(CharityDonation).where(
            CharityDonation.donation_reference == payload["donation_reference"]
        )
    )
    if existing:
        return existing

    donation = CharityDonation(
        charity_case_id=payload["charity_case_id"],
        donor_user_id=payload.get("donor_user_id"),
        payment_id=payload.get("payment_id"),
        status=payload["status"],
        currency_code=payload["currency_code"],
        amount_minor=payload["amount_minor"],
        donation_reference=payload["donation_reference"],
    )
    session.add(donation)
    await session.flush()

    if donation.status == "success":
        await _increment_collected_amount(
            session,
            charity_case_id=case.charity_case_id,
            amount_minor=donation.amount_minor,
        )

    await session.commit()
    await session.refresh(donation)
    return donation


async def create_update(session: AsyncSession, *, payload: dict) -> CharityUpdate:
    case = await session.get(CharityCase, payload["charity_case_id"])
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")

    if case.status not in {"active", "funded"}:
        raise HTTPException(status_code=400, detail="case_not_active")

    update_record = CharityUpdate(
        charity_case_id=payload["charity_case_id"],
        author_user_id=payload.get("author_user_id"),
        body=payload["body"],
        spent_amount_minor=payload.get("spent_amount_minor"),
        currency_code=payload.get("currency_code"),
    )
    session.add(update_record)
    await session.commit()
    await session.refresh(update_record)
    return update_record


async def create_update_media(session: AsyncSession, *, payload: dict) -> CharityUpdateMedia:
    record = CharityUpdateMedia(**payload)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def list_cases(session: AsyncSession, *, status: str | None = None) -> list[CharityCase]:
    query = select(CharityCase)
    if status:
        query = query.where(CharityCase.status == status)
    return (await session.scalars(query)).all()


async def get_case(session: AsyncSession, *, case_id: int) -> CharityCase:
    case = await session.get(CharityCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")
    return case


async def list_updates(session: AsyncSession, *, case_id: int) -> list[CharityUpdate]:
    return (
        await session.scalars(
            select(CharityUpdate).where(CharityUpdate.charity_case_id == case_id)
        )
    ).all()


async def _increment_collected_amount(
    session: AsyncSession, *, charity_case_id: int, amount_minor: int
) -> None:
    case = await session.get(CharityCase, charity_case_id, with_for_update=True)
    if not case:
        return

    new_amount = min(case.collected_amount_minor + amount_minor, case.target_amount_minor)
    case.collected_amount_minor = new_amount
    if new_amount >= case.target_amount_minor:
        case.status = "funded"
        case.closed_at = _utcnow()
