from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import APIModel
from app.models.enums import Role

class UserCreate(BaseModel):
    user_name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    role: Role
    customer_id: int | None = None
    room_no: str | None = None

class UserOut(APIModel):
    id: int
    user_name: str
    role: str
    created_at: datetime
    customer_id: int | None = None
    room_no: str | None = None
