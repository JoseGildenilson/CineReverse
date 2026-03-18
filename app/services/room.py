from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import room as room_repo
from app.schemas.room import RoomCreate, RoomResponse, SeatResponse


async def list_rooms(db: AsyncSession) -> list[RoomResponse]:
    rooms = await room_repo.get_all(db)
    return [RoomResponse(
        id=r.id,
        name=r.name,
        total_seats=r.total_seats,
    ) for r in rooms]


async def get_room(db: AsyncSession, room_id: int) -> RoomResponse:
    room = await room_repo.get_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    seats = await room_repo.get_seats_by_room(db, room_id)
    return RoomResponse(
        id=room.id,
        name=room.name,
        total_seats=room.total_seats,
        seats=[SeatResponse(id=s.id, row=s.row, number=s.number) for s in seats],
    )


async def create_room(db: AsyncSession, data: RoomCreate) -> RoomResponse:
    room = await room_repo.create_room_with_seats(
        db,
        name=data.name,
        rows=data.rows,
        seats_per_row=data.seats_per_row,
    )
    seats = await room_repo.get_seats_by_room(db, room.id)
    return RoomResponse(
        id=room.id,
        name=room.name,
        total_seats=room.total_seats,
        seats=[SeatResponse(id=s.id, row=s.row, number=s.number) for s in seats],
    )