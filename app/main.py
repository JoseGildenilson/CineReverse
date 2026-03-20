from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.routers import user as user_router
from app.routers import movie as movie_router
from app.routers import room as room_router
from app.routers import session as session_router
from app.routers import seat_map as seat_map_router
from app.routers import reservation as reservation_router
from app.routers import ticket as ticket_router


app = FastAPI(
    title="CineReserve API",
    debug=settings.debug,
)

app.include_router(user_router.router)
app.include_router(movie_router.router)
app.include_router(room_router.router)
app.include_router(session_router.router)
app.include_router(seat_map_router.router)
app.include_router(reservation_router.router)
app.include_router(ticket_router.router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="CineReserve API",
        version="1.0.0",
        description="""
## 🎬 CineReserve API

Backend do sistema de reservas do **Cinépolis Natal**.

### Fluxo principal

1. **Cadastro/Login** → obtenha seu token JWT
2. **Filmes** → explore os filmes disponíveis
3. **Sessões** → veja os horários de um filme
4. **Mapa de assentos** → visualize assentos disponíveis, reservados e comprados
5. **Reserva** → bloqueie temporariamente um assento (10 minutos)
6. **Checkout** → confirme sua reserva e gere seu ticket
7. **Meus tickets** → acesse todos os seus ingressos

### Autenticação

Use o botão **Authorize** acima e insira seu token no formato:
```
Bearer <seu_token>
```
        """,
        routes=app.routes,
    )

    schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi