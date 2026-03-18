from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import session as session_repo
from app.repositories import movie as movie_repo
from app.repositories import room as room_repo
from app.schemas.session import SessionCreate, SessionResponse


async def list_sessions(db: AsyncSession, page: int, page_size: int) -> dict:
    skip = (page - 1) * page_size
    sessions = await session_repo.get_all(db, skip=skip, limit=page_size)
    total = await session_repo.count(db)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [SessionResponse.model_validate(s) for s in sessions],
    }


async def list_sessions_by_movie(
    db: AsyncSession, movie_id: int, page: int, page_size: int
) -> dict:
    movie = await movie_repo.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    skip = (page - 1) * page_size
    sessions = await session_repo.get_by_movie(db, movie_id, skip=skip, limit=page_size)
    total = await session_repo.count_by_movie(db, movie_id)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [SessionResponse.model_validate(s) for s in sessions],
    }


async def create_session(db: AsyncSession, data: SessionCreate) -> SessionResponse:
    movie = await movie_repo.get_by_id(db, data.movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    room = await room_repo.get_by_id(db, data.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    session = await session_repo.create(db, data.movie_id, data.room_id, data.starts_at)
    return SessionResponse.model_validate(session)