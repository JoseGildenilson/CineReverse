from pydantic import BaseModel


class ReservationCreate(BaseModel):
    session_id: int
    seat_id: int


class ReservationResponse(BaseModel):
    session_id: int
    seat_id: int
    message: str
    expires_in_seconds: int