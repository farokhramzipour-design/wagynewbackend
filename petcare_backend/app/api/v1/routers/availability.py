from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.availability import (
    AvailabilityCheckRequest,
    AvailabilityOverrideCreate,
    AvailabilityOverrideUpdate,
    AvailabilityRuleCreate,
    AvailabilityRuleUpdate,
    ProviderCalendarOut,
    TimeOffCreate,
    TimeOffUpdate,
)
from app.services.availability import (
    create_override,
    create_rule,
    create_time_off,
    delete_override,
    delete_rule,
    delete_time_off,
    get_override,
    get_rule,
    get_time_off,
    get_provider_calendar,
    is_provider_available,
    list_overrides,
    list_rules,
    list_time_off,
    update_override,
    update_rule,
    update_time_off,
)

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/rules")
async def create_rule_endpoint(
    payload: AvailabilityRuleCreate, db: AsyncSession = Depends(get_db)
):
    rule = await create_rule(db, payload=payload.model_dump())
    return {"rule_id": rule.rule_id}


@router.get("/rules/{rule_id}")
async def get_rule_endpoint(rule_id: int, db: AsyncSession = Depends(get_db)):
    rule = await get_rule(db, rule_id=rule_id)
    return rule


@router.get("/rules")
async def list_rules_endpoint(provider_id: int, db: AsyncSession = Depends(get_db)):
    return await list_rules(db, provider_id=provider_id)


@router.patch("/rules/{rule_id}")
async def update_rule_endpoint(
    rule_id: int, payload: AvailabilityRuleUpdate, db: AsyncSession = Depends(get_db)
):
    rule = await update_rule(db, rule_id=rule_id, payload=payload.model_dump(exclude_unset=True))
    return rule


@router.delete("/rules/{rule_id}")
async def delete_rule_endpoint(rule_id: int, db: AsyncSession = Depends(get_db)):
    await delete_rule(db, rule_id=rule_id)
    return {"deleted": True}


@router.post("/overrides")
async def create_override_endpoint(
    payload: AvailabilityOverrideCreate, db: AsyncSession = Depends(get_db)
):
    override = await create_override(db, payload=payload.model_dump())
    return {"override_id": override.override_id}


@router.get("/overrides/{override_id}")
async def get_override_endpoint(override_id: int, db: AsyncSession = Depends(get_db)):
    override = await get_override(db, override_id=override_id)
    return override


@router.get("/overrides")
async def list_overrides_endpoint(provider_id: int, db: AsyncSession = Depends(get_db)):
    return await list_overrides(db, provider_id=provider_id)


@router.patch("/overrides/{override_id}")
async def update_override_endpoint(
    override_id: int, payload: AvailabilityOverrideUpdate, db: AsyncSession = Depends(get_db)
):
    override = await update_override(
        db, override_id=override_id, payload=payload.model_dump(exclude_unset=True)
    )
    return override


@router.delete("/overrides/{override_id}")
async def delete_override_endpoint(override_id: int, db: AsyncSession = Depends(get_db)):
    await delete_override(db, override_id=override_id)
    return {"deleted": True}


@router.post("/time-off")
async def create_time_off_endpoint(
    payload: TimeOffCreate, db: AsyncSession = Depends(get_db)
):
    time_off = await create_time_off(db, payload=payload.model_dump())
    return {"time_off_id": time_off.time_off_id}


@router.get("/time-off/{time_off_id}")
async def get_time_off_endpoint(time_off_id: int, db: AsyncSession = Depends(get_db)):
    time_off = await get_time_off(db, time_off_id=time_off_id)
    return time_off


@router.get("/time-off")
async def list_time_off_endpoint(provider_id: int, db: AsyncSession = Depends(get_db)):
    return await list_time_off(db, provider_id=provider_id)


@router.patch("/time-off/{time_off_id}")
async def update_time_off_endpoint(
    time_off_id: int, payload: TimeOffUpdate, db: AsyncSession = Depends(get_db)
):
    time_off = await update_time_off(
        db, time_off_id=time_off_id, payload=payload.model_dump(exclude_unset=True)
    )
    return time_off


@router.delete("/time-off/{time_off_id}")
async def delete_time_off_endpoint(time_off_id: int, db: AsyncSession = Depends(get_db)):
    await delete_time_off(db, time_off_id=time_off_id)
    return {"deleted": True}


@router.post("/check")
async def availability_check(
    payload: AvailabilityCheckRequest, db: AsyncSession = Depends(get_db)
):
    available = await is_provider_available(
        db,
        provider_id=payload.provider_id,
        service_type_id=payload.service_type_id,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        requested_units=payload.requested_units,
    )
    return {"available": available}


@router.get("/calendar", response_model=ProviderCalendarOut)
async def provider_calendar_endpoint(
    provider_id: int,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
) -> ProviderCalendarOut:
    data = await get_provider_calendar(
        db, provider_id=provider_id, start_date=start_date, end_date=end_date
    )
    return ProviderCalendarOut(
        bookings=[
            {
                "booking_id": b.booking_id,
                "service_type_id": b.service_type_id,
                "status": b.status,
                "start_datetime": b.start_datetime,
                "end_datetime": b.end_datetime,
            }
            for b in data["bookings"]
        ],
        time_off=[
            {
                "time_off_id": t.time_off_id,
                "start_datetime": t.start_datetime,
                "end_datetime": t.end_datetime,
                "reason": t.reason,
            }
            for t in data["time_off"]
        ],
        overrides=[
            {
                "override_id": o.override_id,
                "date": o.date,
                "service_type_id": o.service_type_id,
                "is_available": o.is_available,
                "capacity": o.capacity,
                "note": o.note,
            }
            for o in data["overrides"]
        ],
    )
