from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import Role
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserOut)
def me(user = Depends(get_current_user)):
    return user

@router.post("", response_model=UserOut)
def create(payload: UserCreate, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner))):
    return create_user(
        db,
        user_name=payload.user_name,
        password=payload.password,
        role=payload.role.value,
        customer_id=payload.customer_id,
        room_no=payload.room_no,
    )
