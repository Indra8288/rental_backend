from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.models.room_payment import RoomPayment

router = APIRouter(prefix="/api/v1/houses/{house_id}/history")

@router.get("/me")
def my_history(house_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Client only endpoint")
    if not user.room_id:
        raise HTTPException(status_code=400, detail="Client has no room_id bound")

    rows = (
        db.query(RoomPayment)
        .filter(RoomPayment.room_id == user.room_id)
        .order_by(desc(RoomPayment.date_key))
        .limit(12)
        .all()
    )
    return rows
