from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import exists
from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import Role
from app.schemas.house import HouseCreate, HouseUpdate, HouseOut
from app.crud.house import create_house, list_houses_for_owner, get_house

router = APIRouter(prefix="/api/v1/houses")

@router.post("", response_model=HouseOut)
def create(payload: HouseCreate, db: Session = Depends(get_db), user=Depends(require_roles(Role.owner))):
    return create_house(db, house_name=payload.house_name, owner_id=user.id)

@router.get("", response_model=list[HouseOut])
def my_houses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == Role.owner.value:
        return list_houses_for_owner(db, user.id)
    if user.house_id is None:
        return []
    return [get_house(db, user.house_id)]

from fastapi import HTTPException
from app.api.deps import assert_house_access
from app.schemas.users import AdminCreate, UserOut
from app.crud.user import create_user

@router.post("/{house_id}/admins", response_model=UserOut)
def create_admin(house_id: int, payload: AdminCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Only owner can create admin, and only for a house they own
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can create admin")
    assert_house_access(db, user, house_id)

    u = create_user(
        db,
        user_name=payload.user_name.strip(),
        password=payload.password,
        role=Role.admin.value,
        house_id=house_id,
    )
    return u

@router.put("/{house_id}", response_model=HouseOut)
def update_house(house_id: int, payload: HouseUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Only owner can update house and must own it
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can edit house")
    assert_house_access(db, user, house_id)

    h = get_house(db, house_id)
    h.house_name = payload.house_name.strip()
    db.commit()
    db.refresh(h)
    return h

@router.delete("/{house_id}")
def delete_house(house_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Only owner can delete house and must own it
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can delete house")
    assert_house_access(db, user, house_id)

    from app.models.house import House
    from app.models.room import Room
    from app.models.customer import Customer
    from app.models.water import Water
    from app.models.electric import Electric
    from app.models.room_payment import RoomPayment
    from app.models.issue_ticket import IssueTicket
    from app.models.user_login import UserLogin

    # Block delete if any related records exist
    has_rooms = db.query(exists().where(Room.house_id == house_id)).scalar()
    has_customers = db.query(exists().where(Customer.house_id == house_id)).scalar()
    has_issues = db.query(exists().where(IssueTicket.house_id == house_id)).scalar()
    has_users = db.query(exists().where(UserLogin.house_id == house_id)).scalar()

    # Indirect tables linked via rooms
    has_water = (
        db.query(exists().where(Water.room_id == Room.room_id).where(Room.house_id == house_id))
        .select_from(Water, Room)
        .scalar()
    )
    has_electric = (
        db.query(exists().where(Electric.room_id == Room.room_id).where(Room.house_id == house_id))
        .select_from(Electric, Room)
        .scalar()
    )
    has_payments = (
        db.query(exists().where(RoomPayment.room_id == Room.room_id).where(Room.house_id == house_id))
        .select_from(RoomPayment, Room)
        .scalar()
    )

    if any([has_rooms, has_customers, has_water, has_electric, has_payments, has_issues, has_users]):
        return {
            "ok": False,
            "deleted": False,
            "reason": "House has related records. Delete rooms/customers/utilities/payments/issues/users first.",
            "details": {
                "rooms": bool(has_rooms),
                "customers": bool(has_customers),
                "water": bool(has_water),
                "electric": bool(has_electric),
                "payments": bool(has_payments),
                "issues": bool(has_issues),
                "users": bool(has_users),
            },
        }

    h = db.get(House, house_id)
    if not h:
        raise HTTPException(status_code=404, detail="House not found")

    db.delete(h)
    db.commit()
    return {"ok": True, "deleted": True, "house_id": house_id}
