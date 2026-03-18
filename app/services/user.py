from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import user as user_repo
from app.schemas.user import TokenResponse, UserRegister


async def register(db: AsyncSession, data: UserRegister) -> TokenResponse:
    existing = await user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed = hash_password(data.password)
    user = await user_repo.create(db, data.email, data.username, hashed)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    user = await user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)