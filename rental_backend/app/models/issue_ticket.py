from __future__ import annotations
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class IssueTicket(Base):
    __tablename__ = "issue_ticket"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[str] = mapped_column(String(64), ForeignKey("room.room_id"), index=True, nullable=False)
    house_id: Mapped[int] = mapped_column(Integer, ForeignKey("house.house_id"), index=True, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_login.id"), nullable=False)

    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPENING", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("UserLogin", foreign_keys=[created_by_user_id])
    room = relationship("Room")
    house = relationship("House")
