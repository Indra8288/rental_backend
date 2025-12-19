from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.payment import PaymentCreate, PartlyPayCreate, RoomPaymentOut, PaymentAccept
from app.crud.rooms import get_room
from app.crud.payments import apply_full_payment, apply_partial_payment, accept_payment

router = APIRouter(prefix="/api/v1/houses/{house_id}/payments")

@router.post("/rooms/{room_id}/pay", response_model=RoomPaymentOut)
def pay(house_id: int, room_id: str, payload: PaymentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    room = get_room(db, room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")
    return apply_full_payment(db, room, payload.date_key, payload.amount_usd, payload.payment_date)

@router.post("/rooms/{room_id}/partly-pay", response_model=RoomPaymentOut)
def partly_pay(house_id: int, room_id: str, payload: PartlyPayCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    room = get_room(db, room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")
    return apply_partial_payment(db, room, payload.date_key, payload.amount_usd, payload.payment_date, payload.promise_date)

@router.post("/rooms/{room_id}/accept", response_model=RoomPaymentOut)
def accept(house_id: int, room_id: str, payload: PaymentAccept, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can accept")
    room = get_room(db, room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")
    return accept_payment(db, room, payload.date_key)
