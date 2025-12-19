from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role, IssueStatus
from app.schemas.issues import IssueCreate, IssueOut
from app.models.issue_ticket import IssueTicket
from app.crud.issues import create_issue, list_issues, list_my_issues, accept_issue, resolve_issue

router = APIRouter(prefix="/api/v1/houses/{house_id}/issues")

@router.post("", response_model=IssueOut)
def create(house_id: int, payload: IssueCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Only client can create issues")
    if not user.room_id:
        raise HTTPException(status_code=400, detail="Client has no room_id bound")

    ticket = IssueTicket(
        house_id=house_id,
        room_id=user.room_id,
        created_by_user_id=user.id,
        issue_type=payload.issue_type.value,
        details=payload.details,
        status=IssueStatus.opening.value,
    )
    return create_issue(db, ticket)

@router.get("", response_model=list[IssueOut])
def my_issues(house_id: int, status: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Client only endpoint")
    if status and status not in {"OPENING", "ACCEPTED", "RESOLVED"}:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    return list_my_issues(db, user_id=user.id, house_id=house_id, status=status)

@router.get("/all", response_model=list[IssueOut])
def all_issues(house_id: int, status: str = "all", db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    status_map = {
        "opening": IssueStatus.opening.value,
        "accepted": IssueStatus.accepted.value,
        "resolved": IssueStatus.resolved.value,
        "all": None,
    }
    key = status.lower().strip()
    if key not in status_map:
        raise HTTPException(status_code=400, detail="status must be: opening, accepted, resolved, all")
    return list_issues(db, house_id=house_id, status=status_map[key])

@router.post("/{ticket_id}/accept", response_model=IssueOut)
def accept(house_id: int, ticket_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    t = accept_issue(db, ticket_id)
    if t.house_id != house_id:
        raise HTTPException(status_code=404, detail="Ticket not found in house")
    return t

@router.post("/{ticket_id}/resolve", response_model=IssueOut)
def resolve(house_id: int, ticket_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can resolve")
    t = resolve_issue(db, ticket_id)
    if t.house_id != house_id:
        raise HTTPException(status_code=404, detail="Ticket not found in house")
    return t
