import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import seat_map as seat_map_repo
from app.repositories import room as room_repo
from app.schemas.reservation import ReservationCreate, ReservationResponse

LOCK_EXPIRE_SECONDS = 600  # 10 minutos


def _lock_key(session_id: int, seat_id: int) -> str:
    return f"seat_lock:{session_id}:{seat_id}"


async def reserve_seat(
    db: AsyncSession, data: ReservationCreate, user_id: int
) -> ReservationResponse:
    # verifica se a sessão existe
    session = await seat_map_repo.get_session_with_room(db, data.session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # verifica se o assento pertence à sala da sessão
    seats = await room_repo.get_seats_by_room(db, session.room_id)
    seat_ids = {s.id for s in seats}
    if data.seat_id not in seat_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat not found in this session")

    # verifica se já foi comprado
    purchased_ids = await seat_map_repo.get_purchased_seat_ids(db, data.session_id)
    if data.seat_id in purchased_ids:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat already purchased")

    # tenta adquirir o lock no Redis
    redis = aioredis.from_url(settings.redis_url)
    key = _lock_key(data.session_id, data.seat_id)

    # NX = só seta se não existir (operação atômica)
    acquired = await redis.set(key, user_id, ex=LOCK_EXPIRE_SECONDS, nx=True)
    await redis.aclose()

    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat is already reserved by another user",
        )

    return ReservationResponse(
        session_id=data.session_id,
        seat_id=data.seat_id,
        message="Seat reserved successfully. You have 10 minutes to complete checkout.",
        expires_in_seconds=LOCK_EXPIRE_SECONDS,
    )


async def release_seat(session_id: int, seat_id: int, user_id: int) -> dict:
    redis = aioredis.from_url(settings.redis_url)
    key = _lock_key(session_id, seat_id)

    owner = await redis.get(key)
    if not owner or int(owner) != user_id:
        await redis.aclose()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this reservation",
        )

    await redis.delete(key)
    await redis.aclose()
    return {"message": "Reservation released successfully"}