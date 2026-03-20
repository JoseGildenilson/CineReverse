from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set, cache_delete_pattern
from app.repositories import session as session_repo
from app.repositories import movie as movie_repo
from app.repositories import room as room_repo
from app.schemas.session import SessionCreate, SessionResponse


async def list_sessions(db: AsyncSession, page: int, page_size: int) -> dict:
    cache_key = f"sessions:page:{page}:size:{page_size}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    skip = (page - 1) * page_size
    sessions = await session_repo.get_all(db, skip=skip, limit=page_size)
    total = await session_repo.count(db)
    result = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [SessionResponse.model_validate(s).model_dump() for s in sessions],
    }
    await cache_set(cache_key, result)
    return result


async def list_sessions_by_movie(
    db: AsyncSession, movie_id: int, page: int, page_size: int
) -> dict:
    cache_key = f"sessions:movie:{movie_id}:page:{page}:size:{page_size}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    movie = await movie_repo.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    skip = (page - 1) * page_size
    sessions = await session_repo.get_by_movie(db, movie_id, skip=skip, limit=page_size)
    total = await session_repo.count_by_movie(db, movie_id)
    result = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [SessionResponse.model_validate(s).model_dump() for s in sessions],
    }
    await cache_set(cache_key, result)
    return result


async def create_session(db: AsyncSession, data: SessionCreate) -> SessionResponse:
    movie = await movie_repo.get_by_id(db, data.movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    room = await room_repo.get_by_id(db, data.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    session = await session_repo.create(db, data.movie_id, data.room_id, data.starts_at)
    await cache_delete_pattern("sessions:*")
    await cache_delete_pattern("movies:*")
    return SessionResponse.model_validate(session)