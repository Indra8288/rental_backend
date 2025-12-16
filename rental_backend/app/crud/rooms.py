from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.room import Room
from app.models.enums import RoomStatus

def get_room(db: Session, room_no: str) -> Room:
    room = db.get(Room, room_no)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

def list_rooms(db: Session) -> list[Room]:
    return db.query(Room).order_by(Room.room_no.asc()).all()

def list_empty_rooms(db: Session) -> list[Room]:
    return db.query(Room).filter(Room.status == 'Empty').order_by(Room.room_no.asc()).all()
