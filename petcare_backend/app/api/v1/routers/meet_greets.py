from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.meet_greets import (
    MeetGreetOut,
    MeetGreetReschedule,
    MeetGreetSchedule,
    MeetGreetStatusUpdate,
)
from app.services.meet_greets import (
    maybe_send_meet_greet_message,
    reschedule_meet_greet,
    schedule_meet_greet,
    update_meet_greet_status,
)

router = APIRouter(prefix="/meet-greets", tags=["meet_greets"])


@router.post("/schedule", response_model=MeetGreetOut)
async def schedule_endpoint(
    payload: MeetGreetSchedule, db: AsyncSession = Depends(get_db)
) -> MeetGreetOut:
    meet = await schedule_meet_greet(db, payload=payload.model_dump())
    if payload.send_message:
        await maybe_send_meet_greet_message(db, meet=meet, status="scheduled")
    return MeetGreetOut.model_validate(meet, from_attributes=True)


@router.post("/{meet_greet_id}/reschedule", response_model=MeetGreetOut)
async def reschedule_endpoint(
    meet_greet_id: int, payload: MeetGreetReschedule, db: AsyncSession = Depends(get_db)
) -> MeetGreetOut:
    meet = await reschedule_meet_greet(db, meet_greet_id=meet_greet_id, payload=payload.model_dump())
    if payload.send_message:
        await maybe_send_meet_greet_message(db, meet=meet, status="rescheduled")
    return MeetGreetOut.model_validate(meet, from_attributes=True)


@router.post("/{meet_greet_id}/status", response_model=MeetGreetOut)
async def update_status_endpoint(
    meet_greet_id: int, payload: MeetGreetStatusUpdate, db: AsyncSession = Depends(get_db)
) -> MeetGreetOut:
    meet = await update_meet_greet_status(db, meet_greet_id=meet_greet_id, status=payload.status)
    if payload.send_message:
        await maybe_send_meet_greet_message(db, meet=meet, status=payload.status)
    return MeetGreetOut.model_validate(meet, from_attributes=True)
