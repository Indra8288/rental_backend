from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import pandas as pd
from io import BytesIO

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role
from app.schemas.utilities import ElectricCreate, WaterCreate, UtilityOut
from app.models.electric import Electric
from app.models.water import Water
from app.crud.utilities import create_electric, create_water, last_water_num
from app.crud.rooms import get_room
from app.utils.date_key import to_date_key

router = APIRouter(prefix="/utilities")

@router.post("/electric", response_model=UtilityOut)
def add_electric(payload: ElectricCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    _ = get_room(db, payload.room_no)

    report_date = date.today()
    date_key = to_date_key(report_date)  # YYYY-MM

    e = Electric(
        room_no=payload.room_no,
        current_num=payload.current_num,
        report_date=report_date,
        date_key=date_key,
        price=payload.price,
    )
    return create_electric(db, e)

@router.post("/water", response_model=UtilityOut)
def add_water(payload: WaterCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    _ = get_room(db, payload.room_no)

    report_date = date.today()
    date_key = to_date_key(report_date)  # YYYY-MM

    prev_num = last_water_num(db, payload.room_no) or 0
    # create_water() already enforces payload.current_num > prev_num when prev exists
    price = (payload.current_num - prev_num) * 2500

    w = Water(
        room_no=payload.room_no,
        current_num=payload.current_num,
        report_date=report_date,
        date_key=date_key,
        price=price,
    )
    return create_water(db, w)

@router.post("/electric/upload-excel")
def upload_electric_excel(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    """Excel columns expected: room_no, current_num, price (optional)"""
    content = file.file.read()
    df = pd.read_excel(BytesIO(content))

    required = {"room_no", "current_num"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {sorted(required)}")

    report_date = date.today()
    date_key = to_date_key(report_date)

    created = 0
    for _, row in df.iterrows():
        room_no = str(row["room_no"]).strip()
        current_num = int(row["current_num"])
        price = float(row["price"]) if "price" in df.columns and not pd.isna(row.get("price")) else 0.0

        _ = get_room(db, room_no)
        e = Electric(room_no=room_no, current_num=current_num, report_date=report_date, date_key=date_key, price=price)
        create_electric(db, e)
        created += 1

    return {"created": created, "report_date": str(report_date), "date_key": date_key}

@router.post("/water/upload-excel")
def upload_water_excel(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    """Excel columns expected: room_no, current_num, price (optional)"""
    content = file.file.read()
    df = pd.read_excel(BytesIO(content))

    required = {"room_no", "current_num"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {sorted(required)}")

    report_date = date.today()
    date_key = to_date_key(report_date)

    created = 0
    for _, row in df.iterrows():
        room_no = str(row["room_no"]).strip()
        current_num = int(row["current_num"])
        price = float(row["price"]) if "price" in df.columns and not pd.isna(row.get("price")) else 0.0

        _ = get_room(db, room_no)
        w = Water(room_no=room_no, current_num=current_num, report_date=report_date, date_key=date_key, price=price)
        create_water(db, w)
        created += 1

    return {"created": created, "report_date": str(report_date), "date_key": date_key}
