from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import APIModel

class PaymentCreate(BaseModel):
    date_key: str
    amount_usd: float = Field(gt=0)
    payment_date: date

class PartlyPayCreate(BaseModel):
    date_key: str
    amount_usd: float = Field(gt=0)
    payment_date: date
    promise_date: date

class PaymentAccept(BaseModel):
    date_key: str

class RoomPaymentOut(APIModel):
    id: int
    room_id: str
    total_payment_usd: float
    remaining_usd: float
    total_water_khr: float
    total_elect_khr: float
    payment_type: str
    status: str
    date_key: str
    payment_date: date | None = None
    promise_date: date | None = None
