from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enums import Role
from app.crud.house import list_houses_for_owner, get_house

router = APIRouter(prefix="/api/v1/home")

@router.get("/me")
def home_me(db: Session = Depends(get_db), user=Depends(get_current_user)):
    houses = []
    if user.role == Role.owner.value:
        houses = list_houses_for_owner(db, user.id)
    elif user.house_id is not None:
        houses = [get_house(db, user.house_id)]

    return {
        "user": {
            "id": user.id,
            "user_name": user.user_name,
            "role": user.role,
            "house_id": user.house_id,
            "room_id": user.room_id,
            "customer_id": user.customer_id,
        },
        "houses": [{"house_id": h.house_id, "house_name": h.house_name, "owner_id": h.owner_id} for h in houses],
    }
