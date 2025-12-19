from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.room_payment import RoomPayment
from app.models.room import Room
from app.models.enums import PaymentType, PaymentStatus

def get_payment(db: Session, room_id: str, date_key: str) -> RoomPayment | None:
    return db.query(RoomPayment).filter(and_(RoomPayment.room_id == room_id, RoomPayment.date_key == date_key)).first()

def ensure_payment_row(db: Session, room: Room, date_key: str) -> RoomPayment:
    rp = get_payment(db, room.room_id, date_key)
    if rp:
        return rp
    rp = RoomPayment(room_id=room.room_id, date_key=date_key,
                     remaining_usd=float(room.price_usd + room.debt),
                     status=PaymentStatus.opening.value,
                     payment_type=PaymentType.full.value)
    db.add(rp)
    db.commit()
    db.refresh(rp)
    return rp

def apply_full_payment(db: Session, room: Room, date_key: str, amount_usd: float, payment_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)
    rp.total_payment_usd += amount_usd
    rp.payment_date = payment_date
    rp.payment_type = PaymentType.full.value
    rp.remaining_usd = max(0.0, rp.remaining_usd - amount_usd)
    rp.status = PaymentStatus.in_progress.value
    room.debt = rp.remaining_usd
    db.commit()
    db.refresh(rp)
    return rp

def apply_partial_payment(db: Session, room: Room, date_key: str, amount_usd: float, payment_date: date, promise_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)
    rp.total_payment_usd += amount_usd
    rp.payment_date = payment_date
    rp.promise_date = promise_date
    rp.payment_type = PaymentType.partial.value
    rp.remaining_usd = max(0.0, rp.remaining_usd - amount_usd)
    rp.status = PaymentStatus.in_progress.value
    room.debt = rp.remaining_usd
    db.commit()
    db.refresh(rp)
    return rp

def accept_payment(db: Session, room: Room, date_key: str) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)
    if rp.remaining_usd != 0:
        raise HTTPException(status_code=400, detail="Cannot accept: remaining must be 0")
    rp.status = PaymentStatus.accepted.value
    room.debt = 0.0
    db.commit()
    db.refresh(rp)
    return rp
