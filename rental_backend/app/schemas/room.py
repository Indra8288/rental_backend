from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import APIModel

class RoomCreate(BaseModel):
    room_no: str = Field(min_length=1, max_length=20)
    price: float
    price_usd: float

class RoomOut(APIModel):
    room_no: str
    price: float
    status: str
    debt: float
    price_usd: float
    last_bom: date | None = None

class RoomStatusCard(BaseModel):
    room_no: str
    color: str  # green/blue/white/red
    status_text: str
    debt: float
    remaining: float

class RoomBillInfo(APIModel):
    room_no: str
    room_price_usd: float

    previous_month_water: int | None
    current_month_water: int | None
    total_water_usage: int
    total_water_price_khr: float

    previous_month_electricity: int | None
    current_month_electricity: int | None
    total_electricity_price_khr: float

    total_usd: float
    total_khr: float
