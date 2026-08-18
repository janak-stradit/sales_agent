"""API endpoints for LOBs and hierarchy extraction."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.database import get_db
from backend.models.account_lob import AccountLob
from backend.schemas.account_schemas import LobCreate, LobResponse
from backend.tasks.data_tasks import extract_org_chart_task

router = APIRouter()


@router.post("/", response_model=LobResponse, status_code=status.HTTP_201_CREATED)
def create_lob(payload: LobCreate, db: Session = Depends(get_db)):
    """Manually create a LOB."""
    lob = AccountLob(**payload.model_dump())
    db.add(lob)
    db.commit()
    db.refresh(lob)
    return LobResponse(
        **{c.name: getattr(lob, c.name) for c in lob.__table__.columns},
        contact_count=0,
    )


@router.post("/{lob_id}/extract-hierarchy", status_code=status.HTTP_202_ACCEPTED)
def trigger_hierarchy_extraction(lob_id: UUID, db: Session = Depends(get_db)):
    """Trigger async org chart extraction for a LOB."""
    lob = db.query(AccountLob).filter(AccountLob.id == lob_id).first()
    if not lob:
        raise HTTPException(status_code=404, detail="LOB not found")
    task = extract_org_chart_task.delay(str(lob_id))
    return {"message": "Hierarchy extraction started", "task_id": task.id}


@router.get("/{lob_id}/hierarchy")
def get_lob_hierarchy(lob_id: UUID, level: int = None, db: Session = Depends(get_db)):
    """View the org hierarchy for a LOB, optionally filtered by level."""
    from backend.models.org_hierarchy import OrgHierarchy
    from backend.models.contact import Contact

    query = (
        db.query(Contact, OrgHierarchy)
        .join(OrgHierarchy, Contact.id == OrgHierarchy.contact_id)
        .filter(Contact.lob_id == lob_id)
    )
    if level:
        query = query.filter(OrgHierarchy.level == level)

    query = query.order_by(OrgHierarchy.level)
    results = query.all()

    return [
        {
            "contact_id": str(c.id),
            "name": c.full_name,
            "title": c.title,
            "email": c.email,
            "level": h.level,
            "decision_authority": h.decision_authority,
            "reports_to_path": h.reports_to_path,
            "manager_id": str(h.manager_id) if h.manager_id else None,
        }
        for c, h in results
    ]
