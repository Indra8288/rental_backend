from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role, PaymentStatus
from app.crud.rooms import list_rooms
from app.crud.payments import ensure_payment_row, get_payment
from app.utils.date_key import prev_month_key

router = APIRouter(prefix="/eom")

@router.get("/rooms")
def list_rooms_for_new_month(date_key: str, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    rooms = list_rooms(db)
    out = []
    for r in rooms:
        rp = ensure_payment_row(db, r, date_key)
        out.append({"room_no": r.room_no, "remaining": rp.remaining, "status": rp.status})
    return out

@router.post("/start")
def start_eom(new_date_key: str, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner))):
    rooms = list_rooms(db)
    prev_key = prev_month_key(new_date_key)

    # 1) Close previous month: unpaid -> DEBT, carry to room.debt
    for r in rooms:
        prev = get_payment(db, r.room_no, prev_key)
        if prev and prev.remaining > 0 and prev.status != PaymentStatus.accepted.value:
            prev.status = PaymentStatus.debt.value
            r.debt = float(prev.remaining)

    # 2) Create/Reset new month rows to OPENING
    for r in rooms:
        rp = ensure_payment_row(db, r, new_date_key)
        rp.status = PaymentStatus.opening.value
        rp.remaining = float(r.price + r.debt)

        r.last_bom = date.today()

    db.commit()
    return {"ok": True, "new_date_key": new_date_key, "rooms": len(rooms)}
