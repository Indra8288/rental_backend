from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.dashboard import DashboardOut
from app.crud.dashboard import house_dashboard
from app.utils.date_key import to_date_key

router = APIRouter(prefix="/api/v1/houses/{house_id}/dashboard")

@router.get("", response_model=DashboardOut)
def dashboard(house_id: int, date_key: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    if date_key is None:
        date_key = to_date_key(date.today())

    total_collected_khr, total_collected_usd, total_water_khr, total_elect_khr, collected_rooms, uncollected_rooms = house_dashboard(db, house_id, date_key)
    return DashboardOut(
        house_id=house_id,
        date_key=date_key,
        total_collected_khr=total_collected_khr,
        total_collected_usd=total_collected_usd,
        total_water_khr=total_water_khr,
        total_elect_khr=total_elect_khr,
        collected_rooms=collected_rooms,
        uncollected_rooms=uncollected_rooms,
    )
