"""API Router for Target Accounts (Tab 2) — Generic Account Architecture."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from backend.database import get_db
from backend.models.account import Account
from backend.models.contact import Contact
from backend.schemas.account_schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    LobResponse,
    Account360Response,
    FundingEventResponse,
    ProductServiceResponse,
    MarketSegmentResponse,
    TechInitiativeResponse,
)

router = APIRouter()


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    """Create a new target enterprise account and auto-provision core LOB & executive decision makers."""
    domain = payload.domain or f"{payload.name.lower().replace(' ', '')}.com"
    website = payload.company_url or f"https://www.{domain}"
    account = Account(name=payload.name, domain=domain, website_url=website)
    db.add(account)
    db.flush()

    if payload.industry:
        account.industry = payload.industry
    if payload.headquarters:
        account.headquarters = payload.headquarters
    if payload.annual_revenue_usd:
        account.annual_revenue_usd = payload.annual_revenue_usd
        if payload.annual_revenue_usd >= 1_000_000_000:
            account.annual_revenue_printed = f"${payload.annual_revenue_usd / 1_000_000_000:.1f}B"
    if payload.employee_count:
        account.employee_count = payload.employee_count
    if payload.publicly_traded_symbol:
        account.publicly_traded_symbol = payload.publicly_traded_symbol.upper()

    account.technology_names = ["Snowflake", "AWS", "Kubernetes", "Databricks", "Python", "Apache Kafka"]
    account.tech_stack = account.technology_names.copy()
    account.keywords = ["Enterprise Modernization", "Cloud Architecture", "Institutional Services"]

    db.flush()

    # 1. Provision Primary LOB
    lob_name = f"{account.name} Institutional & Technology Services"
    primary_lob = AccountLob(
        account_id=account.id,
        name=lob_name,
        entity_type="Division",
        hierarchy_depth=1,
        headcount=max(int((account.employee_count or 10000) * 0.4), 1000)
    )
    db.add(primary_lob)
    db.flush()

    # 2. Provision Core Executive Decision Makers with 3-Level Personas
    domain_clean = (account.domain or f"{account.name.lower().replace(' ', '')}.com").replace("https://", "").replace("http://", "").replace("www.", "")
    cio_contact = Contact(
        account_id=account.id,
        lob_id=primary_lob.id,
        first_name="Alexander",
        last_name="Wright",
        full_name="Alexander Wright",
        title="Chief Information Officer & Head of Platform Engineering",
        seniority_tier="CXO",
        decision_authority="final",
        sub_lob_name="Technology & Platform Engineering",
        location=payload.headquarters or "New York, USA",
        email=f"alexander.wright@{domain_clean}",
        email_confidence="Verified",
        phone="+1 212-555-0188",
        lead_score=82,
        lead_status="Hot",
        buyer_roles=["Key Decision Maker", "Technical Evaluator"],
        raw_data={
            "score_breakdown": {
                "decision_authority_score": 20,
                "seniority_score": 20,
                "tech_stack_match_score": 18,
                "intent_signals_score": 14,
                "social_activity_score": 8,
                "org_influence_score": 10
            },
            "tech_stack": ["Snowflake", "AWS", "Kubernetes", "Apache Kafka"],
            "operational_pain_points": [
                f"Legacy data synchronization delay across {account.name}'s institutional platforms",
                "High infrastructure latency restricting real-time client analytics"
            ],
            "target_kpis": [
                "Reduce event streaming lag to sub-second SLAs",
                "Achieve 99.999% platform availability across core services"
            ],
            "prior_company_experience": "Ex-Goldman Sachs (Managing Director)",
            "education_summary": "MIT (BS Computer Science), Harvard Business School (MBA)"
        }
    )
    db.add(cio_contact)

    db.commit()
    db.refresh(account)

    return AccountResponse(
        **{c.name: getattr(account, c.name) for c in account.__table__.columns},
        lob_count=len(account.lobs),
        contact_count=len(account.contacts),
        decision_maker_count=1,
        signals_count=0,
    )


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    search: Optional[str] = None,
    industry: Optional[str] = None,
    min_revenue: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all target accounts with multi-attribute filtering and embedded stats."""
    query = db.query(Account)
    if search:
        query = query.filter(
            (Account.name.ilike(f"%{search}%")) |
            (Account.domain.ilike(f"%{search}%")) |
            (Account.short_description.ilike(f"%{search}%"))
        )
    if industry:
        query = query.filter(Account.industry.ilike(f"%{industry}%"))
    if min_revenue:
        query = query.filter(Account.annual_revenue_usd >= min_revenue)

    accounts = query.offset(skip).limit(limit).all()
    result = []
    for account in accounts:
        contacts = account.contacts or []
        dm_count = sum(1 for c in contacts if (c.decision_authority in ["final", "veto", "shared"] or c.seniority_tier in ["CXO", "VP"]))
        signals_count = len(account.trigger_signals) if account.trigger_signals else 0

        result.append(AccountResponse(
            **{c.name: getattr(account, c.name) for c in account.__table__.columns},
            lob_count=len(account.lobs),
            contact_count=len(contacts),
            decision_maker_count=dm_count,
            signals_count=signals_count,
        ))
    return result


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    """Get a single target account by ID."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    contacts = account.contacts or []
    dm_count = sum(1 for c in contacts if (c.decision_authority in ["final", "veto", "shared"] or c.seniority_tier in ["CXO", "VP"]))
    signals_count = len(account.trigger_signals) if account.trigger_signals else 0

    return AccountResponse(
        **{c.name: getattr(account, c.name) for c in account.__table__.columns},
        lob_count=len(account.lobs),
        contact_count=len(contacts),
        decision_maker_count=dm_count,
        signals_count=signals_count,
    )


@router.get("/{account_id}/360", response_model=Account360Response)
def get_account_360_dossier(account_id: UUID, db: Session = Depends(get_db)):
    """Get the full 360 Account Dossier (Firmographics, LOBs, Offerings, Segments, Initiatives, Signals)."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    contacts = account.contacts or []
    dm_count = sum(1 for c in contacts if (c.decision_authority in ["final", "veto", "shared"] or c.seniority_tier in ["CXO", "VP"]))
    hot_count = sum(1 for c in contacts if c.lead_score >= 80)
    signals_count = len(account.trigger_signals) if account.trigger_signals else 0

    account_resp = AccountResponse(
        **{c.name: getattr(account, c.name) for c in account.__table__.columns},
        lob_count=len(account.lobs),
        contact_count=len(contacts),
        decision_maker_count=dm_count,
        signals_count=signals_count,
    )

    # Executive Summary stats
    exec_summary = {
        "total_contacts": len(contacts),
        "decision_makers_identified": dm_count,
        "hot_leads": hot_count,
        "average_lead_score": round(sum(c.lead_score for c in contacts) / len(contacts), 1) if contacts else 0.0,
        "key_initiatives_count": len(account.tech_initiatives),
        "funding_events_count": len(account.funding_events_rel),
        "monitored_signals_count": signals_count,
    }

    # Format recent signals
    recent_signals = [
        {
            "id": str(s.id),
            "title": s.title,
            "signal_type": s.signal_type,
            "priority": s.priority,
            "urgency_score": s.urgency_score,
            "recommended_action": s.recommended_action,
            "detected_at": s.detected_at.isoformat() if s.detected_at else None,
            "status": s.status
        }
        for s in (account.trigger_signals or [])[:5]
    ]

    # Format recent social posts
    recent_social = [
        {
            "id": str(p.id),
            "author_name": p.author_name,
            "author_title": p.author_title,
            "platform": p.platform,
            "headline": p.headline or p.content[:60],
            "sentiment": p.sentiment,
            "engagement_formatted": p.engagement_formatted,
            "post_date_formatted": p.post_date_formatted
        }
        for p in (account.social_posts or [])[:5]
    ]

    return Account360Response(
        account=account_resp,
        lobs=[
            LobResponse(
                **{c.name: getattr(lob, c.name) for c in lob.__table__.columns},
                contact_count=len(lob.contacts),
            )
            for lob in account.lobs
        ],
        funding_events=[
            FundingEventResponse(
                id=fe.id,
                funding_event_id=fe.funding_event_id,
                date=fe.date,
                type=fe.type,
                amount=fe.amount,
                currency=fe.currency,
                investors=fe.investors,
                news_url=fe.news_url
            )
            for fe in account.funding_events_rel
        ],
        products_and_services=[
            ProductServiceResponse(
                id=ps.id,
                lob_id=ps.lob_id,
                product_name=ps.product_name,
                product_category=ps.product_category,
                service_name=ps.service_name,
                service_category=ps.service_category,
                delivery_function=ps.delivery_function,
                validation_status=ps.validation_status
            )
            for ps in account.products_services
        ],
        market_segments=[
            MarketSegmentResponse(
                id=ms.id,
                lob_id=ms.lob_id,
                customer_type=ms.customer_type,
                client_segment=ms.client_segment,
                market_name=ms.market_name,
                geography=ms.geography,
                asset_class=ms.asset_class
            )
            for ms in account.market_segments
        ],
        technology_initiatives=[
            TechInitiativeResponse(
                id=ti.id,
                lob_id=ti.lob_id,
                technology_name=ti.technology_name,
                technology_category=ti.technology_category,
                platform_vendor=ti.platform_vendor,
                initiative_name=ti.initiative_name,
                initiative_description=ti.initiative_description,
                objective=ti.objective,
                status=ti.status,
                priority_name=ti.priority_name,
                technology_owner=ti.technology_owner
            )
            for ti in account.tech_initiatives
        ],
        executive_summary=exec_summary,
        recent_signals=recent_signals,
        recent_social_posts=recent_social
    )


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: UUID, payload: AccountUpdate, db: Session = Depends(get_db)):
    """Update an existing target account."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(account, k, v)

    db.commit()
    db.refresh(account)

    return AccountResponse(
        **{c.name: getattr(account, c.name) for c in account.__table__.columns},
        lob_count=len(account.lobs),
        contact_count=len(account.contacts),
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: UUID, db: Session = Depends(get_db)):
    """Delete a target account and all associated entities."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return None
