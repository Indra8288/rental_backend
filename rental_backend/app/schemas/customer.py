from datetime import date
from pydantic import BaseModel, Field
from app.schemas.common import APIModel

class CustomerCreate(BaseModel):
    name: str
    phone_no: str
    dob: date | None = None
    room_no: str
    start_date: date
    telegram: str | None = None
    remark: str | None = None

    # Payment status at registration
    payment_fully_paid: bool = True
    partial_amount: float | None = None
    note: str | None = None

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_no: str | None = None
    dob: date | None = None
    telegram: str | None = None
    remark: str | None = None
    status: str | None = None
    room_no: str | None = None

class CustomerOut(APIModel):
    cust_id: int
    name: str
    dob: date | None = None
    room_no: str
    start_date: date
    phone_no: str
    remark: str | None = None
    id_link: str | None = None
    telegram: str | None = None
    status: str
