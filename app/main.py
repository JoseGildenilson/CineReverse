from fastapi import FastAPI

from app.core.config import settings
from app.routers import user as user_router
from app.routers import movie as movie_router
from app.routers import room as room_router
from app.routers import session as session_router

app = FastAPI(
    title="CineReserve API",
    debug=settings.debug,
)

app.include_router(user_router.router)
app.include_router(movie_router.router)
app.include_router(room_router.router)
app.include_router(session_router.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}