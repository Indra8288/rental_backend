from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.house import House

def create_house(db: Session, *, house_name: str, owner_id: int) -> House:
    h = House(house_name=house_name, owner_id=owner_id)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h

def get_house(db: Session, house_id: int) -> House:
    h = db.get(House, house_id)
    if not h:
        raise HTTPException(status_code=404, detail="House not found")
    return h

def list_houses_for_owner(db: Session, owner_id: int) -> list[House]:
    return db.query(House).filter(House.owner_id == owner_id).order_by(House.house_id.desc()).all()
