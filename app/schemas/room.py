from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    rows: int        # quantidade de fileiras ex: 5
    seats_per_row: int  # assentos por fileira ex: 10


class SeatResponse(BaseModel):
    id: int
    row: str
    number: int

    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    id: int
    name: str
    total_seats: int
    seats: list[SeatResponse] = []

    model_config = {"from_attributes": True}