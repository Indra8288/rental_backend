from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.session import Base

class RoomNote(Base):
    __tablename__ = "room_note"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_no: Mapped[str] = mapped_column(String(20), ForeignKey("room.room_no"), index=True, nullable=False)
    note: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    room = relationship("Room", back_populates="notes")
