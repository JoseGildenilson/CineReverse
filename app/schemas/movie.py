from pydantic import BaseModel


class MovieCreate(BaseModel):
    title: str
    description: str | None = None
    duration_minutes: int
    banner_url: str | None = None


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str | None
    duration_minutes: int
    banner_url: str | None
    has_sessions: bool = False
    available_seats: int = 0

    model_config = {"from_attributes": True}