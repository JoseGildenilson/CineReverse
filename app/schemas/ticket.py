from datetime import datetime
from pydantic import BaseModel


class CheckoutCreate(BaseModel):
    session_id: int
    seat_id: int


class TicketResponse(BaseModel):
    id: int
    code: str
    session_id: int
    seat_id: int
    purchased_at: datetime
    movie_title: str
    room_name: str
    seat_row: str
    seat_number: int
    starts_at: datetime

    model_config = {"from_attributes": True}