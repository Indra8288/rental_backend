from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import APIModel
from app.models.enums import IssueType

class IssueCreate(BaseModel):
    issue_type: IssueType
    details: str = Field(min_length=1)

class IssueOut(APIModel):
    id: int
    house_id: int
    room_id: str
    created_by_user_id: int
    issue_type: str
    details: str
    status: str
    created_at: datetime
    updated_at: datetime
