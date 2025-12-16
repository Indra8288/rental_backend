from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.session import Base
from app.models.enums import IssueType, IssueStatus

class IssueTicket(Base):
    __tablename__ = "issue_ticket"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_no: Mapped[str] = mapped_column(String(20), ForeignKey("room.room_no"), index=True, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_login.id"), nullable=False)

    issue_type: Mapped[str] = mapped_column(String(50), default=IssueType.other.value, nullable=False)
    details: Mapped[str] = mapped_column(String(2000), nullable=False)

    # ✅ new default
    status: Mapped[str] = mapped_column(String(20), default=IssueStatus.opening.value, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("UserLogin")
