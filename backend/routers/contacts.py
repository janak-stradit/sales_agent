"""API endpoints for Contacts, Personas, and enrichment."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.database import get_db
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.schemas.contact_schemas import ContactCreate, ContactResponse, ContactSearchParams
from backend.schemas.persona_schemas import PersonaResponse
from backend.tasks.data_tasks import enrich_persona_task, bulk_enrich_task

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    """Manually create a contact."""
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/search", response_model=list[ContactResponse])
def search_contacts(
    seniority: str = None,
    min_score: int = None,
    status_filter: str = None,
    department: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Advanced search with filters."""
    query = db.query(Contact)
    if seniority:
        query = query.filter(Contact.seniority == seniority)
    if min_score:
        query = query.filter(Contact.lead_score >= min_score)
    if status_filter:
        query = query.filter(Contact.status == status_filter)
    if department:
        query = query.filter(Contact.department.ilike(f"%{department}%"))
    return query.order_by(Contact.lead_score.desc()).offset(offset).limit(limit).all()


@router.post("/{contact_id}/enrich", status_code=status.HTTP_202_ACCEPTED)
def trigger_enrichment(contact_id: UUID, db: Session = Depends(get_db)):
    """Trigger 3-level persona enrichment (async)."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    task = enrich_persona_task.delay(str(contact_id))
    return {"message": "Enrichment started", "task_id": task.id}


@router.get("/{contact_id}/persona", response_model=PersonaResponse)
def get_persona(contact_id: UUID, db: Session = Depends(get_db)):
    """Get the enriched persona for a contact."""
    persona = db.query(Persona).filter(Persona.contact_id == contact_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found — trigger enrichment first")
    return persona


@router.get("/{contact_id}/reports-chain")
def get_contact_reports_chain(contact_id: UUID, db: Session = Depends(get_db)):
    """Get full reporting chain up to C-Suite (ltree query)."""
    from sqlalchemy import text
    from backend.models.org_hierarchy import OrgHierarchy
    
    hierarchy = db.query(OrgHierarchy).filter(
        OrgHierarchy.contact_id == contact_id
    ).first()

    if not hierarchy or not hierarchy.reports_to_path:
        return {"contact_id": str(contact_id), "chain": []}

    # ltree ancestor query: find all nodes whose path is an ancestor
    result = db.execute(
        text("""
            SELECT c.id, c.first_name, c.last_name, c.title, c.email,
                   oh.level, oh.decision_authority, oh.reports_to_path
            FROM contacts c
            JOIN org_hierarchy oh ON c.id = oh.contact_id
            WHERE oh.reports_to_path @> (
                SELECT reports_to_path FROM org_hierarchy WHERE contact_id = :cid
            )
            ORDER BY oh.level
        """),
        {"cid": str(contact_id)},
    )

    chain = [dict(row._mapping) for row in result]
    return {"contact_id": str(contact_id), "chain": chain}


@router.post("/bulk-enrich", status_code=status.HTTP_202_ACCEPTED)
def trigger_bulk_enrichment(contact_ids: list[UUID], db: Session = Depends(get_db)):
    """Bulk enrich multiple contacts (async)."""
    task = bulk_enrich_task.delay([str(cid) for cid in contact_ids])
    return {"message": f"Bulk enrichment started for {len(contact_ids)} contacts", "task_id": task.id}
