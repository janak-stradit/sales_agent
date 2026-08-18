"""Pydantic schemas for Executive Dashboard (Tab 1) & Unified Global Search."""

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class SeniorityBreakdownItem(BaseModel):
    tier: str
    count: int
    percentage: float
    hot_count: int
    decision_maker_count: int


class ScoreDistributionResponse(BaseModel):
    hot_count: int
    warm_count: int
    cold_count: int
    total_count: int
    average_score: float
    hot_percentage: float
    warm_percentage: float
    cold_percentage: float


class LOBBreakdownItem(BaseModel):
    lob_id: UUID
    lob_name: str
    account_name: str
    entity_type: str
    headcount: Optional[int] = None
    lead_count: int
    decision_maker_count: int
    avg_lead_score: float


class TopAccountSummaryItem(BaseModel):
    account_id: UUID
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue_usd: Optional[int] = None
    employee_count: Optional[int] = None
    lob_count: int
    lead_count: int
    decision_maker_count: int
    hot_lead_count: int
    signal_count: int


class DashboardMetricsResponse(BaseModel):
    total_target_accounts: int
    total_leads_identified: int
    decision_makers_count: int
    hot_leads_count: int
    warm_leads_count: int
    cold_leads_count: int
    total_revenue_covered_usd: int
    total_revenue_formatted: str
    total_signals_detected: int
    active_signals_count: int
    average_lead_score: float


class DashboardOverviewResponse(BaseModel):
    metrics: DashboardMetricsResponse
    seniority_distribution: List[SeniorityBreakdownItem]
    score_distribution: ScoreDistributionResponse
    top_lobs: List[LOBBreakdownItem]
    top_accounts: List[TopAccountSummaryItem]
    top_decision_makers: List[Dict[str, Any]] = []
    segment_revenues: List[Dict[str, Any]] = []
    recent_signals: List[Dict[str, Any]]
    recent_pipeline_runs: List[Dict[str, Any]]


# ── Unified Dashboard Search Schemas ─────────────────────────────────────────

class DashboardContactSearchResult(BaseModel):
    id: UUID
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str
    seniority_tier: str
    department: Optional[str] = None
    account_name: str
    account_id: UUID
    lead_score: int
    lead_status: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_initials: str
    buyer_roles: List[str] = []
    decision_authority: Optional[str] = None
    summary_bio: Optional[str] = None
    linkedin_url: Optional[str] = None


class DashboardAccountSearchResult(BaseModel):
    id: UUID
    name: str
    domain: Optional[str] = None
    publicly_traded_symbol: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue_formatted: Optional[str] = None
    employee_count: Optional[int] = None
    headquarters: Optional[str] = None
    leads_count: int = 0
    lobs_count: int = 0


class DashboardLOBSearchResult(BaseModel):
    id: UUID
    name: str
    account_name: str
    account_id: UUID
    entity_type: str
    revenue_printed: Optional[str] = None
    headcount: Optional[int] = None
    short_description: Optional[str] = None


class DashboardSignalSearchResult(BaseModel):
    id: UUID
    title: str
    account_name: str
    account_id: UUID
    category: Optional[str] = None
    priority: str
    urgency_score: int
    status: str
    recommended_action: Optional[str] = None


class DashboardPostSearchResult(BaseModel):
    id: UUID
    author_name: str
    author_title: Optional[str] = None
    account_name: Optional[str] = None
    account_id: UUID
    contact_id: Optional[UUID] = None
    platform: str = "LINKEDIN"
    content: str
    headline: Optional[str] = None
    post_date_formatted: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    sentiment: str = "POSITIVE"
    topic_tags: List[str] = []


class DashboardSearchResponse(BaseModel):
    query: str
    total_matches: int
    contacts: List[DashboardContactSearchResult] = []
    accounts: List[DashboardAccountSearchResult] = []
    lobs: List[DashboardLOBSearchResult] = []
    signals: List[DashboardSignalSearchResult] = []
    posts: List[DashboardPostSearchResult] = []
