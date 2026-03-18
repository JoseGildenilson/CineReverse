from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse
from app.services import session as session_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=dict)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await session_service.list_sessions(db, page, page_size)


@router.get("/movie/{movie_id}", response_model=dict)
async def list_sessions_by_movie(
    movie_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await session_service.list_sessions_by_movie(db, movie_id, page, page_size)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    from app.repositories import session as session_repo
    from fastapi import HTTPException
    s = await session_repo.get_by_id(db, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(s)


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.create_session(db, data)