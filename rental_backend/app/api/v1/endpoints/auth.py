from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import Token, LoginRequest
from app.core.security import create_access_token
from app.crud.user import authenticate

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, data.username, data.password)
    token = create_access_token(subject=user.user_name, role=user.role, extra={"uid": user.id})
    return Token(access_token=token)
