"""Pydantic schemas for Organizational Hierarchy (Tab 4)."""

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID


class HierarchyTreeNodeResponse(BaseModel):
    id: UUID
    contact_id: UUID
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_initials: Optional[str] = None
    location: Optional[str] = None
    seniority_tier: str
    target_persona_type: Optional[str] = None
    decision_authority: str
    budget_authority: Optional[str] = None
    lead_score: int
    lead_status: str
    level: int
    reports_to_path: Optional[str] = None
    manager_id: Optional[UUID] = None
    manager_name: Optional[str] = None
    lob_id: UUID
    lob_name: Optional[str] = None
    direct_reports_count: int = 0
    total_subtree_count: int = 0
    children: List["HierarchyTreeNodeResponse"] = []


class SpanOfControlMetricsResponse(BaseModel):
    account_id: UUID
    account_name: Optional[str] = None
    max_depth: int
    total_nodes: int
    average_span_of_control: float
    level_distribution: Dict[int, int]
    decision_power_distribution: Dict[str, int]
    top_decision_nodes: List[Dict[str, Any]]


class ReportingChainNode(BaseModel):
    contact_id: UUID
    full_name: str
    title: str
    level: int
    decision_authority: str
    budget_authority: Optional[str] = None
    reports_to_path: Optional[str] = None


class ReportingChainResponse(BaseModel):
    contact_id: UUID
    full_name: str
    title: str
    upward_chain: List[ReportingChainNode]
    direct_reports: List[ReportingChainNode]
    total_subordinates_count: int
