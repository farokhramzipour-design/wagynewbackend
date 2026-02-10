from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import (
    ProviderAvailabilityOverride,
    ProviderAvailabilityRule,
    ProviderTimeOff,
)
from app.models.bookings import Booking


def _validate_time_range(start: datetime, end: datetime) -> None:
    if start >= end:
        raise HTTPException(status_code=400, detail="invalid_time_range")


def _iter_dates(start_date: date, end_date: date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


async def create_rule(session: AsyncSession, *, payload: dict) -> ProviderAvailabilityRule:
    await _validate_rule_conflicts(session, payload)
    rule = ProviderAvailabilityRule(**payload)
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


async def update_rule(
    session: AsyncSession, *, rule_id: int, payload: dict
) -> ProviderAvailabilityRule:
    rule = await session.get(ProviderAvailabilityRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule_not_found")

    updates = {**payload}
    test_payload = {
        "provider_id": rule.provider_id,
        "service_type_id": updates.get("service_type_id", rule.service_type_id),
        "day_of_week": updates.get("day_of_week", rule.day_of_week),
        "start_time": updates.get("start_time", rule.start_time),
        "end_time": updates.get("end_time", rule.end_time),
        "capacity": updates.get("capacity", rule.capacity),
        "is_active": updates.get("is_active", rule.is_active),
    }
    await _validate_rule_conflicts(session, test_payload, exclude_rule_id=rule_id)

    for field, value in updates.items():
        setattr(rule, field, value)

    await session.commit()
    await session.refresh(rule)
    return rule


async def delete_rule(session: AsyncSession, *, rule_id: int) -> None:
    rule = await session.get(ProviderAvailabilityRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule_not_found")
    await session.delete(rule)
    await session.commit()


async def get_rule(session: AsyncSession, *, rule_id: int) -> ProviderAvailabilityRule:
    rule = await session.get(ProviderAvailabilityRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule_not_found")
    return rule


async def list_rules(session: AsyncSession, *, provider_id: int):
    return (
        await session.scalars(
            select(ProviderAvailabilityRule).where(
                ProviderAvailabilityRule.provider_id == provider_id
            )
        )
    ).all()


async def create_override(
    session: AsyncSession, *, payload: dict
) -> ProviderAvailabilityOverride:
    await _validate_override_conflicts(session, payload)
    override = ProviderAvailabilityOverride(**payload)
    session.add(override)
    await session.commit()
    await session.refresh(override)
    return override


async def update_override(
    session: AsyncSession, *, override_id: int, payload: dict
) -> ProviderAvailabilityOverride:
    override = await session.get(ProviderAvailabilityOverride, override_id)
    if not override:
        raise HTTPException(status_code=404, detail="override_not_found")

    test_payload = {
        "provider_id": override.provider_id,
        "date": payload.get("date", override.date),
        "service_type_id": payload.get("service_type_id", override.service_type_id),
    }
    await _validate_override_conflicts(session, test_payload, exclude_override_id=override_id)

    for field, value in payload.items():
        setattr(override, field, value)

    await session.commit()
    await session.refresh(override)
    return override


async def delete_override(session: AsyncSession, *, override_id: int) -> None:
    override = await session.get(ProviderAvailabilityOverride, override_id)
    if not override:
        raise HTTPException(status_code=404, detail="override_not_found")
    await session.delete(override)
    await session.commit()


async def get_override(
    session: AsyncSession, *, override_id: int
) -> ProviderAvailabilityOverride:
    override = await session.get(ProviderAvailabilityOverride, override_id)
    if not override:
        raise HTTPException(status_code=404, detail="override_not_found")
    return override


async def list_overrides(session: AsyncSession, *, provider_id: int):
    return (
        await session.scalars(
            select(ProviderAvailabilityOverride).where(
                ProviderAvailabilityOverride.provider_id == provider_id
            )
        )
    ).all()


async def create_time_off(session: AsyncSession, *, payload: dict) -> ProviderTimeOff:
    await _validate_time_off_conflicts(session, payload)
    time_off = ProviderTimeOff(**payload)
    session.add(time_off)
    await session.commit()
    await session.refresh(time_off)
    return time_off


async def update_time_off(
    session: AsyncSession, *, time_off_id: int, payload: dict
) -> ProviderTimeOff:
    time_off = await session.get(ProviderTimeOff, time_off_id)
    if not time_off:
        raise HTTPException(status_code=404, detail="time_off_not_found")

    test_payload = {
        "provider_id": time_off.provider_id,
        "start_datetime": payload.get("start_datetime", time_off.start_datetime),
        "end_datetime": payload.get("end_datetime", time_off.end_datetime),
    }
    await _validate_time_off_conflicts(session, test_payload, exclude_time_off_id=time_off_id)

    for field, value in payload.items():
        setattr(time_off, field, value)

    await session.commit()
    await session.refresh(time_off)
    return time_off


async def delete_time_off(session: AsyncSession, *, time_off_id: int) -> None:
    time_off = await session.get(ProviderTimeOff, time_off_id)
    if not time_off:
        raise HTTPException(status_code=404, detail="time_off_not_found")
    await session.delete(time_off)
    await session.commit()


async def get_time_off(session: AsyncSession, *, time_off_id: int) -> ProviderTimeOff:
    time_off = await session.get(ProviderTimeOff, time_off_id)
    if not time_off:
        raise HTTPException(status_code=404, detail="time_off_not_found")
    return time_off


async def list_time_off(session: AsyncSession, *, provider_id: int):
    return (
        await session.scalars(
            select(ProviderTimeOff).where(ProviderTimeOff.provider_id == provider_id)
        )
    ).all()


async def is_provider_available(
    session: AsyncSession,
    *,
    provider_id: int,
    service_type_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    requested_units: int,
) -> bool:
    _validate_time_range(start_datetime, end_datetime)
    if requested_units <= 0:
        raise HTTPException(status_code=400, detail="invalid_requested_units")

    # 1) Time off overrides everything
    time_off = await session.scalar(
        select(ProviderTimeOff).where(
            ProviderTimeOff.provider_id == provider_id,
            ProviderTimeOff.start_datetime < end_datetime,
            ProviderTimeOff.end_datetime > start_datetime,
        )
    )
    if time_off:
        return False

    start_date = start_datetime.date()
    end_date = end_datetime.date()
    if start_date != end_date:
        return await _is_available_multi_day(
            session,
            provider_id=provider_id,
            service_type_id=service_type_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            requested_units=requested_units,
        )

    # 2) Overrides for the date
    overrides = (
        await session.scalars(
            select(ProviderAvailabilityOverride).where(
                ProviderAvailabilityOverride.provider_id == provider_id,
                ProviderAvailabilityOverride.date == start_date,
                or_(
                    ProviderAvailabilityOverride.service_type_id == service_type_id,
                    ProviderAvailabilityOverride.service_type_id.is_(None),
                ),
            )
        )
    ).all()

    # prefer specific override
    specific_override = next(
        (o for o in overrides if o.service_type_id == service_type_id), None
    )
    generic_override = next(
        (o for o in overrides if o.service_type_id is None), None
    )

    override = specific_override or generic_override
    if override:
        if not override.is_available:
            return False
        if override.capacity is not None:
            capacity = override.capacity
            overlapping = await _count_overlapping_bookings(
                session, provider_id, start_datetime, end_datetime
            )
            return capacity >= (requested_units + overlapping)
        # fall back to rules capacity when override has no capacity

    # 3) Rules
    day_of_week = start_datetime.weekday()
    rules = (
        await session.scalars(
            select(ProviderAvailabilityRule).where(
                ProviderAvailabilityRule.provider_id == provider_id,
                ProviderAvailabilityRule.day_of_week == day_of_week,
                ProviderAvailabilityRule.is_active.is_(True),
                or_(
                    ProviderAvailabilityRule.service_type_id == service_type_id,
                    ProviderAvailabilityRule.service_type_id.is_(None),
                ),
                ProviderAvailabilityRule.start_time <= start_datetime.time(),
                ProviderAvailabilityRule.end_time >= end_datetime.time(),
            )
        )
    ).all()

    if not rules:
        return False

    max_capacity = max(r.capacity for r in rules)
    overlapping = await _count_overlapping_bookings(
        session, provider_id, start_datetime, end_datetime
    )
    return max_capacity >= (requested_units + overlapping)


async def _count_overlapping_bookings(
    session: AsyncSession, provider_id: int, start_datetime: datetime, end_datetime: datetime
) -> int:
    return await session.scalar(
        select(func.count(Booking.booking_id)).where(
            Booking.provider_id == provider_id,
            Booking.status.in_(["confirmed", "started", "in_progress"]),
            Booking.start_datetime < end_datetime,
            Booking.end_datetime > start_datetime,
        )
    )


async def _is_available_multi_day(
    session: AsyncSession,
    *,
    provider_id: int,
    service_type_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    requested_units: int,
) -> bool:
    current = start_datetime.date()
    end = end_datetime.date()
    while current <= end:
        day_start = datetime.combine(current, datetime.min.time(), start_datetime.tzinfo)
        day_end = datetime.combine(current, datetime.max.time(), start_datetime.tzinfo)
        if not await is_provider_available(
            session,
            provider_id=provider_id,
            service_type_id=service_type_id,
            start_datetime=day_start,
            end_datetime=day_end,
            requested_units=requested_units,
        ):
            return False
        current += timedelta(days=1)
    return True


async def _validate_rule_conflicts(
    session: AsyncSession, payload: dict, exclude_rule_id: int | None = None
) -> None:
    if payload["start_time"] >= payload["end_time"]:
        raise HTTPException(status_code=400, detail="invalid_time_range")

    conditions = [
        ProviderAvailabilityRule.provider_id == payload["provider_id"],
        ProviderAvailabilityRule.day_of_week == payload["day_of_week"],
        ProviderAvailabilityRule.start_time < payload["end_time"],
        ProviderAvailabilityRule.end_time > payload["start_time"],
    ]

    if payload.get("service_type_id") is None:
        conditions.append(ProviderAvailabilityRule.service_type_id.is_(None))
    else:
        conditions.append(
            ProviderAvailabilityRule.service_type_id == payload["service_type_id"]
        )

    if exclude_rule_id:
        conditions.append(ProviderAvailabilityRule.rule_id != exclude_rule_id)

    conflict = await session.scalar(select(ProviderAvailabilityRule).where(and_(*conditions)))
    if conflict:
        raise HTTPException(status_code=409, detail="availability_rule_conflict")


async def _validate_override_conflicts(
    session: AsyncSession, payload: dict, exclude_override_id: int | None = None
) -> None:
    conditions = [
        ProviderAvailabilityOverride.provider_id == payload["provider_id"],
        ProviderAvailabilityOverride.date == payload["date"],
    ]

    if payload.get("service_type_id") is None:
        conditions.append(ProviderAvailabilityOverride.service_type_id.is_(None))
    else:
        conditions.append(
            ProviderAvailabilityOverride.service_type_id == payload["service_type_id"]
        )

    if exclude_override_id:
        conditions.append(ProviderAvailabilityOverride.override_id != exclude_override_id)

    conflict = await session.scalar(
        select(ProviderAvailabilityOverride).where(and_(*conditions))
    )
    if conflict:
        raise HTTPException(status_code=409, detail="availability_override_conflict")


async def _validate_time_off_conflicts(
    session: AsyncSession, payload: dict, exclude_time_off_id: int | None = None
) -> None:
    if payload["start_datetime"] >= payload["end_datetime"]:
        raise HTTPException(status_code=400, detail="invalid_time_range")

    conditions = [
        ProviderTimeOff.provider_id == payload["provider_id"],
        ProviderTimeOff.start_datetime < payload["end_datetime"],
        ProviderTimeOff.end_datetime > payload["start_datetime"],
    ]
    if exclude_time_off_id:
        conditions.append(ProviderTimeOff.time_off_id != exclude_time_off_id)

    conflict = await session.scalar(select(ProviderTimeOff).where(and_(*conditions)))
    if conflict:
        raise HTTPException(status_code=409, detail="time_off_conflict")
