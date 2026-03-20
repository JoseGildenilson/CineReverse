from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services import reservation as reservation_service

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationResponse, status_code=201)
async def reserve_seat(
    data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await reservation_service.reserve_seat(db, data, current_user.id)


@router.delete("/{session_id}/{seat_id}", response_model=dict)
async def release_seat(
    session_id: int,
    seat_id: int,
    current_user: User = Depends(get_current_user),
):
    return await reservation_service.release_seat(session_id, seat_id, current_user.id)