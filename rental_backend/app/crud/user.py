from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_login import UserLogin
from app.core.security import hash_password, verify_password

def get_by_username(db: Session, username: str) -> UserLogin | None:
    return db.query(UserLogin).filter(UserLogin.user_name == username).first()

def authenticate(db: Session, username: str, password: str) -> UserLogin:
    user = get_by_username(db, username)
    if not user or not verify_password(password, user.pass_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return user

def create_user(db: Session, *, user_name: str, password: str, role: str, customer_id: int | None = None, room_no: str | None = None) -> UserLogin:
    if get_by_username(db, user_name):
        raise HTTPException(status_code=400, detail="Username already exists")
    u = UserLogin(user_name=user_name, pass_hash=hash_password(password), role=role, customer_id=customer_id, room_no=room_no)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
