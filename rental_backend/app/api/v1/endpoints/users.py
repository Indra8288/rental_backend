from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access, require_roles
from app.models.enums import Role
from app.schemas.users import AdminCreate, UserOut
from app.crud.user import create_user
from app.models.user_login import UserLogin
from app.crud.house import list_houses_for_owner

router = APIRouter(prefix="/api/v1/users")

@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user

@router.get("", response_model=list[UserOut])
def list_users(house_id: int | None = None, role: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Owner: can list users within their houses (optionally filter by house_id)
    # Admin: can list users within their single house only
    # Client: forbidden
    if user.role == Role.client.value:
        raise HTTPException(status_code=403, detail="Forbidden")

    q = db.query(UserLogin)

    if user.role == Role.admin.value:
        if user.house_id is None:
            return []
        q = q.filter(UserLogin.house_id == user.house_id)
    else:
        houses = list_houses_for_owner(db, user.id)
        house_ids = [h.house_id for h in houses]
        if not house_ids:
            return []
        # include owner accounts too
        q = q.filter((UserLogin.house_id.in_(house_ids)) | (UserLogin.role == Role.owner.value))

    if house_id is not None:
        assert_house_access(db, user, house_id)
        q = q.filter((UserLogin.house_id == house_id) | (UserLogin.role == Role.owner.value))
    if role is not None:
        q = q.filter(UserLogin.role == role)

    return q.order_by(UserLogin.id.desc()).all()

@router.post("/admins", response_model=UserOut)
def create_admin_for_house(house_id: int, payload: AdminCreate, db: Session = Depends(get_db), user=Depends(require_roles(Role.owner))):
    assert_house_access(db, user, house_id)
    return create_user(
        db,
        user_name=payload.user_name.strip(),
        password=payload.password,
        role=Role.admin.value,
        house_id=house_id,
    )

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user=Depends(require_roles(Role.owner))):
    u = db.get(UserLogin, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if u.role == Role.owner.value:
        raise HTTPException(status_code=400, detail="Cannot delete owner user")

    if u.house_id is not None:
        assert_house_access(db, user, u.house_id)

    db.delete(u)
    db.commit()
    return {"ok": True, "deleted_user_id": user_id}
