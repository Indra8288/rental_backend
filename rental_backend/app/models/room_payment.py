from sqlalchemy import String, Float, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.enums import PaymentType, PaymentStatus

class RoomPayment(Base):
    __tablename__ = "room_payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_no: Mapped[str] = mapped_column(String(20), ForeignKey("room.room_no"), index=True, nullable=False)
    total_payment: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_water: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_elect: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    remaining: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), default=PaymentType.full.value, nullable=False)
    date_key: Mapped[str] = mapped_column(String(7), index=True, nullable=False)  # YYYY-MM

    # Needed for UI: "Pending accept"
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.accepted.value, nullable=False)

    # For partial pay promise
    promise_date: Mapped[Date | None] = mapped_column(Date, nullable=True)

    room = relationship("Room", back_populates="payments")
