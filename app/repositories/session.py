from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


async def get_all(db: AsyncSession, skip: int, limit: int) -> list[Session]:
    result = await db.execute(select(Session).offset(skip).limit(limit))
    return result.scalars().all()


async def count(db: AsyncSession) -> int:
    from sqlalchemy import func
    result = await db.execute(select(func.count()).select_from(Session))
    return result.scalar_one()


async def get_by_id(db: AsyncSession, session_id: int) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def get_by_movie(db: AsyncSession, movie_id: int, skip: int, limit: int) -> list[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.movie_id == movie_id)
        .offset(skip).limit(limit)
    )
    return result.scalars().all()


async def count_by_movie(db: AsyncSession, movie_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(
        select(func.count()).select_from(Session).where(Session.movie_id == movie_id)
    )
    return result.scalar_one()


async def create(db: AsyncSession, movie_id: int, room_id: int, starts_at) -> Session:
    session = Session(movie_id=movie_id, room_id=room_id, starts_at=starts_at)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session