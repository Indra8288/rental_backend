from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.models.room import Room
from app.models.customer import Customer

router = APIRouter(prefix="/api/v1/admin")

@router.get("/overview")
def admin_overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != Role.admin.value:
        raise HTTPException(status_code=403, detail="Admin only")
    if user.house_id is None:
        raise HTTPException(status_code=400, detail="Admin has no house_id assigned")

    house_id = user.house_id
    assert_house_access(db, user, house_id)

    total_rooms = int(db.query(func.count(Room.room_id)).filter(Room.house_id == house_id).scalar() or 0)
    active_customers = int(db.query(func.count(Customer.cust_id)).filter(Customer.house_id == house_id, Customer.status == "Active").scalar() or 0)

    return {"house_id": house_id, "total_rooms": total_rooms, "active_customers": active_customers}
