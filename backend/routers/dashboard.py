"""API Router for Executive Dashboard (Tab 1) with Unified Multi-Entity Search."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.dashboard_schemas import (
    DashboardMetricsResponse,
    SeniorityBreakdownItem,
    ScoreDistributionResponse,
    LOBBreakdownItem,
    TopAccountSummaryItem,
    DashboardOverviewResponse,
    DashboardSearchResponse,
)
from backend.services.dashboard_service import (
    get_dashboard_metrics,
    get_seniority_distribution,
    get_score_distribution,
    get_top_lobs,
    get_top_accounts_summary,
    get_dashboard_overview,
    search_dashboard,
)

router = APIRouter()


@router.get("/search", response_model=DashboardSearchResponse)
def search_dashboard_endpoint(
    q: str = Query(..., min_length=1, description="Search term for account name, person name, role/title (VP, Director, CXO), LOB, or signal"),
    limit: int = Query(25, ge=1, le=100, description="Max results per entity category"),
    db: Session = Depends(get_db)
):
    """
    Unified Dashboard Search Bar Engine:
    Searches across:
    - Person / Lead Name (e.g. 'Emily Portney', 'Robin Vince')
    - Role / Seniority / Title (e.g. 'VP', 'Director', 'Head of Asset Servicing', 'CIO')
    - Account Name & Ticker (e.g. 'BNY', 'BK', 'JPMorgan Chase', 'Goldman Sachs')
    - Lines of Business / Segments (e.g. 'Asset Servicing', 'Pershing', 'Custody')
    - Strategic Intent Signals & Topics (e.g. 'Cloud Modernization', 'Snowflake', 'Kafka')
    """
    return search_dashboard(db, query=q, limit=limit)


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_metrics_endpoint(
    account: Optional[str] = Query(None, description="Optional account name or ID to filter metrics"),
    db: Session = Depends(get_db)
):
    """Get high-level summary KPIs (accounts, leads, decision makers, hot/warm/cold counts, revenue covered, signals)."""
    return get_dashboard_metrics(db, account_id=account)


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview_endpoint(
    account: Optional[str] = Query(None, description="Optional account name or ID to filter overview"),
    db: Session = Depends(get_db)
):
    """Get complete dashboard overview with metrics, distributions, top accounts, LOBs, and recent signals."""
    return get_dashboard_overview(db, account_id=account)


@router.get("/seniority-breakdown", response_model=list[SeniorityBreakdownItem])
def get_seniority_breakdown_endpoint(
    account: Optional[str] = Query(None, description="Optional account name to filter breakdown"),
    db: Session = Depends(get_db)
):
    """Get lead distribution across Seniority Tiers (CXO, VP, Director, Tech Lead, Manager)."""
    return get_seniority_distribution(db, account_id=account)


@router.get("/score-distribution", response_model=ScoreDistributionResponse)
def get_score_distribution_endpoint(
    account: Optional[str] = Query(None, description="Optional account name to filter distribution"),
    db: Session = Depends(get_db)
):
    """Get lead distribution across Score Tiers (Hot >=80, Warm 50-79, Cold <50)."""
    return get_score_distribution(db, account_id=account)


@router.get("/top-lobs", response_model=list[LOBBreakdownItem])
def get_top_lobs_endpoint(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    """Get top Lines of Business by executive density and lead score."""
    return get_top_lobs(db, limit=limit)


@router.get("/top-accounts", response_model=list[TopAccountSummaryItem])
def get_top_accounts_endpoint(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get summary overview of top target accounts with key lead and signal metrics."""
    return get_top_accounts_summary(db, limit=limit)
