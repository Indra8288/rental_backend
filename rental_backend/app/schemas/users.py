from pydantic import BaseModel, Field
from app.schemas.common import APIModel

class AdminCreate(BaseModel):
    user_name: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=4, max_length=200)

class UserOut(APIModel):
    id: int
    user_name: str
    role: str
    house_id: int | None = None
