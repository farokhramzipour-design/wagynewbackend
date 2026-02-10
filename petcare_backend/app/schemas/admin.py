from pydantic import BaseModel


class AdminStatusUpdate(BaseModel):
    status: str


class AdminBookingDispute(BaseModel):
    actor_user_id: int | None = None
    payload_json: dict | None = None
