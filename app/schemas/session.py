from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    movie_id: int
    room_id: int
    starts_at: datetime


class SessionResponse(BaseModel):
    id: int
    movie_id: int
    room_id: int
    starts_at: datetime

    model_config = {"from_attributes": True}