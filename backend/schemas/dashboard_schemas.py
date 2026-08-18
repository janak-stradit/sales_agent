"""Pydantic schemas for Executive Dashboard (Tab 1)."""

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
