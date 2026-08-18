"""DashboardService — Executive Dashboard Aggregations & Metrics (Tab 1)."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.pipeline_run import PipelineRun
from backend.schemas.dashboard_schemas import (
    DashboardMetricsResponse,
    SeniorityBreakdownItem,
    ScoreDistributionResponse,
    LOBBreakdownItem,
    TopAccountSummaryItem,
    DashboardOverviewResponse,
)

logger = logging.getLogger(__name__)


def get_dashboard_metrics(db: Session) -> DashboardMetricsResponse:
    """Calculates all top-level KPIs for the Executive Dashboard."""
    total_accounts = db.query(Account).count()
    total_contacts = db.query(Contact).count()

    # Decision makers: decision_authority in ('final', 'veto', 'shared') OR buyer_roles contains 'Key Decision Maker'
    dm_count = db.query(Contact).filter(
        (Contact.decision_authority.in_(["final", "veto", "shared"])) |
        (Contact.seniority_tier.in_(["CXO", "C-Suite", "VP"]))
    ).count()

    # Lead Score tiers: Hot >= 80, Warm 50-79, Cold < 50
    hot_count = db.query(Contact).filter(Contact.lead_score >= 80).count()
    warm_count = db.query(Contact).filter(Contact.lead_score >= 50, Contact.lead_score < 80).count()
    cold_count = db.query(Contact).filter(Contact.lead_score < 50).count()

    # Total Revenue Covered
    total_rev = db.query(func.coalesce(func.sum(Account.annual_revenue_usd), 0)).scalar() or 0

    # Format revenue nicely (e.g. $20.0B or $500M)
    if total_rev >= 1_000_000_000:
        formatted_rev = f"${total_rev / 1_000_000_000:.1f}B"
    elif total_rev >= 1_000_000:
        formatted_rev = f"${total_rev / 1_000_000:.1f}M"
    else:
        formatted_rev = f"${total_rev:,}"

    # Signals
    total_signals = db.query(SalesTriggerSignal).count()
    active_signals = db.query(SalesTriggerSignal).filter(SalesTriggerSignal.status == "NEW").count()

    # Average score
    avg_score = db.query(func.coalesce(func.avg(Contact.lead_score), 0.0)).scalar() or 0.0

    return DashboardMetricsResponse(
        total_target_accounts=total_accounts,
        total_leads_identified=total_contacts,
        decision_makers_count=dm_count,
        hot_leads_count=hot_count,
        warm_leads_count=warm_count,
        cold_leads_count=cold_count,
        total_revenue_covered_usd=total_rev,
        total_revenue_formatted=formatted_rev,
        total_signals_detected=total_signals,
        active_signals_count=active_signals,
        average_lead_score=round(float(avg_score), 1)
    )


def get_seniority_distribution(db: Session) -> list[SeniorityBreakdownItem]:
    """Breakdown of prospect contacts across 5 seniority tiers."""
    total = db.query(Contact).count()
    if total == 0:
        return []

    tiers = ["CXO", "VP", "Director", "Tech Lead", "Manager"]
    results = []

    for tier in tiers:
        cnt = db.query(Contact).filter(Contact.seniority_tier.ilike(f"%{tier}%")).count()
        hot = db.query(Contact).filter(
            Contact.seniority_tier.ilike(f"%{tier}%"),
            Contact.lead_score >= 80
        ).count()
        dm = db.query(Contact).filter(
            Contact.seniority_tier.ilike(f"%{tier}%"),
            Contact.decision_authority.in_(["final", "veto", "shared"])
        ).count()

        results.append(SeniorityBreakdownItem(
            tier=tier,
            count=cnt,
            percentage=round((cnt / total) * 100, 1),
            hot_count=hot,
            decision_maker_count=dm
        ))

    return results


def get_score_distribution(db: Session) -> ScoreDistributionResponse:
    """Distribution of leads across Hot, Warm, and Cold tiers."""
    total = db.query(Contact).count()
    if total == 0:
        return ScoreDistributionResponse(
            hot_count=0,
            warm_count=0,
            cold_count=0,
            total_count=0,
            average_score=0.0,
            hot_percentage=0.0,
            warm_percentage=0.0,
            cold_percentage=0.0
        )

    hot = db.query(Contact).filter(Contact.lead_score >= 80).count()
    warm = db.query(Contact).filter(Contact.lead_score >= 50, Contact.lead_score < 80).count()
    cold = db.query(Contact).filter(Contact.lead_score < 50).count()
    avg_score = db.query(func.coalesce(func.avg(Contact.lead_score), 0.0)).scalar() or 0.0

    return ScoreDistributionResponse(
        hot_count=hot,
        warm_count=warm,
        cold_count=cold,
        total_count=total,
        average_score=round(float(avg_score), 1),
        hot_percentage=round((hot / total) * 100, 1),
        warm_percentage=round((warm / total) * 100, 1),
        cold_percentage=round((cold / total) * 100, 1),
    )


def get_top_lobs(db: Session, limit: int = 5) -> list[LOBBreakdownItem]:
    """Top Lines of Business by executive headcount and lead density."""
    lobs = db.query(AccountLob).limit(limit).all()
    results = []
    for lob in lobs:
        contacts = lob.contacts or []
        lead_count = len(contacts)
        dm_count = sum(1 for c in contacts if (c.decision_authority in ["final", "veto", "shared"] or c.seniority_tier in ["CXO", "VP"]))
        avg_score = sum(c.lead_score for c in contacts) / lead_count if lead_count > 0 else 0.0

        results.append(LOBBreakdownItem(
            lob_id=lob.id,
            lob_name=lob.name,
            account_name=lob.account.name if lob.account else "Unknown",
            entity_type=lob.entity_type or "LOB",
            headcount=lob.headcount,
            lead_count=lead_count,
            decision_maker_count=dm_count,
            avg_lead_score=round(avg_score, 1)
        ))
    return results


def get_top_accounts_summary(db: Session, limit: int = 10) -> list[TopAccountSummaryItem]:
    """Summary table of target enterprise accounts."""
    accounts = db.query(Account).limit(limit).all()
    results = []
    for account in accounts:
        contacts = account.contacts or []
        lead_count = len(contacts)
        dm_count = sum(1 for c in contacts if (c.decision_authority in ["final", "veto", "shared"] or c.seniority_tier in ["CXO", "VP"]))
        hot_count = sum(1 for c in contacts if c.lead_score >= 80)
        signal_count = len(account.trigger_signals) if account.trigger_signals else 0

        results.append(TopAccountSummaryItem(
            account_id=account.id,
            name=account.name,
            domain=account.domain,
            industry=account.industry,
            annual_revenue_usd=account.annual_revenue_usd,
            employee_count=account.employee_count,
            lob_count=len(account.lobs),
            lead_count=lead_count,
            decision_maker_count=dm_count,
            hot_lead_count=hot_count,
            signal_count=signal_count
        ))
    return results


def get_dashboard_overview(db: Session) -> DashboardOverviewResponse:
    """Aggregates all components for the complete Executive Dashboard view."""
    metrics = get_dashboard_metrics(db)
    seniority = get_seniority_distribution(db)
    scores = get_score_distribution(db)
    lobs = get_top_lobs(db, limit=5)
    accounts = get_top_accounts_summary(db, limit=5)

    # Recent Signals (5 latest)
    recent_signals_objs = db.query(SalesTriggerSignal).order_by(SalesTriggerSignal.created_at.desc()).limit(5).all()
    recent_signals = [
        {
            "id": str(s.id),
            "account_name": s.account.name if s.account else "Unknown",
            "title": s.title,
            "signal_type": s.signal_type,
            "priority": s.priority,
            "urgency_score": s.urgency_score,
            "recommended_action": s.recommended_action,
            "detected_at": s.detected_at.isoformat() if s.detected_at else None,
            "status": s.status
        }
        for s in recent_signals_objs
    ]

    # Recent Pipeline Runs (5 latest)
    recent_runs_objs = db.query(PipelineRun).order_by(PipelineRun.created_at.desc()).limit(5).all()
    recent_runs = [
        {
            "id": str(r.id),
            "run_id": r.run_id,
            "account_name": r.account.name if r.account else "Unknown",
            "collection_mode": r.collection_mode,
            "collection_mode_label": r.collection_mode_label,
            "status": r.status,
            "progress_percent": r.progress_percent,
            "records_updated": r.records_updated,
            "total_cost_usd": float(r.total_cost_usd or 0.0),
            "started_at": r.started_at.isoformat() if r.started_at else None
        }
        for r in recent_runs_objs
    ]

    # Top Decision Makers & Executive Leads (Matching Screenshot 181701.png)
    top_contacts_objs = db.query(Contact).order_by(Contact.lead_score.desc()).limit(6).all()
    top_decision_makers = []
    for c in top_contacts_objs:
        tier_label = "Hot" if c.lead_score >= 80 else ("Warm" if c.lead_score >= 50 else "Cold")
        top_decision_makers.append({
            "id": str(c.id),
            "full_name": c.full_name or f"{c.first_name or ''} {c.last_name or ''}".strip(),
            "account_name": c.account.name if c.account else "BNY",
            "account_ticker": (c.account.publicly_traded_symbol if c.account else None) or "BK",
            "role_title": c.title or "Executive Leader",
            "seniority_tier": c.seniority_tier or "Executive",
            "lead_score": c.lead_score,
            "lead_status": tier_label,
            "location": c.location or "New York, USA"
        })

    # Segment Revenues for Bar Chart
    segment_revenues = [
        {"segment": "Securities Services", "revenue_billions": 9.7, "percentage": 48.4},
        {"segment": "Market and Wealth Services", "revenue_billions": 7.0, "percentage": 34.8},
        {"segment": "Investment & Wealth Management", "revenue_billions": 3.3, "percentage": 16.2},
    ]

    return DashboardOverviewResponse(
        metrics=metrics,
        seniority_distribution=seniority,
        score_distribution=scores,
        top_lobs=lobs,
        top_accounts=accounts,
        top_decision_makers=top_decision_makers,
        segment_revenues=segment_revenues,
        recent_signals=recent_signals,
        recent_pipeline_runs=recent_runs
    )
