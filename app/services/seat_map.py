from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import seat_map as seat_map_repo
from app.repositories import room as room_repo
from app.schemas.seat_map import SeatMapItem, SeatMapResponse, SeatStatus
import redis.asyncio as aioredis


async def get_seat_map(db: AsyncSession, session_id: int) -> SeatMapResponse:
    session = await seat_map_repo.get_session_with_room(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    room = await room_repo.get_by_id(db, session.room_id)
    seats = await seat_map_repo.get_seats_by_room(db, session.room_id)
    purchased_ids = await seat_map_repo.get_purchased_seat_ids(db, session_id)

    # busca assentos temporariamente reservados no Redis
    redis = aioredis.from_url(settings.redis_url)
    reserved_ids = set()
    for seat in seats:
        lock_key = f"seat_lock:{session_id}:{seat.id}"
        is_locked = await redis.exists(lock_key)
        if is_locked:
            reserved_ids.add(seat.id)
    await redis.aclose()

    items = []
    for seat in seats:
        if seat.id in purchased_ids:
            seat_status = SeatStatus.purchased
        elif seat.id in reserved_ids:
            seat_status = SeatStatus.reserved
        else:
            seat_status = SeatStatus.available

        items.append(SeatMapItem(
            seat_id=seat.id,
            row=seat.row,
            number=seat.number,
            status=seat_status,
        ))

    # ordena por fileira e número
    items.sort(key=lambda s: (s.row, s.number))

    return SeatMapResponse(
        session_id=session_id,
        room_name=room.name,
        seats=items,
    )