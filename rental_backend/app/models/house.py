from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class House(Base):
    __tablename__ = "house"

    house_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    house_name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_login.id"), nullable=False)

    owner = relationship("UserLogin", back_populates="owned_houses", foreign_keys=[owner_id])
    rooms = relationship("Room", back_populates="house")
