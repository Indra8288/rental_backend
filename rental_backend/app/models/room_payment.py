from __future__ import annotations
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class RoomPayment(Base):
    __tablename__ = "room_payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[str] = mapped_column(String(64), ForeignKey("room.room_id"), index=True, nullable=False)

    total_payment_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_water_khr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_elect_khr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    payment_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    promise_date: Mapped[Date | None] = mapped_column(Date, nullable=True)

    remaining_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), default="FULL", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPENING", nullable=False)
    date_key: Mapped[str] = mapped_column(String(7), index=True, nullable=False)

    room = relationship("Room", back_populates="payments")
