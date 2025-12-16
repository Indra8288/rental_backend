from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pathlib import Path
import shutil
from app.crud.user import create_user
from app.models.enums import Role

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.models.customer import Customer
from app.core.config import settings
from app.crud.customers import create_customer, list_customers, get_customer, update_customer
from app.crud.rooms import get_room
from app.crud.payments import ensure_payment_row, apply_full_payment, apply_partial_payment
from app.utils.date_key import to_date_key

router = APIRouter(prefix="/customers")

@router.get("", response_model=list[CustomerOut])
def all_customers(status: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    return list_customers(db, status=status)

@router.post("", response_model=CustomerOut)
def register(payload: CustomerCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    cust = Customer(
        name=payload.name,
        phone_no=payload.phone_no,
        dob=payload.dob,
        room_no=payload.room_no,
        start_date=payload.start_date,
        telegram=payload.telegram,
        remark=payload.remark,
        status="Active",
    )
    cust = create_customer(db, obj=cust)
    # ---- Auto-create client login
    if payload.dob is None:
        raise HTTPException(status_code=400, detail="dob is required to auto-create client login password")

    username = payload.phone_no.strip()
    password = payload.dob.strftime("%d%m%Y") + payload.room_no.strip()  # DDMMYYYY + room_no

    try:
        create_user(
            db,
            user_name=username,
            password=password,
            role=Role.client.value,
            customer_id=cust.cust_id,
            room_no=payload.room_no,
        )
    except Exception as ex:
        # If login creation fails, rollback the customer creation to avoid inconsistent data
        # (room would otherwise remain OCCUPIED without a login)
        db.delete(cust)
        # reset room back to empty
        room = get_room(db, payload.room_no)
        room.status = "EMPTY"
        db.commit()

        # raise a clean error
        raise HTTPException(status_code=400, detail=f"Failed to auto-create client login: {str(ex)}")


    # Create initial payment row for the month of start_date
    date_key = to_date_key(payload.start_date)
    room = get_room(db, payload.room_no)
    rp = ensure_payment_row(db, room, date_key)

    if payload.payment_fully_paid:
        # full payment amount assumed = remaining
        if rp.remaining > 0:
            apply_full_payment(db, room, date_key, amount=rp.remaining, payment_date=payload.start_date, pending=False)
    else:
        if not payload.partial_amount or payload.partial_amount <= 0:
            raise HTTPException(status_code=400, detail="partial_amount required when not fully paid")
        apply_partial_payment(db, room, date_key, amount=payload.partial_amount, payment_date=payload.start_date, promise_date=payload.start_date, pending=True)

    return cust

@router.get("/{cust_id}", response_model=CustomerOut)
def get_one(cust_id: int, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    return get_customer(db, cust_id)

@router.patch("/{cust_id}", response_model=CustomerOut)
def edit(cust_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    cust = get_customer(db, cust_id)
    patch = payload.model_dump(exclude_unset=True)
    return update_customer(db, cust, patch)

@router.post("/{cust_id}/upload-id", response_model=CustomerOut)
def upload_id(cust_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    cust = get_customer(db, cust_id)
    upload_dir = Path(settings.UPLOAD_DIR) / "ids"
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"cust_{cust_id}_{file.filename}"
    dest = upload_dir / safe_name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    cust.id_link = str(dest.as_posix())
    db.commit()
    db.refresh(cust)
    return cust
