from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.models.customer import Customer
from app.crud.customers import create_customer
from app.crud.rooms import get_room
from app.crud.user import create_user
from app.utils.date_key import make_room_id

router = APIRouter(prefix="/api/v1/houses/{house_id}/customers")

@router.post("", response_model=CustomerOut)
def register(house_id: int, payload: CustomerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    room_id = make_room_id(house_id, payload.room_no.strip())
    room = get_room(db, room_id)
    if room.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")
    if room.status != "EMPTY":
        raise HTTPException(status_code=400, detail="Room is not empty")

    cust = Customer(
        name=payload.name,
        dob=payload.dob,
        house_id=house_id,
        room_id=room_id,
        start_date=payload.start_date,
        phone_no=payload.phone_no,
        telegram=payload.telegram,
        remark=payload.remark,
        id_link=payload.id_link,
        status=payload.status,
    )
    cust = create_customer(db, cust)

    room.status = "OCCUPIED"
    db.commit()

    if payload.dob is None:
        raise HTTPException(status_code=400, detail="dob is required to auto-create client login password")

    username = payload.phone_no.strip()
    password = payload.dob.strftime("%d%m%Y") + payload.room_no.strip()

    create_user(
        db,
        user_name=username,
        password=password,
        role=Role.client.value,
        house_id=house_id,
        room_id=room_id,
        customer_id=cust.cust_id,
    )

    return cust

from app.services.s3 import build_key, upload_fileobj, presign_get, get_object_stream

@router.get("", response_model=list[CustomerOut])
def list_customers(house_id: int, status: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    q = db.query(Customer).filter(Customer.house_id == house_id)
    if status:
        q = q.filter(Customer.status == status)
    return q.order_by(desc(Customer.cust_id)).all()

@router.put("/{cust_id}", response_model=CustomerOut)
def update_customer(house_id: int, cust_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    cust = db.get(Customer, cust_id)
    if not cust or cust.house_id != house_id:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Allowed updates (room changes are NOT supported here)
    if payload.name is not None:
        cust.name = payload.name
    if payload.phone_no is not None:
        cust.phone_no = payload.phone_no
    if payload.dob is not None:
        cust.dob = payload.dob
    if payload.start_date is not None:
        cust.start_date = payload.start_date
    if payload.telegram is not None:
        cust.telegram = payload.telegram
    if payload.remark is not None:
        cust.remark = payload.remark
    if payload.id_link is not None:
        cust.id_link = payload.id_link
    if payload.status is not None:
        cust.status = payload.status

    db.commit()
    db.refresh(cust)
    return cust

@router.post("/{cust_id}/id/upload")
def upload_customer_id_image(house_id: int, cust_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Upload customer's ID picture to S3 and store the S3 key in customer.id_link."""
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    cust = db.get(Customer, cust_id)
    if not cust or cust.house_id != house_id:
        raise HTTPException(status_code=404, detail="Customer not found")

    filename = file.filename or "id"
    ext = ""
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        ext = "".join([c for c in ext if c.isalnum()])[:10]

    key = build_key(f"house-{house_id}", "customers", str(cust_id), f"id.{ext}" if ext else "id")
    upload_fileobj(file.file, key, content_type=file.content_type)

    cust.id_link = key
    db.commit()

    return {"ok": True, "s3_key": key}

@router.get("/{cust_id}/id/url")
def get_customer_id_presigned_url(house_id: int, cust_id: int, expires: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return a presigned URL to view the customer's ID picture."""
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    cust = db.get(Customer, cust_id)
    if not cust or cust.house_id != house_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not cust.id_link:
        raise HTTPException(status_code=404, detail="Customer has no id_link")

    url = presign_get(cust.id_link, expires=expires)
    return {"url": url}

@router.get("/{cust_id}/id/file")
def get_customer_id_file(house_id: int, cust_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Proxy the customer's ID image bytes from S3."""
    from fastapi.responses import StreamingResponse

    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    cust = db.get(Customer, cust_id)
    if not cust or cust.house_id != house_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not cust.id_link:
        raise HTTPException(status_code=404, detail="Customer has no id_link")

    body, content_type = get_object_stream(cust.id_link)
    return StreamingResponse(body, media_type=content_type)

