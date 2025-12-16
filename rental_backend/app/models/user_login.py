from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.session import Base
from app.models.enums import Role

class UserLogin(Base):
    __tablename__ = "user_login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    pass_hash: Mapped[str] = mapped_column("pass", String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=Role.client.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # To link client login -> customer/room for history screens
    customer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("customer.cust_id"), nullable=True)
    room_no: Mapped[str | None] = mapped_column(String(20), ForeignKey("room.room_no"), nullable=True)

    customer = relationship("Customer", back_populates="logins")
    room = relationship("Room", back_populates="logins")
