from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import Role
from app.schemas.house import HouseCreate, HouseOut
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
