"""Pydantic schemas for Contact, Persona, and Lead Intelligence Profile."""

from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    account_id: UUID
    lob_id: Optional[UUID] = None
    email: Optional[str] = None
    email_confidence: Optional[str] = "verified"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    seniority_tier: Optional[str] = "Director"
    target_persona_type: Optional[str] = "Decision Maker"
    decision_authority: Optional[str] = "shared"
    budget_authority: Optional[str] = "partial"
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    tenure_months: Optional[int] = None
    lead_score: Optional[int] = 50


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    email: Optional[str] = None
    title: Optional[str] = None
    seniority_tier: Optional[str] = None
    decision_authority: Optional[str] = None
    lead_score: Optional[int] = None
    status: Optional[str] = None


class ContactResponse(BaseModel):
    id: UUID
    account_id: UUID
    lob_id: Optional[UUID] = None
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    email_confidence: Optional[str] = "verified"
    avatar_initials: str
    avatar_url: Optional[str] = None
    title: str
    current_title: Optional[str] = None
    seniority_tier: Optional[str] = None
    target_persona_type: Optional[str] = None
    leadership_type: Optional[str] = None
    buyer_roles: List[str] = ["Key Decision Maker"]
    decision_authority: Optional[str] = None
    budget_authority: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    tenure_months: Optional[int] = None
    tenure_formatted: Optional[str] = None
    status: str = "ACTIVE"
    outreach_status: Optional[str] = "NOT_CONTACTED"
    lead_score: int
    lead_status: str  # Hot, Warm, Cold
    summary_bio: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Detailed Individual Lead Intelligence Profile Models ──

class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None
    certifications: Optional[List[str]] = []
    formatted: Optional[str] = None


class CareerTimelineItem(BaseModel):
    company: str
    title: str
    role_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = "Present"
    duration_formatted: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False


class LinkedInIntelligence(BaseModel):
    linkedin_url: Optional[str] = None
    headline: Optional[str] = None
    follower_count: int = 0
    connection_count: int = 0
    scraping_status: str = "COMPLETED"
    scraped_at_formatted: Optional[str] = None
    recent_posts_count: int = 0
    profile_summary: Optional[str] = None


class ScrapedPostItem(BaseModel):
    platform: str = "LinkedIn"
    date: Optional[str] = None
    topic_focus: Optional[str] = None
    headline: Optional[str] = None
    content: Optional[str] = None
    engagement: Optional[str] = None
    url: Optional[str] = None


class ColdOutreachPlaybook(BaseModel):
    recommended_angle: str
    email_subject: str
    email_body: str
    linkedin_dm: str
    cold_call_opening: str
    value_proposition: str
    objection_handling: Dict[str, str] = {}


class AISalesInsights(BaseModel):
    summary: Optional[str] = None
    ice_breakers: List[str] = []
    value_proposition: Optional[str] = None
    pain_points: List[str] = []
    kpis: List[str] = []
    objections: List[str] = []
    communication_style: Optional[str] = "data-driven & architectural"


class ScoreBreakdown(BaseModel):
    decision_authority_score: int = 0
    seniority_score: int = 0
    tech_stack_match_score: int = 0
    intent_signals_score: int = 0
    social_activity_score: int = 0
    org_influence_score: int = 0
    total_score: int = 0
    max_score: int = 100
    tier: str = "Warm"


class LeadProfileResponse(BaseModel):
    # Header Information
    id: UUID
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_initials: str
    avatar_url: Optional[str] = None
    title: str
    current_title: Optional[str] = None
    account_id: UUID
    account_name: Optional[str] = None
    account_ticker: Optional[str] = None
    lob_id: Optional[UUID] = None
    lob_name: Optional[str] = None
    lead_score: int
    lead_status: str  # Hot, Warm, Cold
    email: Optional[str] = None
    email_confidence: Optional[str] = "verified"
    phone: Optional[str] = None
    location: Optional[str] = None
    tenure_formatted: Optional[str] = None
    tenure_months: Optional[int] = None

    # Summary Bio Narrative
    summary_bio: Optional[str] = None

    # ── Level 1: Demographics & Career Trajectory ──
    education_and_certifications: List[EducationItem] = []
    education_summary: Optional[str] = "N/A"
    top_endorsed_skills: List[str] = []
    career_experience_timeline: List[CareerTimelineItem] = []
    prior_company_experience: Optional[str] = None

    # ── Level 2: Professional Behavior & Buying Context ──
    key_buyer_roles: List[str] = ["Key Decision Maker"]
    decision_authority: Optional[str] = "final"
    budget_authority: Optional[str] = "full"
    tech_stack: List[str] = []
    operational_pain_points: List[str] = []
    target_kpis: List[str] = []
    active_initiatives: List[str] = []

    # ── Level 3: Scraped Personal Touch & Thought Leadership ──
    linkedin_intelligence: LinkedInIntelligence
    communication_style: Optional[str] = "Direct, ROI-focused & architectural"
    professional_interests: List[str] = []
    recent_scraped_posts: List[ScrapedPostItem] = []

    # ── AI Insights & Actionable Cold Outreach Playbook ──
    ai_insights: AISalesInsights
    cold_outreach_playbook: ColdOutreachPlaybook

    # ── Rec 2: 72-Hour Recent Post Trigger Hook ──
    recent_72h_post_hook: Optional[Dict[str, Any]] = None

    # ── Rec 3: Buying Committee Consensus & Multi-Threading ──
    buying_committee_consensus: List[Dict[str, Any]] = []

    # ── Rec 4: Interactive Objection Handling Simulator ──
    interactive_objections: List[Dict[str, Any]] = []

    # ── 14-Day Outreach Cadence & Activity Tracker (Rec 1, 2, 3) ──
    cadence_steps: List[Dict[str, Any]] = []
    outreach_status: Optional[str] = "NOT_CONTACTED"
    outreach_notes: List[Dict[str, Any]] = []

    # ── Score Breakdown & Explainability Engine ──
    score_breakdown: ScoreBreakdown
