from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import movie as movie_repo
from app.schemas.movie import MovieCreate, MovieResponse


async def list_movies(db: AsyncSession, page: int, page_size: int) -> dict:
    skip = (page - 1) * page_size
    movies = await movie_repo.get_all(db, skip=skip, limit=page_size)
    total = await movie_repo.count(db)

    items = []
    for movie in movies:
        available_seats = await movie_repo.count_available_seats(db, movie.id)
        sessions = await movie_repo.has_sessions(db, movie.id)
        items.append(MovieResponse(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            duration_minutes=movie.duration_minutes,
            banner_url=movie.banner_url,
            has_sessions=sessions,
            available_seats=available_seats,
        ))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


async def create_movie(db: AsyncSession, data: MovieCreate) -> MovieResponse:
    movie = await movie_repo.create(
        db,
        title=data.title,
        description=data.description,
        duration_minutes=data.duration_minutes,
        banner_url=data.banner_url,
    )
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        duration_minutes=movie.duration_minutes,
        banner_url=movie.banner_url,
        has_sessions=False,
        available_seats=0,
    )


async def get_movie(db: AsyncSession, movie_id: int) -> MovieResponse:
    movie = await movie_repo.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    available_seats = await movie_repo.count_available_seats(db, movie_id)
    sessions = await movie_repo.has_sessions(db, movie_id)

    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        duration_minutes=movie.duration_minutes,
        banner_url=movie.banner_url,
        has_sessions=sessions,
        available_seats=available_seats,
    )