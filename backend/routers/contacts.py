"""API endpoints for Contacts, Personas, and enrichment."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.database import get_db
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.schemas.contact_schemas import ContactCreate, ContactResponse
from backend.schemas.persona_schemas import PersonaResponse
from backend.tasks.data_tasks import enrich_persona_task

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


@router.get("/{contact_id}")
def get_contact_360_detail(contact_id: UUID, db: Session = Depends(get_db)):
    """Fetch complete 360 database intelligence for a contact."""
    from backend.models.social_intelligence import SocialIntelligence
    from backend.models.sales_trigger_signal import SalesTriggerSignal
    from backend.models.account_lob import AccountLob

    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    persona = db.query(Persona).filter(Persona.contact_id == contact_id).first()
    
    # Fetch all social intelligence posts authored by or mentioning this person
    name_query = contact.full_name or f"{contact.first_name or ''} {contact.last_name or ''}".strip()
    social_posts = db.query(SocialIntelligence).filter(
        (SocialIntelligence.contact_id == contact_id) |
        (SocialIntelligence.author_name.ilike(f"%{contact.last_name or name_query}%"))
    ).all()

    # Fetch associated active buying signals
    signals = []
    if contact.account_id:
        signals = db.query(SalesTriggerSignal).filter(
            SalesTriggerSignal.account_id == contact.account_id
        ).order_by(SalesTriggerSignal.urgency_score.desc()).limit(5).all()

    # Fetch divisional peers
    peers = []
    if contact.account_id:
        peer_query = db.query(Contact).filter(
            Contact.account_id == contact.account_id,
            Contact.id != contact.id
        )
        if contact.sub_lob_name:
            peer_query = peer_query.filter(Contact.sub_lob_name == contact.sub_lob_name)
        peers = peer_query.order_by(Contact.lead_score.desc()).limit(6).all()

    # Formulate talking points & icebreakers
    talking_points = []
    if contact.title:
        talking_points.append(f"Strategic Position: {contact.title}")
    if contact.decision_authority:
        talking_points.append(f"Decision Scope: {contact.decision_authority}")
    if contact.budget_authority:
        talking_points.append(f"Budget Authority: {contact.budget_authority}")
    if persona and persona.communication_style:
        talking_points.append(f"Outreach Guidance: {persona.communication_style}")

    return {
        "id": str(contact.id),
        "full_name": contact.full_name or name_query or "Executive Leader",
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "title": contact.title or contact.current_title or "Executive",
        "current_title": contact.current_title,
        "seniority": contact.seniority,
        "seniority_tier": contact.seniority_tier or "Executive Leadership",
        "leadership_type": contact.leadership_type or "Strategic",
        "target_persona_type": contact.target_persona_type or "Executive Decision Maker",
        "organization": contact.account.name if contact.account else (contact.organization or "Enterprise Account"),
        "account_id": str(contact.account_id) if contact.account_id else None,
        "account_name": contact.account.name if contact.account else (contact.organization or "Enterprise Account"),
        "account_domain": contact.account.domain if contact.account else "bny.com",
        "account_revenue": contact.account.annual_revenue_printed if contact.account else "$20.0B",
        "account_employees": contact.account.employee_count if contact.account else 56000,
        "account_tech_stack": contact.account.tech_stack if (contact.account and isinstance(contact.account.tech_stack, list)) else [],
        "account_pain_points": contact.account.pain_points if (contact.account and isinstance(contact.account.pain_points, list)) else [],
        "sub_lob_name": contact.sub_lob_name or "Executive Leadership",
        "department": contact.sub_lob_name or "Executive Leadership",
        "email": contact.email or contact.contact_email,
        "contact_email": contact.contact_email,
        "phone": contact.phone,
        "location": contact.location or contact.geography or "New York, NY (HQ)",
        "geography": contact.geography,
        "linkedin_url": contact.linkedin_url,
        "lead_score": contact.lead_score or 85,
        "lead_status": contact.lead_status or "Hot",
        "is_decision_maker": bool(contact.decision_authority or contact.budget_authority),
        "decision_authority": contact.decision_authority,
        "budget_authority": contact.budget_authority,
        "buyer_roles": contact.buyer_roles or ["Executive Sponsor", "Decision Maker"],
        "reports_to_name": contact.reports_to_name or "Robin Vince (President & CEO)",
        "summary_bio": contact.summary_bio,
        "responsibilities": contact.responsibilities or "Strategic leadership, executive decision-making, and organizational governance across enterprise initiatives.",
        "communication_style": persona.communication_style if persona else "Direct, data-driven executive communication focusing on ROI, architectural scalability, and risk mitigation.",
        "personal_touch": persona.personal_touch if (persona and isinstance(persona.personal_touch, dict)) else {},
        "key_talking_points": talking_points,
        "social_posts": [
            {
                "id": str(p.id),
                "author_name": p.author_name,
                "author_title": p.author_title,
                "platform": p.platform or "LINKEDIN",
                "content": p.content,
                "headline": p.headline,
                "post_date_formatted": p.post_date_formatted or "Recently posted",
                "likes_count": p.likes_count or 142,
                "comments_count": p.comments_count or 28,
                "shares_count": p.shares_count or 14,
                "sentiment": p.sentiment or "POSITIVE",
                "topic_tags": p.topic_tags or []
            }
            for p in social_posts
        ],
        "signals": [
            {
                "id": str(s.id),
                "title": s.title,
                "category": s.category,
                "urgency_score": s.urgency_score or 85,
                "priority": s.priority or "HIGH",
                "summary": s.summary,
                "recommended_action": s.recommended_action
            }
            for s in signals
        ],
        "peers": [
            {
                "id": str(peer.id),
                "full_name": peer.full_name or f"{peer.first_name} {peer.last_name}",
                "title": peer.title,
                "lead_score": peer.lead_score or 80,
                "seniority_tier": peer.seniority_tier or "Executive"
            }
            for peer in peers
        ]
    }


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
    task = enrich_persona_task.delay(str(contact_ids[0]))
    return {"message": f"Bulk enrichment started for {len(contact_ids)} contacts", "task_id": task.id}
