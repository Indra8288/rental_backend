from __future__ import annotations
from typing import Optional
from datetime import date
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Customer(Base):
    __tablename__ = "customer"

    cust_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    house_id: Mapped[int] = mapped_column(Integer, ForeignKey("house.house_id"), index=True, nullable=False)
    room_id: Mapped[str] = mapped_column(String(64), ForeignKey("room.room_id"), index=True, nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)

    remark: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    id_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    room = relationship("Room", back_populates="customers")
    house = relationship("House")
