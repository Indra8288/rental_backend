from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class UserLogin(Base):
    __tablename__ = "user_login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    pass_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    house_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("house.house_id"), nullable=True)
    room_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("room.room_id"), nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customer.cust_id"), nullable=True)

    house = relationship("House", foreign_keys=[house_id])
    room = relationship("Room", back_populates="logins", foreign_keys=[room_id])
    customer = relationship("Customer", foreign_keys=[customer_id])

    owned_houses = relationship("House", back_populates="owner", foreign_keys="House.owner_id")
