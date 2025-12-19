from datetime import date
from io import BytesIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.utilities import ElectricCreate, WaterCreate, UtilityOut
from app.models.electric import Electric
from app.models.water import Water
from app.crud.rooms import get_room
from app.crud.utilities import create_electric, create_water, last_water_num
from app.utils.date_key import to_date_key

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
