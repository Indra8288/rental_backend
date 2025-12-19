from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.room import Room
from app.models.room_payment import RoomPayment
from app.models.water import Water
from app.models.electric import Electric

def house_dashboard(db: Session, house_id: int, date_key: str):
    total_collected_usd = float(
        db.query(func.coalesce(func.sum(RoomPayment.total_payment_usd), 0.0))
        .join(Room, Room.room_id == RoomPayment.room_id)
        .filter(Room.house_id == house_id, RoomPayment.date_key == date_key)
        .scalar() or 0.0
    )
    total_water_khr = float(
        db.query(func.coalesce(func.sum(Water.price_khr), 0.0))
        .join(Room, Room.room_id == Water.room_id)
        .filter(Room.house_id == house_id, Water.date_key == date_key)
        .scalar() or 0.0
    )
    total_elect_khr = float(
        db.query(func.coalesce(func.sum(Electric.price_khr), 0.0))
        .join(Room, Room.room_id == Electric.room_id)
        .filter(Room.house_id == house_id, Electric.date_key == date_key)
        .scalar() or 0.0
    )
    collected_rooms = int(
        db.query(func.count(RoomPayment.id))
        .join(Room, Room.room_id == RoomPayment.room_id)
        .filter(Room.house_id == house_id, RoomPayment.date_key == date_key, RoomPayment.remaining_usd == 0)
        .scalar() or 0
    )
    total_rooms = int(db.query(func.count(Room.room_id)).filter(Room.house_id == house_id).scalar() or 0)
    return total_collected_usd, total_water_khr, total_elect_khr, collected_rooms, max(0, total_rooms - collected_rooms)
