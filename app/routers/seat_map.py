from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.seat_map import SeatMapResponse
from app.services import seat_map as seat_map_service

router = APIRouter(prefix="/sessions", tags=["Seat Map"])


@router.get("/{session_id}/seats", response_model=SeatMapResponse)
async def get_seat_map(session_id: int, db: AsyncSession = Depends(get_db)):
    return await seat_map_service.get_seat_map(db, session_id)