from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.customer import Customer
from app.models.room import Room
from app.models.enums import RoomStatus, CustomerStatus

def get_customer(db: Session, cust_id: int) -> Customer:
    c = db.get(Customer, cust_id)
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    return c

def list_customers(db: Session, status: str | None = None) -> list[Customer]:
    q = db.query(Customer)
    if status:
        q = q.filter(Customer.status == status)
    return q.order_by(Customer.cust_id.desc()).all()

def create_customer(db: Session, *, obj: Customer) -> Customer:
    room = db.get(Room, obj.room_no)
    if not room:
        raise HTTPException(status_code=400, detail="Room not found")
    if room.status != RoomStatus.empty.value:
        raise HTTPException(status_code=400, detail="Room is not empty")
    db.add(obj)
    room.status = RoomStatus.occupied.value
    db.commit()
    db.refresh(obj)
    return obj

def update_customer(db: Session, cust: Customer, patch: dict) -> Customer:
    for k, v in patch.items():
        setattr(cust, k, v)
    db.commit()
    db.refresh(cust)
    return cust
