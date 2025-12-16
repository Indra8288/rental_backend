from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.room_payment import RoomPayment
from app.models.room import Room
from app.models.enums import PaymentType, PaymentStatus

def get_payment(db: Session, room_no: str, date_key: str) -> RoomPayment | None:
    return db.query(RoomPayment).filter(and_(RoomPayment.room_no == room_no, RoomPayment.date_key == date_key)).first()

def ensure_payment_row(db: Session, room: Room, date_key: str) -> RoomPayment:
    rp = get_payment(db, room.room_no, date_key)
    if rp:
        return rp
    rp = RoomPayment(
        room_no=room.room_no,
        date_key=date_key,
        remaining=room.price + room.debt,
        status=PaymentStatus.opening.value,   # ✅ OPENING by default
    )
    db.add(rp)
    db.commit()
    db.refresh(rp)
    return rp

def apply_full_payment(db: Session, room: Room, date_key: str, amount: float, payment_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)
    rp.total_payment += amount
    rp.payment_date = payment_date
    rp.payment_type = PaymentType.full.value
    rp.remaining = max(0.0, rp.remaining - amount)

    # ✅ admin action puts it IN_PROGRESS (not accepted yet)
    rp.status = PaymentStatus.in_progress.value

    room.debt = rp.remaining
    db.commit()
    db.refresh(rp)
    return rp

def apply_partial_payment(db: Session, room: Room, date_key: str, amount: float, payment_date: date, promise_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)
    rp.total_payment += amount
    rp.payment_date = payment_date
    rp.payment_type = PaymentType.partial.value
    rp.promise_date = promise_date
    rp.remaining = max(0.0, rp.remaining - amount)

    # ✅ partial also IN_PROGRESS
    rp.status = PaymentStatus.in_progress.value

    room.debt = rp.remaining
    db.commit()
    db.refresh(rp)
    return rp

def accept_payment(db: Session, room_no: str, date_key: str) -> RoomPayment:
    rp = get_payment(db, room_no, date_key)
    if not rp:
        raise HTTPException(status_code=404, detail="Payment record not found")

    # ✅ only accept when fully settled
    if rp.remaining != 0:
        raise HTTPException(status_code=400, detail="Cannot accept: remaining must be 0")

    rp.status = PaymentStatus.accepted.value
    db.commit()
    db.refresh(rp)
    return rp
