from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import desc
from app.models.water import Water
from app.models.electric import Electric

def last_water_num(db: Session, room_id: str) -> int | None:
    w = db.query(Water).filter(Water.room_id == room_id).order_by(desc(Water.report_date), desc(Water.id)).first()
    return w.current_num if w else None

def create_water(db: Session, w: Water) -> Water:
    prev = last_water_num(db, w.room_id)
    if prev is not None and w.current_num <= prev:
        raise HTTPException(status_code=400, detail="Water current_num must be bigger than last month")
    db.add(w)
    db.commit()
    db.refresh(w)
    return w

def create_electric(db: Session, e: Electric) -> Electric:
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
