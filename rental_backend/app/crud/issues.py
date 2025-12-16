from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from app.models.issue_ticket import IssueTicket
from app.models.enums import IssueStatus

def create_issue(db: Session, issue: IssueTicket) -> IssueTicket:
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

def list_issues(
    db: Session,
    *,
    room_no: str | None = None,
    user_id: int | None = None,
    status: str | None = None,  # "OPENING" | "ACCEPTED" | "RESOLVED" | None
) -> list[IssueTicket]:
    q = db.query(IssueTicket)
    if room_no:
        q = q.filter(IssueTicket.room_no == room_no)
    if user_id:
        q = q.filter(IssueTicket.created_by_user_id == user_id)
    if status:
        q = q.filter(IssueTicket.status == status)
    return q.order_by(IssueTicket.created_at.desc()).all()

def accept_issue(db: Session, ticket_id: int) -> IssueTicket:
    t = db.get(IssueTicket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if t.status != IssueStatus.opening.value:
        raise HTTPException(status_code=400, detail="Only OPENING tickets can be accepted")
    t.status = IssueStatus.accepted.value
    t.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t

def resolve_issue(db: Session, ticket_id: int) -> IssueTicket:
    t = db.get(IssueTicket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if t.status != IssueStatus.accepted.value:
        raise HTTPException(status_code=400, detail="Only ACCEPTED tickets can be resolved")
    t.status = IssueStatus.resolved.value
    t.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t
