from datetime import date
from io import BytesIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.utilities import (
    ElectricCreate,
    WaterCreate,
    UtilityOut,
    ElectricLastMonthOut,
    WaterLastMonthOut,
)
from app.models.electric import Electric
from app.models.water import Water
from app.crud.rooms import get_room, list_rooms
from app.crud.utilities import create_electric, create_water, last_water_num
from app.utils.date_key import to_date_key, prev_month_key

router = APIRouter(prefix="/api/v1/houses/{house_id}/utilities")

@router.post("/electric", response_model=UtilityOut)
def add_electric(house_id: int, payload: ElectricCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    room = get_room(db, payload.room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    report_date = date.today()
    date_key = to_date_key(report_date)

    e = Electric(
        room_id=payload.room_id,
        current_num=payload.current_num,
        report_date=report_date,
        date_key=date_key,
        price_khr=payload.price_khr,
    )
    return create_electric(db, e)

@router.post("/water", response_model=UtilityOut)
def add_water(house_id: int, payload: WaterCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    room = get_room(db, payload.room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    report_date = date.today()
    date_key = to_date_key(report_date)

    prev_num = last_water_num(db, payload.room_id) or 0
    price_khr = float((payload.current_num - prev_num) * 2500)

    wtr = Water(
        room_id=payload.room_id,
        current_num=payload.current_num,
        report_date=report_date,
        date_key=date_key,
        price_khr=price_khr,
    )
    return create_water(db, wtr)

@router.post("/electric/upload-excel")
def upload_electric_excel(house_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    content = file.file.read()
    df = pd.read_excel(BytesIO(content))
    required = {"room_id", "current_num"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {sorted(required)}")

    report_date = date.today()
    date_key = to_date_key(report_date)

    created = 0
    for _, row in df.iterrows():
        room_id = str(row["room_id"]).strip()
        current_num = int(row["current_num"])
        price_khr = float(row["price_khr"]) if "price_khr" in df.columns and not pd.isna(row.get("price_khr")) else 0.0

        room = get_room(db, room_id)
        if room.house_id != house_id:
            continue

        e = Electric(room_id=room_id, current_num=current_num, report_date=report_date, date_key=date_key, price_khr=price_khr)
        create_electric(db, e)
        created += 1

    return {"created": created, "date_key": date_key}

@router.post("/water/upload-excel")
def upload_water_excel(house_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    content = file.file.read()
    df = pd.read_excel(BytesIO(content))
    required = {"room_id", "current_num"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {sorted(required)}")

    report_date = date.today()
    date_key = to_date_key(report_date)

    created = 0
    for _, row in df.iterrows():
        room_id = str(row["room_id"]).strip()
        current_num = int(row["current_num"])

        room = get_room(db, room_id)
        if room.house_id != house_id:
            continue

        prev_num = last_water_num(db, room_id) or 0
        price_khr = float((current_num - prev_num) * 2500)

        wtr = Water(room_id=room_id, current_num=current_num, report_date=report_date, date_key=date_key, price_khr=price_khr)
        create_water(db, wtr)
        created += 1

    return {"created": created, "date_key": date_key}


@router.get("/electric/last-month", response_model=list[ElectricLastMonthOut])
def last_month_electric(house_id: int, date_key: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    List all rooms and return the latest electricity number + price for LAST MONTH.

    - If date_key is omitted, uses current month and computes previous month automatically.
    - Uses the latest record in that month (by report_date desc, id desc).
    """
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    if date_key is None:
        date_key = to_date_key(date.today())
    target_key = prev_month_key(date_key)

    out: list[ElectricLastMonthOut] = []
    for r in list_rooms(db, house_id):
        rec = (
            db.query(Electric)
            .filter(Electric.room_id == r.room_id, Electric.date_key == target_key)
            .order_by(desc(Electric.report_date), desc(Electric.id))
            .first()
        )
        out.append(
            ElectricLastMonthOut(
                room_id=r.room_id,
                room_no=r.room_no,
                date_key=target_key,
                current_num=rec.current_num if rec else None,
                price_khr=float(rec.price_khr) if rec else None,
            )
        )
    return out


@router.get("/water/last-month", response_model=list[WaterLastMonthOut])
def last_month_water(house_id: int, date_key: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    List all rooms and return the latest water number for LAST MONTH.

    - If date_key is omitted, uses current month and computes previous month automatically.
    - Uses the latest record in that month (by report_date desc, id desc).
    """
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    if date_key is None:
        date_key = to_date_key(date.today())
    target_key = prev_month_key(date_key)

    out: list[WaterLastMonthOut] = []
    for r in list_rooms(db, house_id):
        rec = (
            db.query(Water)
            .filter(Water.room_id == r.room_id, Water.date_key == target_key)
            .order_by(desc(Water.report_date), desc(Water.id))
            .first()
        )
        out.append(
            WaterLastMonthOut(
                room_id=r.room_id,
                room_no=r.room_no,
                date_key=target_key,
                current_num=rec.current_num if rec else None,
            )
        )
    return out
