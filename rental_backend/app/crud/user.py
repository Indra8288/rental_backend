from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_login import UserLogin
from app.core.security import hash_password, verify_password
from app.models.enums import Role

def get_by_username(db: Session, user_name: str) -> UserLogin | None:
    return db.query(UserLogin).filter(UserLogin.user_name == user_name).first()

def create_user(db: Session, *, user_name: str, password: str, role: str,
                house_id: int | None = None, room_id: str | None = None, customer_id: int | None = None) -> UserLogin:
    if get_by_username(db, user_name):
        raise HTTPException(status_code=400, detail="username already exists")
    if role in (Role.admin.value, Role.client.value) and house_id is None:
        raise HTTPException(status_code=400, detail="house_id is required for admin/client")
    u = UserLogin(user_name=user_name, pass_hash=hash_password(password), role=role,
                  house_id=house_id, room_id=room_id, customer_id=customer_id)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def authenticate(db: Session, user_name: str, password: str) -> UserLogin:
    u = get_by_username(db, user_name)
    if not u or not verify_password(password, u.pass_hash):
        raise HTTPException(status_code=401, detail="Invalid username/password")
    return u
