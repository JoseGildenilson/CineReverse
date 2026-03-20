from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.models.session import Session
from app.models.movie import Movie
from app.models.room import Room, Seat


async def get_by_session_and_seat(
    db: AsyncSession, session_id: int, seat_id: int
) -> Ticket | None:
    result = await db.execute(
        select(Ticket).where(
            Ticket.session_id == session_id,
            Ticket.seat_id == seat_id,
        )
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession, user_id: int, session_id: int, seat_id: int, code: str
) -> Ticket:
    ticket = Ticket(
        user_id=user_id,
        session_id=session_id,
        seat_id=seat_id,
        code=code,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def get_by_user(db: AsyncSession, user_id: int, skip: int, limit: int) -> list[Ticket]:
    result = await db.execute(
        select(Ticket).where(Ticket.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def count_by_user(db: AsyncSession, user_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(
        select(func.count()).select_from(Ticket).where(Ticket.user_id == user_id)
    )
    return result.scalar_one()


async def get_ticket_details(db: AsyncSession, ticket: Ticket) -> dict:
    session = await db.get(Session, ticket.session_id)
    movie = await db.get(Movie, session.movie_id)
    room = await db.get(Room, session.room_id)
    seat = await db.get(Seat, ticket.seat_id)

    return {
        "id": ticket.id,
        "code": ticket.code,
        "session_id": ticket.session_id,
        "seat_id": ticket.seat_id,
        "purchased_at": ticket.purchased_at,
        "movie_title": movie.title,
        "room_name": room.name,
        "seat_row": seat.row,
        "seat_number": seat.number,
        "starts_at": session.starts_at,
    }