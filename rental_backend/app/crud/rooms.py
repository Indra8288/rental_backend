from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.room import Room

def get_room(db: Session, room_id: str) -> Room:
    r = db.get(Room, room_id)
    if not r:
        raise HTTPException(status_code=404, detail="Room not found")
    return r

def list_rooms(db: Session, house_id: int) -> list[Room]:
    return db.query(Room).filter(Room.house_id == house_id).order_by(Room.room_no.asc()).all()

def list_empty_rooms(db: Session, house_id: int) -> list[Room]:
    return db.query(Room).filter(Room.house_id == house_id, Room.status == "EMPTY").order_by(Room.room_no.asc()).all()

def create_room(db: Session, room: Room) -> Room:
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
