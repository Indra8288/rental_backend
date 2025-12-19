from datetime import date
from app.schemas.common import APIModel

class RoomCreate(APIModel):
    room_no: str
    price_usd: float

class RoomOut(APIModel):
    room_id: str
    house_id: int
    room_no: str
    price_usd: float
    status: str
    debt: float
    last_bom: date | None = None

class RoomStatusCard(APIModel):
    room_id: str
    room_no: str
    color: str
    status_text: str
    remaining_usd: float

class RoomBillInfo(APIModel):
    room_id: str
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

class RoomUpdate(APIModel):
    price_usd: float | None = None
    status: str | None = None
