from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.room_payment import RoomPayment
from app.models.room import Room
from app.models.enums import PaymentType, PaymentStatus

FX_RATE = 4000.0

def usd_to_khr(usd: float) -> float:
    return float(usd) * FX_RATE

def khr_to_usd(khr: float) -> float:
    return float(khr) / FX_RATE

def get_payment(db: Session, room_id: str, date_key: str) -> RoomPayment | None:
    return db.query(RoomPayment).filter(and_(RoomPayment.room_id == room_id, RoomPayment.date_key == date_key)).first()

def ensure_payment_row(db: Session, room: Room, date_key: str) -> RoomPayment:
    """
    Currency rule (v4.1):
      - water/electric/debt are calculated and stored in KHR
      - room.price_usd is converted to KHR (rate=4000) when combined

    NOTE: existing DB column names still say *_usd, but values are treated as KHR to avoid migration:
      - RoomPayment.remaining_usd      -> remaining_khr
      - RoomPayment.total_payment_usd -> paid_khr
      - Room.debt                     -> debt_khr
    """
    rp = get_payment(db, room.room_id, date_key)
    if rp:
        return rp

    remaining_khr = usd_to_khr(room.price_usd) + float(room.debt or 0.0)

    rp = RoomPayment(
        room_id=room.room_id,
        date_key=date_key,
        remaining_usd=float(remaining_khr),
        status=PaymentStatus.opening.value,
        payment_type=PaymentType.full.value,
    )
    db.add(rp)
    db.commit()
    db.refresh(rp)
    return rp

def apply_full_payment(db: Session, room: Room, date_key: str, amount_usd: float, payment_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)

    pay_khr = usd_to_khr(amount_usd)
    rp.total_payment_usd = float(rp.total_payment_usd + pay_khr)
    rp.payment_date = payment_date
    rp.payment_type = PaymentType.full.value

    rp.remaining_usd = float(max(0.0, float(rp.remaining_usd) - pay_khr))
    rp.status = PaymentStatus.in_progress.value

    room.debt = float(rp.remaining_usd)

    db.commit()
    db.refresh(rp)
    return rp

def apply_partial_payment(db: Session, room: Room, date_key: str, amount_usd: float, payment_date: date, promise_date: date) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)

    pay_khr = usd_to_khr(amount_usd)
    rp.total_payment_usd = float(rp.total_payment_usd + pay_khr)
    rp.payment_date = payment_date
    rp.promise_date = promise_date
    rp.payment_type = PaymentType.partial.value

    rp.remaining_usd = float(max(0.0, float(rp.remaining_usd) - pay_khr))
    rp.status = PaymentStatus.in_progress.value

    room.debt = float(rp.remaining_usd)

    db.commit()
    db.refresh(rp)
    return rp

def accept_payment(db: Session, room: Room, date_key: str) -> RoomPayment:
    rp = ensure_payment_row(db, room, date_key)

    if float(rp.remaining_usd) != 0.0:
        raise HTTPException(status_code=400, detail="Cannot accept: remaining must be 0")

    rp.status = PaymentStatus.accepted.value
    room.debt = 0.0

    db.commit()
    db.refresh(rp)
    return rp
