from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieResponse
from app.services import movie as movie_service

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=dict)
async def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await movie_service.list_movies(db, page, page_size)


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await movie_service.get_movie(db, movie_id)


@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(
    data: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await movie_service.create_movie(db, data)