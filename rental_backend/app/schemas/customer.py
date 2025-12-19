from datetime import date
from app.schemas.common import APIModel

class CustomerCreate(APIModel):
    name: str
    phone_no: str
    dob: date | None = None
    room_no: str
    start_date: date
    telegram: str | None = None
    remark: str | None = None
    id_link: str | None = None
    status: str = "Active"

class CustomerOut(APIModel):
    cust_id: int
    name: str
    dob: date | None
    house_id: int
    room_id: str
    start_date: date
    phone_no: str
    telegram: str | None
    status: str
    remark: str | None
    id_link: str | None
