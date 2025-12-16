from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from dateutil.relativedelta import relativedelta

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import Role
from app.schemas.history import HistoryOut, MonthlyHistoryItem
from app.models.room_payment import RoomPayment

router = APIRouter(prefix="/history")

def last_n_month_keys(n: int = 12) -> list[str]:
    keys = []
    d = date.today().replace(day=1)
    for i in range(n):
        k = f"{d.year:04d}-{d.month:02d}"
        keys.append(k)
        d = d - relativedelta(months=1)
    return keys

@router.get("/me", response_model=HistoryOut)
def my_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Client only endpoint")
    if not user.room_no:
        raise HTTPException(status_code=400, detail="Client user has no room_no bound")
    room_no = user.room_no

    keys = last_n_month_keys(12)
    rows = db.query(RoomPayment).filter(RoomPayment.room_no == room_no, RoomPayment.date_key.in_(keys)).order_by(desc(RoomPayment.date_key)).all()

    items = []
    for r in rows:
        items.append(MonthlyHistoryItem(
            date_key=r.date_key,
            room_price_paid=r.total_payment,
            water_paid=r.total_water,
            electric_paid=r.total_elect,
            remaining=r.remaining,
        ))
    return HistoryOut(room_no=room_no, items=items)
