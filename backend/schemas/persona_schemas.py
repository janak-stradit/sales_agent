"""Pydantic schemas for Persona and Hierarchy endpoints."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class PersonaResponse(BaseModel):
    id: UUID
    contact_id: UUID

    # Level 1: Demographics & Trajectory
    demographics: Dict[str, Any] = {}
    age_estimate: Optional[int] = None
    tenure_months: Optional[int] = None
    location: Optional[str] = None
    education_degree: Optional[str] = None
    education_institution: Optional[str] = None
    education_grad_year: Optional[int] = None
    prior_company: Optional[str] = None
    prior_title: Optional[str] = None
    prior_duration_months: Optional[int] = None

    # Level 2: Professional Behavior & Intent
    professional_behavior: Dict[str, Any] = {}
    intent_signals: List[Any] = []

    # Level 3: Scraped Personal Touch (Apify / Monid MCP)
    personal_touch: Dict[str, Any] = {}
    is_scraped: bool = True
    is_ai_generated: bool = False
    scraping_source: Optional[str] = None
    scraping_status: Optional[str] = None
    scraped_at: Optional[datetime] = None
    engagement_rate: Optional[str] = None
    communication_style: Optional[str] = None
    professional_interests: List[str] = []
    social_platforms: Dict[str, Any] = {}
    recent_scraped_posts: List[Any] = []

    # AI Outputs & Insights
    ai_summary: Optional[str] = None
    ice_breakers: List[str] = []
    value_proposition: Optional[str] = None
    objections: List[str] = []

    last_enriched: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HierarchyNodeResponse(BaseModel):
    contact_id: UUID
    contact_name: str
    title: Optional[str] = None
    level: int
    decision_authority: Optional[str] = None
    reports_to_path: Optional[str] = None
    children: List["HierarchyNodeResponse"] = []

    model_config = {"from_attributes": True}
