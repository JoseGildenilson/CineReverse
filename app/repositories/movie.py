from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movie import Movie
from app.models.session import Session
from app.models.ticket import Ticket
from app.models.room import Seat


async def get_all(db: AsyncSession, skip: int, limit: int) -> list[Movie]:
    result = await db.execute(select(Movie).offset(skip).limit(limit))
    return result.scalars().all()


async def count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Movie))
    return result.scalar_one()


async def get_by_id(db: AsyncSession, movie_id: int) -> Movie | None:
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, title: str, description: str | None,
                 duration_minutes: int, banner_url: str | None) -> Movie:
    movie = Movie(
        title=title,
        description=description,
        duration_minutes=duration_minutes,
        banner_url=banner_url,
    )
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


async def count_available_seats(db: AsyncSession, movie_id: int) -> int:
    # total de assentos em todas as sessões do filme
    total = await db.execute(
        select(func.count(Seat.id))
        .join(Session, Session.room_id == Seat.room_id)
        .where(Session.movie_id == movie_id)
    )
    total_seats = total.scalar_one()

    # assentos já comprados
    taken = await db.execute(
        select(func.count(Ticket.id))
        .join(Session, Ticket.session_id == Session.id)
        .where(Session.movie_id == movie_id)
    )
    taken_seats = taken.scalar_one()

    return total_seats - taken_seats


async def has_sessions(db: AsyncSession, movie_id: int) -> bool:
    result = await db.execute(
        select(func.count()).select_from(Session).where(Session.movie_id == movie_id)
    )
    return result.scalar_one() > 0