from datetime import datetime

from pydantic import BaseModel


class MeetGreetSchedule(BaseModel):
    owner_user_id: int
    provider_id: int
    scheduled_at: datetime
    location_text: str | None = None
    notes: str | None = None
    send_message: bool = False


class MeetGreetReschedule(BaseModel):
    scheduled_at: datetime
    location_text: str | None = None
    notes: str | None = None
    send_message: bool = False


class MeetGreetStatusUpdate(BaseModel):
    status: str
    send_message: bool = False


class MeetGreetOut(BaseModel):
    meet_greet_id: int
    owner_user_id: int
    provider_id: int
    scheduled_at: datetime
    status: str
    location_text: str | None = None
    notes: str | None = None
    created_at: datetime
