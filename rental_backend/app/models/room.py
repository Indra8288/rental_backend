from sqlalchemy import String, Float, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.enums import RoomStatus

class Room(Base):
    __tablename__ = "room"

    room_no: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=RoomStatus.empty.value, nullable=False)
    debt: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_bom: Mapped[Date | None] = mapped_column(Date, nullable=True)  # last end-of-month date

    customers = relationship("Customer", back_populates="room")
    payments = relationship("RoomPayment", back_populates="room")
    electrics = relationship("Electric", back_populates="room")
    waters = relationship("Water", back_populates="room")
    logins = relationship("UserLogin", back_populates="room")
    notes = relationship("RoomNote", back_populates="room")
