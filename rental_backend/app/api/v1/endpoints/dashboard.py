from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role, PaymentStatus
from app.schemas.dashboard import DashboardOut
from app.models.room_payment import RoomPayment
from app.models.room import Room
from app.utils.date_key import to_date_key

router = APIRouter(prefix="/dashboard")

@router.get("", response_model=DashboardOut)
def get_dashboard(date_key: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    if date_key is None:
        date_key = to_date_key(date.today())

    total_collected_amount = db.query(func.coalesce(func.sum(RoomPayment.total_payment), 0.0)).filter(RoomPayment.date_key == date_key).scalar() or 0.0
    total_collected_water = db.query(func.coalesce(func.sum(RoomPayment.total_water), 0.0)).filter(RoomPayment.date_key == date_key).scalar() or 0.0
    total_collected_electric = db.query(func.coalesce(func.sum(RoomPayment.total_elect), 0.0)).filter(RoomPayment.date_key == date_key).scalar() or 0.0

    paid_rooms = db.query(func.count(RoomPayment.id)).filter(
        RoomPayment.date_key == date_key,
        RoomPayment.remaining == 0,
        RoomPayment.status == PaymentStatus.accepted.value
    ).scalar() or 0

    total_rooms = db.query(func.count(Room.room_no)).scalar() or 0
    uncollected = max(0, total_rooms - paid_rooms)

    return DashboardOut(
        date_key=date_key,
        total_collected_amount=float(total_collected_amount),
        total_collected_water=float(total_collected_water),
        total_collected_electric=float(total_collected_electric),
        collected_rooms=int(paid_rooms),
        uncollected_rooms=int(uncollected),
    )
