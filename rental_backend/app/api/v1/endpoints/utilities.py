from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.models.room import Room
from app.models.water import Water
from app.models.electric import Electric
from app.schemas.utilities import (
    ElectricCreate,
    WaterCreate,
    ElectricBulkCreate,
    WaterBulkCreate,
    UtilitiesOverviewOut,
    UtilityRoomOverview,
)
from app.utils.date_key import to_date_key, prev_month_key

router = APIRouter(prefix="/api/v1/houses/{house_id}/utilities")

WATER_RATE_KHR = 2500.0

def _require_owner_or_admin(user):
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

def _get_room_in_house(db: Session, house_id: int, room_id: str) -> Room:
    r = db.get(Room, room_id)
    if not r or r.house_id != house_id:
        raise HTTPException(status_code=404, detail=f"Room not found: {room_id}")
    return r

def _get_latest_by_key(db: Session, model, room_id: str, date_key: str):
    return (
        db.query(model)
        .filter(and_(model.room_id == room_id, model.date_key == date_key))
        .order_by(model.report_date.desc())
        .first()
    )

@router.post("/electric")
def add_electric(house_id: int, payload: ElectricCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    _require_owner_or_admin(user)

    _get_room_in_house(db, house_id, payload.room_id)
    report_date = date.today()
    dk = to_date_key(report_date)

    e = Electric(
        room_id=payload.room_id,
        current_num=payload.current_num,
        price_khr=float(payload.price_khr),
        report_date=report_date,
        date_key=dk,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@router.post("/water")
def add_water(house_id: int, payload: WaterCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    _require_owner_or_admin(user)

    _get_room_in_house(db, house_id, payload.room_id)
    report_date = date.today()
    dk = to_date_key(report_date)
    prev_dk = prev_month_key(dk)

    prev = _get_latest_by_key(db, Water, payload.room_id, prev_dk)
    prev_num = int(prev.current_num) if prev else 0

    if payload.current_num < prev_num:
        raise HTTPException(status_code=400, detail=f"Water current_num must be >= previous month ({prev_num})")

    usage = payload.current_num - prev_num
    price_khr = float(usage * WATER_RATE_KHR)

    wrow = Water(
        room_id=payload.room_id,
        current_num=payload.current_num,
        price_khr=price_khr,
        report_date=report_date,
        date_key=dk,
    )
    db.add(wrow)
    db.commit()
    db.refresh(wrow)
    return wrow

# 1) Bulk insert electricity many at once
@router.post("/electric/bulk")
def add_electric_bulk(house_id: int, payload: ElectricBulkCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    _require_owner_or_admin(user)

    if not payload.items:
        return {"ok": True, "inserted": 0}

    report_date = date.today()
    dk = to_date_key(report_date)

    rows = []
    for item in payload.items:
        _get_room_in_house(db, house_id, item.room_id)
        rows.append(
            Electric(
                room_id=item.room_id,
                current_num=item.current_num,
                price_khr=float(item.price_khr),
                report_date=report_date,
                date_key=dk,
            )
        )

    db.add_all(rows)
    db.commit()
    return {"ok": True, "date_key": dk, "inserted": len(rows)}

# 1) Bulk insert water many at once (auto price = usage * 2500)
@router.post("/water/bulk")
def add_water_bulk(house_id: int, payload: WaterBulkCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    _require_owner_or_admin(user)

    if not payload.items:
        return {"ok": True, "inserted": 0}

    report_date = date.today()
    dk = to_date_key(report_date)
    prev_dk = prev_month_key(dk)

    rows = []
    for item in payload.items:
        _get_room_in_house(db, house_id, item.room_id)
        prev = _get_latest_by_key(db, Water, item.room_id, prev_dk)
        prev_num = int(prev.current_num) if prev else 0
        if item.current_num < prev_num:
            raise HTTPException(status_code=400, detail=f"Room {item.room_id}: water current_num must be >= previous month ({prev_num})")

        usage = item.current_num - prev_num
        price_khr = float(usage * WATER_RATE_KHR)

        rows.append(
            Water(
                room_id=item.room_id,
                current_num=item.current_num,
                price_khr=price_khr,
                report_date=report_date,
                date_key=dk,
            )
        )

    db.add_all(rows)
    db.commit()
    return {"ok": True, "date_key": dk, "inserted": len(rows)}

# 2) Overview endpoint for frontend rendering (water OR electric)
@router.get("/overview", response_model=UtilitiesOverviewOut)
def utilities_overview(
    house_id: int,
    utility_type: str,
    date_key: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Frontend helper:
      Return list of rooms with:
        - room_no, room_id
        - previous month number
        - current month number (null if not input)
        - current total in KHR (null if not input)
    utility_type: "water" or "electric"
    date_key: target month (YYYY-MM). If omitted, uses current month.
    """
    assert_house_access(db, user, house_id)
    _require_owner_or_admin(user)

    if date_key is None:
        date_key = to_date_key(date.today())
    prev_dk = prev_month_key(date_key)

    if utility_type not in ("water", "electric"):
        raise HTTPException(status_code=400, detail='utility_type must be "water" or "electric"')

    rooms = db.query(Room).filter(Room.house_id == house_id).order_by(Room.room_no.asc()).all()

    out_rooms: list[UtilityRoomOverview] = []
    for r in rooms:
        if utility_type == "water":
            prev = _get_latest_by_key(db, Water, r.room_id, prev_dk)
            curr = _get_latest_by_key(db, Water, r.room_id, date_key)
            out_rooms.append(
                UtilityRoomOverview(
                    room_id=r.room_id,
                    room_no=r.room_no,
                    prev_num=int(prev.current_num) if prev else None,
                    current_num=int(curr.current_num) if curr else None,
                    total_khr=float(curr.price_khr) if curr else None,
                )
            )
        else:
            prev = _get_latest_by_key(db, Electric, r.room_id, prev_dk)
            curr = _get_latest_by_key(db, Electric, r.room_id, date_key)
            out_rooms.append(
                UtilityRoomOverview(
                    room_id=r.room_id,
                    room_no=r.room_no,
                    prev_num=int(prev.current_num) if prev else None,
                    current_num=int(curr.current_num) if curr else None,
                    total_khr=float(curr.price_khr) if curr else None,
                )
            )

    return UtilitiesOverviewOut(house_id=house_id, date_key=date_key, utility_type=utility_type, rooms=out_rooms)
