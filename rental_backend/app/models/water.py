from __future__ import annotations
from datetime import date
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Water(Base):
    __tablename__ = "water"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[str] = mapped_column(String(64), ForeignKey("room.room_id"), index=True, nullable=False)
    current_num: Mapped[int] = mapped_column(Integer, nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    date_key: Mapped[str] = mapped_column(String(7), index=True, nullable=False)
    price_khr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    room = relationship("Room", back_populates="waters")
