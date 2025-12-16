from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.session import Base

class ElectricBillImage(Base):
    __tablename__ = "electric_bill_image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date_key: Mapped[str] = mapped_column(String(7), index=True, nullable=False)  # YYYY-MM
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)  # local path or URL
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
