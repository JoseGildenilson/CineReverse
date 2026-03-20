from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Seat
from app.models.session import Session
from app.models.ticket import Ticket


async def get_session_with_room(db: AsyncSession, session_id: int) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def get_seats_by_room(db: AsyncSession, room_id: int) -> list[Seat]:
    result = await db.execute(select(Seat).where(Seat.room_id == room_id))
    return result.scalars().all()


async def get_purchased_seat_ids(db: AsyncSession, session_id: int) -> set[int]:
    result = await db.execute(
        select(Ticket.seat_id).where(Ticket.session_id == session_id)
    )
    return set(result.scalars().all())