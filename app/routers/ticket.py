from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.ticket import CheckoutCreate, TicketResponse
from app.services import ticket as ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/checkout", response_model=TicketResponse, status_code=201)
async def checkout(
    data: CheckoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ticket_service.checkout(db, data, current_user.id)


@router.get("/me", response_model=dict)
async def my_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ticket_service.list_my_tickets(db, current_user.id, page, page_size)