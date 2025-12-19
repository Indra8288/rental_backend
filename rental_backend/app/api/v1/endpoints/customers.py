from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role
from app.schemas.customer import CustomerCreate, CustomerOut
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
