from sqlalchemy import String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Electric(Base):
    __tablename__ = "electric"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_no: Mapped[str] = mapped_column(String(20), ForeignKey("room.room_no"), index=True, nullable=False)
    current_num: Mapped[int] = mapped_column(Integer, nullable=False)
    report_date: Mapped[Date] = mapped_column(Date, nullable=False)
    date_key: Mapped[str] = mapped_column(String(7), index=True, nullable=False)  # YYYY-MM
    price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    room = relationship("Room", back_populates="electrics")
