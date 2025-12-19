from __future__ import annotations
from typing import Optional
from datetime import date
from sqlalchemy import String, Float, Date, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Room(Base):
    __tablename__ = "room"
    __table_args__ = (UniqueConstraint("house_id", "room_no", name="uq_room_house_roomno"),)

    room_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    house_id: Mapped[int] = mapped_column(Integer, ForeignKey("house.house_id"), index=True, nullable=False)

    room_no: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    status: Mapped[str] = mapped_column(String(20), default="EMPTY", nullable=False)
    debt: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_bom: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    house = relationship("House", back_populates="rooms")
    customers = relationship("Customer", back_populates="room")
    payments = relationship("RoomPayment", back_populates="room")
    electrics = relationship("Electric", back_populates="room")
    waters = relationship("Water", back_populates="room")
    notes = relationship("RoomNote", back_populates="room")
    logins = relationship("UserLogin", back_populates="room")
