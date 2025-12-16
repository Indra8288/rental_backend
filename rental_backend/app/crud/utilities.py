from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import desc
from app.models.electric import Electric
from app.models.water import Water

def last_water_num(db: Session, room_no: str) -> int | None:
    rec = db.query(Water).filter(Water.room_no == room_no).order_by(desc(Water.report_date)).first()
    return rec.current_num if rec else None

def create_electric(db: Session, e: Electric) -> Electric:
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

def create_water(db: Session, w: Water) -> Water:
    last = last_water_num(db, w.room_no)
    if last is not None and w.current_num <= last:
        raise HTTPException(status_code=400, detail=f"Water current_num must be bigger than last month ({last})")
    db.add(w)
    db.commit()
    db.refresh(w)
    return w

def list_electric_by_month(db: Session, date_key: str):
    return db.query(Electric).filter(Electric.date_key == date_key).all()

def list_water_by_month(db: Session, date_key: str):
    return db.query(Water).filter(Water.date_key == date_key).all()
