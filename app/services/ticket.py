import uuid

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import ticket as ticket_repo
from app.repositories import seat_map as seat_map_repo
from app.schemas.ticket import CheckoutCreate, TicketResponse


def _lock_key(session_id: int, seat_id: int) -> str:
    return f"seat_lock:{session_id}:{seat_id}"


async def checkout(
    db: AsyncSession, data: CheckoutCreate, user_id: int
) -> TicketResponse:
    # verifica se a sessão existe
    session = await seat_map_repo.get_session_with_room(db, data.session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # verifica se já existe ticket para esse assento nessa sessão
    existing = await ticket_repo.get_by_session_and_seat(db, data.session_id, data.seat_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat already purchased")

    # verifica se o lock no Redis pertence ao usuário
    redis = aioredis.from_url(settings.redis_url)
    key = _lock_key(data.session_id, data.seat_id)
    owner = await redis.get(key)

    if not owner or int(owner) != user_id:
        await redis.aclose()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active reservation found for this seat. Reserve it first.",
        )

    # gera código único do ticket
    code = str(uuid.uuid4()).upper().replace("-", "")[:12]

    # cria o ticket no banco
    ticket = await ticket_repo.create(db, user_id, data.session_id, data.seat_id, code)

    # remove o lock do Redis
    await redis.delete(key)
    await redis.aclose()

    details = await ticket_repo.get_ticket_details(db, ticket)
    return TicketResponse(**details)


async def list_my_tickets(
    db: AsyncSession, user_id: int, page: int, page_size: int
) -> dict:
    skip = (page - 1) * page_size
    tickets = await ticket_repo.get_by_user(db, user_id, skip=skip, limit=page_size)
    total = await ticket_repo.count_by_user(db, user_id)

    items = []
    for ticket in tickets:
        details = await ticket_repo.get_ticket_details(db, ticket)
        items.append(TicketResponse(**details))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }