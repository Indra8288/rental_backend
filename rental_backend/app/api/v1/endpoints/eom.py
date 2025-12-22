from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role, PaymentStatus
from app.crud.rooms import list_rooms
from app.crud.payments import ensure_payment_row, get_payment, usd_to_khr
from app.utils.date_key import prev_month_key

router = APIRouter(prefix="/api/v1/houses/{house_id}/eom")

@router.post("/start")
def start_eom(house_id: int, new_date_key: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can run EOM")

    rooms = list_rooms(db, house_id)
    prev_key = prev_month_key(new_date_key)

    # Close previous month: unpaid -> DEBT, carry remaining into room.debt (KHR)
    for r in rooms:
        prev = get_payment(db, r.room_id, prev_key)
        if prev and float(prev.remaining_usd) > 0.0 and prev.status != PaymentStatus.accepted.value:
            prev.status = PaymentStatus.debt.value
            r.debt = float(prev.remaining_usd)

    # Open new month: reset status to OPENING and set remaining in KHR
    for r in rooms:
        rp = ensure_payment_row(db, r, new_date_key)
        rp.status = PaymentStatus.opening.value
        rp.remaining_usd = float(usd_to_khr(r.price_usd) + float(r.debt or 0.0))
        r.last_bom = date.today()

    db.commit()
    return {"ok": True, "house_id": house_id, "new_date_key": new_date_key, "rooms": len(rooms)}
