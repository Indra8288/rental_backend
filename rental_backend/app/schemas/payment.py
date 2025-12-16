from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import APIModel
from app.models.enums import PaymentType, PaymentStatus

class PaymentCreate(BaseModel):
    date_key: str  # YYYY-MM
    amount: float = Field(gt=0)
    payment_date: date

class PartlyPayCreate(BaseModel):
    date_key: str
    amount: float = Field(gt=0)
    payment_date: date
    promise_date: date

class PaymentAccept(BaseModel):
    date_key: str

class RoomPaymentOut(APIModel):
    id: int
    room_no: str
    total_payment: float
    total_water: float
    total_elect: float
    payment_date: date | None = None
    remaining: float
    payment_type: str
    date_key: str
    status: str
    promise_date: date | None = None
