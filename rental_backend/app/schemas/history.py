from pydantic import BaseModel

class MonthlyHistoryItem(BaseModel):
    date_key: str
    room_price_paid: float
    water_paid: float
    electric_paid: float
    remaining: float

class HistoryOut(BaseModel):
    room_no: str
    items: list[MonthlyHistoryItem]
