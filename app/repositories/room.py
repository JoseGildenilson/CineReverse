from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room, Seat


async def get_all(db: AsyncSession) -> list[Room]:
    result = await db.execute(select(Room))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, room_id: int) -> Room | None:
    result = await db.execute(select(Room).where(Room.id == room_id))
    return result.scalar_one_or_none()


async def get_seats_by_room(db: AsyncSession, room_id: int) -> list[Seat]:
    result = await db.execute(select(Seat).where(Seat.room_id == room_id))
    return result.scalars().all()


async def create_room_with_seats(
    db: AsyncSession, name: str, rows: int, seats_per_row: int
) -> Room:
    total_seats = rows * seats_per_row
    room = Room(name=name, total_seats=total_seats)
    db.add(room)
    await db.flush()  # gera o room.id sem commitar ainda

    # gera as letras das fileiras: A, B, C...
    for row_index in range(rows):
        row_letter = chr(65 + row_index)  # 65 = ord('A')
        for seat_number in range(1, seats_per_row + 1):
            seat = Seat(room_id=room.id, row=row_letter, number=seat_number)
            db.add(seat)

    await db.commit()
    await db.refresh(room)
    return room