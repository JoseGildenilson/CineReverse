from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)

    seats = relationship("Seat", back_populates="room")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    row = Column(String, nullable=False)    # ex: "A", "B", "C"
    number = Column(Integer, nullable=False) # ex: 1, 2, 3

    room = relationship("Room", back_populates="seats")