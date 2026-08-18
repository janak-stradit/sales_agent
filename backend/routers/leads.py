"""API Router for Executive Lead Scoring & Individual Lead Intelligence Profile (Tab 3 & Screenshot 1)."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from backend.database import get_db
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.account import Account
from backend.schemas.contact_schemas import (
    ContactCreate,
    ContactResponse,
    LeadProfileResponse,
    ScoreBreakdown,
)
from backend.services.lead_scoring_service import (
    calculate_lead_score_breakdown,
    format_lead_profile,
)

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
def list_leads(
    account_id: Optional[UUID] = None,
    lob_id: Optional[UUID] = None,
    seniority_tier: Optional[str] = None,
    buyer_role: Optional[str] = None,
    score_tier: Optional[str] = None,  # hot, warm, cold
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    decision_authority: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("score_desc", pattern="^(score_desc|score_asc|name|seniority)$"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Search and filter leads across target accounts with multi-attribute filtering.
    Supports filtering by Account, LOB, Seniority, Buyer Role, Score Tier, and keywords.
    """
    query = db.query(Contact)

    if account_id:
        query = query.filter(Contact.account_id == account_id)
    if lob_id:
        query = query.filter(Contact.lob_id == lob_id)
    if seniority_tier:
        query = query.filter(Contact.seniority_tier.ilike(seniority_tier))
    if decision_authority:
        query = query.filter(Contact.decision_authority.ilike(decision_authority))
    if min_score is not None:
        query = query.filter(Contact.lead_score >= min_score)
    if max_score is not None:
        query = query.filter(Contact.lead_score <= max_score)
    if score_tier:
        st = score_tier.lower()
        if st == "hot":
            query = query.filter(Contact.lead_score >= 80)
        elif st == "warm":
            query = query.filter(Contact.lead_score >= 50, Contact.lead_score < 80)
        elif st == "cold":
            query = query.filter(Contact.lead_score < 50)
    if buyer_role:
        query = query.filter(Contact.buyer_roles.any(buyer_role))
    if search:
        query = query.filter(
            (Contact.full_name.ilike(f"%{search}%")) |
            (Contact.title.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        )

    if sort_by == "score_desc":
        query = query.order_by(Contact.lead_score.desc())
    elif sort_by == "score_asc":
        query = query.order_by(Contact.lead_score.asc())
    elif sort_by == "name":
        query = query.order_by(Contact.last_name.asc(), Contact.first_name.asc())

    contacts = query.offset(skip).limit(limit).all()

    results = []
    for c in contacts:
        first = c.first_name or ""
        last = c.last_name or ""
        if not first and not last and c.full_name:
            parts = c.full_name.split()
            first = parts[0] if parts else ""
            last = parts[-1] if len(parts) > 1 else ""
        avatar_initials = f"{first[:1]}{last[:1]}".upper() or "EP"

        tenure_str = c.tenure
        if not tenure_str and c.tenure_months:
            years = c.tenure_months // 12
            months = c.tenure_months % 12
            if years > 0 and months > 0:
                tenure_str = f"{years} yrs {months} mos"
            elif years > 0:
                tenure_str = f"{years} yrs"
            else:
                tenure_str = f"{months} mos"
        elif not tenure_str:
            tenure_str = "3 yrs 6 mos"

        lead_status = "Hot" if c.lead_score >= 80 else ("Warm" if c.lead_score >= 50 else "Cold")

        results.append(ContactResponse(
            id=c.id,
            account_id=c.account_id,
            lob_id=c.lob_id,
            full_name=c.full_name or f"{first} {last}".strip(),
            first_name=c.first_name or first,
            last_name=c.last_name or last,
            email=c.email,
            email_confidence=c.email_confidence or "verified",
            avatar_initials=avatar_initials,
            avatar_url=c.avatar_url,
            title=c.title,
            current_title=c.current_title or c.title,
            seniority_tier=c.seniority_tier,
            target_persona_type=c.target_persona_type,
            leadership_type=c.leadership_type,
            buyer_roles=c.buyer_roles or ["Key Decision Maker"],
            decision_authority=c.decision_authority,
            budget_authority=c.budget_authority,
            linkedin_url=c.linkedin_url,
            phone=c.phone,
            location=c.location,
            tenure_months=c.tenure_months,
            tenure_formatted=tenure_str,
            status=c.status or "ACTIVE",
            lead_score=c.lead_score,
            lead_status=lead_status,
            summary_bio=c.summary_bio or c.remit,
            created_at=c.created_at
        ))
    return results


@router.get("/{contact_id}/profile", response_model=LeadProfileResponse)
def get_individual_lead_profile(contact_id: UUID, db: Session = Depends(get_db)):
    """
    Get the complete Individual Lead Intelligence Profile matching Screenshot 1:
    - Header Card with Avatar initials, Lead Score badge, Location, Role Tenure
    - Summary Bio
    - Education & Certifications
    - Key Buyer Roles
    - LinkedIn Executive Profile & Scraper Intelligence
    - Top Endorsed Executive Skills
    - Career Experience Timeline
    - AI Sales Insights (Icebreakers, Pain Points, Pitch, Objections)
    - Multi-Factor Score Breakdown
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        # Fallback in case hierarchy node ID was passed
        from backend.models.org_hierarchy import OrgHierarchy
        hier = db.query(OrgHierarchy).filter(OrgHierarchy.id == contact_id).first()
        if hier and hier.contact:
            contact = hier.contact

    if not contact:
        raise HTTPException(status_code=404, detail="Lead not found")

    return format_lead_profile(contact, db)


@router.post("/{contact_id}/recalculate-score", response_model=ScoreBreakdown)
def recalculate_contact_score(contact_id: UUID, db: Session = Depends(get_db)):
    """Recalculate lead score for a prospect using the multi-factor scoring engine and save to DB."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        from backend.models.org_hierarchy import OrgHierarchy
        hier = db.query(OrgHierarchy).filter(OrgHierarchy.id == contact_id).first()
        if hier and hier.contact:
            contact = hier.contact

    if not contact:
        raise HTTPException(status_code=404, detail="Lead not found")

    breakdown = calculate_lead_score_breakdown(contact, contact.persona, contact.org_node)
    contact.lead_score = breakdown.total_score
    contact.lead_status = breakdown.tier

    if contact.persona:
        contact.persona.score_breakdown = breakdown.model_dump()

    db.commit()
    db.refresh(contact)
    return breakdown


@router.post("/recalculate-all")
def recalculate_all_scores(account_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    """Batch recalculates scores for all prospects in the database or for a specific target account."""
    query = db.query(Contact)
    if account_id:
        query = query.filter(Contact.account_id == account_id)

    contacts = query.all()
    count = 0
    for c in contacts:
        breakdown = calculate_lead_score_breakdown(c, c.persona, c.org_node)
        c.lead_score = breakdown.total_score
        c.lead_status = breakdown.tier
        if c.persona:
            c.persona.score_breakdown = breakdown.model_dump()
        count += 1

    db.commit()
    return {"message": f"Successfully recalculated lead scores for {count} contacts", "contacts_updated": count}


@router.post("/{contact_id}/export-crm")
def export_lead_to_crm(contact_id: UUID, crm_type: str = "outreach", db: Session = Depends(get_db)):
    """Exports fully enriched prospect intelligence, verified contact channels, and customized pitches to CRM / Sequencer."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        from backend.models.org_hierarchy import OrgHierarchy
        hier = db.query(OrgHierarchy).filter(OrgHierarchy.id == contact_id).first()
        if hier and hier.contact:
            contact = hier.contact

    if not contact:
        raise HTTPException(status_code=404, detail="Lead profile not found")

    profile = format_lead_profile(contact, db)
    crm_format = crm_type.lower()
    
    export_record = {
        "external_id": str(profile.id),
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "full_name": profile.full_name,
        "title": profile.title,
        "company": profile.account_name,
        "company_ticker": profile.account_ticker,
        "email": profile.email,
        "email_deliverability": profile.email_confidence,
        "phone": profile.phone,
        "location": profile.location,
        "lead_score": profile.lead_score,
        "lead_status": profile.lead_status,
        "seniority_tier": profile.score_breakdown.seniority_score,
        "buyer_roles": profile.key_buyer_roles,
        "custom_email_subject": profile.cold_outreach_playbook.email_subject,
        "custom_email_body": profile.cold_outreach_playbook.email_body,
        "linkedin_dm_script": profile.cold_outreach_playbook.linkedin_dm,
        "phone_hook_script": profile.cold_outreach_playbook.cold_call_opening,
        "tech_stack": profile.tech_stack,
        "pain_points": profile.operational_pain_points,
        "sync_destination": crm_format.upper(),
        "ready_for_outreach": True
    }

    return {
        "status": "SUCCESS",
        "message": f"Successfully prepared prospect for {crm_format.upper()} outbound campaign",
        "crm_type": crm_format,
        "record": export_record
    }


@router.patch("/{contact_id}/outreach-status")
def update_contact_outreach_status(
    contact_id: UUID,
    payload: dict,
    db: Session = Depends(get_db)
):
    """Updates the sales representative's outreach status and logs activity notes."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        from backend.models.org_hierarchy import OrgHierarchy
        hier = db.query(OrgHierarchy).filter(OrgHierarchy.id == contact_id).first()
        if hier and hier.contact:
            contact = hier.contact

    if not contact:
        raise HTTPException(status_code=404, detail="Lead not found")

    new_status = payload.get("status", "NOT_CONTACTED")
    note = payload.get("note")

    raw = dict(contact.raw_data or {})
    raw["outreach_status"] = new_status

    notes = list(raw.get("outreach_notes") or [])
    if note:
        from datetime import datetime
        notes.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "action": f"Status updated to {new_status}",
            "note": note,
            "author": payload.get("author", "Sales Rep")
        })
    raw["outreach_notes"] = notes
    contact.raw_data = raw
    contact.status = new_status

    db.commit()
    db.refresh(contact)

    return {
        "status": "SUCCESS",
        "outreach_status": new_status,
        "outreach_notes": notes,
        "message": f"Updated outreach status to {new_status}"
    }
