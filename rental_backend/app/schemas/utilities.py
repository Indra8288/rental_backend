from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import APIModel

class ElectricCreate(BaseModel):
    room_id: str
    current_num: int = Field(ge=0)
    price_khr: float = 0.0

class WaterCreate(BaseModel):
    room_id: str
    current_num: int = Field(ge=0)

class UtilityOut(APIModel):
    id: int
    room_id: str
    current_num: int
    report_date: date
    date_key: str
    price_khr: float
