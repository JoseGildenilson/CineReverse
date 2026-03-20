from enum import Enum
from pydantic import BaseModel


class SeatStatus(str, Enum):
    available = "available"
    reserved = "reserved"
    purchased = "purchased"


class SeatMapItem(BaseModel):
    seat_id: int
    row: str
    number: int
    status: SeatStatus


class SeatMapResponse(BaseModel):
    session_id: int
    room_name: str
    seats: list[SeatMapItem]