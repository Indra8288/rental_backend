from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token
from app.core.security import create_access_token
from app.crud.user import authenticate

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    token = create_access_token(subject=user.user_name, role=user.role, extra={"uid": user.id})
    return Token(access_token=token)
