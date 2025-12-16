from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import Role, IssueStatus
from app.schemas.issues import IssueCreate, IssueOut
from app.models.issue_ticket import IssueTicket
from app.crud.issues import create_issue, list_issues, accept_issue, resolve_issue

router = APIRouter(prefix="/issues")

# 1) Client creates ticket -> OPENING
@router.post("", response_model=IssueOut)
def create(payload: IssueCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Only client can create issues")
    if not user.room_no:
        raise HTTPException(status_code=400, detail="Client user has no room_no bound")

    ticket = IssueTicket(
        room_no=user.room_no,
        created_by_user_id=user.id,
        issue_type=payload.issue_type.value,
        details=payload.details,
        status=IssueStatus.opening.value,
    )
    return create_issue(db, ticket)

# Client view previous issues (their own)
@router.get("", response_model=list[IssueOut])
def my_issues(status: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != Role.client.value:
        raise HTTPException(status_code=403, detail="Client only endpoint")
    # optional filter: OPENING / ACCEPTED / RESOLVED
    if status and status not in {"OPENING", "ACCEPTED", "RESOLVED"}:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    return list_issues(db, user_id=user.id, status=status)

# 4) New endpoint: list all issues (owner/admin), filter by status or all
@router.get("/all", response_model=list[IssueOut])
def all_issues(
    status: str = "all",  # opening|accepted|resolved|all
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.owner, Role.admin)),
):
    status_map = {
        "opening": IssueStatus.opening.value,
        "accepted": IssueStatus.accepted.value,
        "resolved": IssueStatus.resolved.value,
        "all": None,
    }
    key = status.lower().strip()
    if key not in status_map:
        raise HTTPException(status_code=400, detail="status must be: opening, accepted, resolved, all")

    return list_issues(db, status=status_map[key])

# 2) Owner/Admin accept -> ACCEPTED
@router.post("/{ticket_id}/accept", response_model=IssueOut)
def accept(ticket_id: int, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    return accept_issue(db, ticket_id)

# 3) Owner resolves -> RESOLVED
@router.post("/{ticket_id}/resolve", response_model=IssueOut)
def resolve(ticket_id: int, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner))):
    return resolve_issue(db, ticket_id)
