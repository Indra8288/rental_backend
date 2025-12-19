from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user_login import UserLogin
from app.models.house import House
from app.models.enums import Role
from app.crud.user import get_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserLogin:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = get_by_username(db, username)
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return u

def require_roles(*roles: Role):
    allowed = {r.value for r in roles}
    def _dep(user: UserLogin = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return _dep

def assert_house_access(db: Session, user: UserLogin, house_id: int) -> None:
    if user.role in (Role.admin.value, Role.client.value):
        if user.house_id != house_id:
            raise HTTPException(status_code=403, detail="No access to this house")
        return
    if user.role == Role.owner.value:
        ok = db.query(House).filter(House.house_id == house_id, House.owner_id == user.id).first()
        if not ok:
            raise HTTPException(status_code=403, detail="Owner has no access to this house")
        return
    raise HTTPException(status_code=403, detail="No access")
