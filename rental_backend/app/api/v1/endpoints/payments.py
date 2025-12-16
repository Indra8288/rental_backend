from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role
from app.schemas.payment import PaymentCreate, PartlyPayCreate, RoomPaymentOut, PaymentAccept
from app.crud.rooms import get_room
from app.crud.payments import apply_full_payment, apply_partial_payment, accept_payment

router = APIRouter(prefix="/payments")

@router.post("/rooms/{room_no}/pay", response_model=RoomPaymentOut)
def pay(room_no: str, payload: PaymentCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    room = get_room(db, room_no)
    return apply_full_payment(db, room, payload.date_key, payload.amount, payload.payment_date)

@router.post("/rooms/{room_no}/partly-pay", response_model=RoomPaymentOut)
def partly_pay(room_no: str, payload: PartlyPayCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    room = get_room(db, room_no)
    return apply_partial_payment(db, room, payload.date_key, payload.amount, payload.payment_date, payload.promise_date)

@router.post("/rooms/{room_no}/accept", response_model=RoomPaymentOut)
def accept(room_no: str, payload: PaymentAccept, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner))):
    return accept_payment(db, room_no, payload.date_key)
