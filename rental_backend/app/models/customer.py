from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.enums import CustomerStatus

class Customer(Base):
    __tablename__ = "customer"

    cust_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dob: Mapped[Date | None] = mapped_column(Date, nullable=True)
    room_no: Mapped[str] = mapped_column(String(20), ForeignKey("room.room_no"), nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(50), nullable=False)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    id_link: Mapped[str | None] = mapped_column(String(500), nullable=True)  # path/url to uploaded ID
    telegram: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=CustomerStatus.active.value, nullable=False)

    room = relationship("Room", back_populates="customers")
    logins = relationship("UserLogin", back_populates="customer")
