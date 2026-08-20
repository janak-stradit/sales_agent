"""Pydantic schemas for Sales AI Chatbot API."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── Structured Person Result for Chatbot ──────────
class ChatbotPersonResult(BaseModel):
    id: UUID
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str
    seniority: Optional[str] = None
    seniority_tier: Optional[str] = None
    role: Optional[str] = None
    organization: str
    account_id: Optional[UUID] = None
    sub_lob_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_score: Optional[int] = 75
    lead_status: Optional[str] = "Hot"
    is_decision_maker: Optional[bool] = False
    decision_authority: Optional[str] = None
    budget_authority: Optional[str] = None
    reports_to_name: Optional[str] = None
    summary_bio: Optional[str] = None
    responsibilities: Optional[str] = None
    communication_style: Optional[str] = None
    personal_touch: Optional[Dict[str, Any]] = None
    key_talking_points: Optional[List[str]] = Field(default_factory=list)


# ── Structured Organization Result for Chatbot ─────
class ChatbotOrganizationResult(BaseModel):
    id: UUID
    name: str
    domain: str
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    market_cap: Optional[str] = None
    headquarters: Optional[str] = None
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    pain_points: Optional[List[str]] = Field(default_factory=list)
    total_executives: Optional[int] = 0
    total_lobs: Optional[int] = 0


# ── Structured LOB / Business Unit Result ──────────
class ChatbotLOBResult(BaseModel):
    id: UUID
    name: str
    account_name: str
    node_type: Optional[str] = None
    business_head: Optional[str] = None
    tech_leader: Optional[str] = None
    tech_leader_title: Optional[str] = None
    confidence_level: Optional[str] = "High"
    key_platforms: Optional[str] = None
    intelligence_notes: Optional[str] = None


# ── Structured Signal Result ───────────────────────
class ChatbotSignalResult(BaseModel):
    id: UUID
    title: str
    organization: str
    signal_type: Optional[str] = None
    category: Optional[str] = None
    urgency_score: Optional[int] = 85
    priority: Optional[str] = "HIGH"
    summary: Optional[str] = None
    recommended_action: Optional[str] = None
    source_name: Optional[str] = None


# ── Structured Social Post Result ──────────────────
class ChatbotPostResult(BaseModel):
    id: UUID
    author_name: str
    author_title: Optional[str] = None
    platform: Optional[str] = "LINKEDIN"
    content: str
    headline: Optional[str] = None
    post_date_formatted: Optional[str] = None
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    sentiment: Optional[str] = "POSITIVE"
    sentiment_score: Optional[float] = 0.5
    topic_tags: Optional[List[str]] = Field(default_factory=list)


# ── Chatbot Request Payload ────────────────────────
class ChatbotQueryRequest(BaseModel):
    message: Optional[str] = Field(None, description="Natural language question or search prompt from sales rep")
    query: Optional[str] = Field(None, description="Alias for message parameter")
    session_id: Optional[str] = Field("default_session", description="Conversation session ID for multi-turn context and coreference resolution")
    account_id: Optional[UUID] = Field(None, description="Optional account ID to constrain search to a specific organization")
    account_name: Optional[str] = Field(None, description="Optional account name filter (e.g. 'BNY', 'Goldman Sachs')")
    include_dossier: bool = Field(True, description="Include deep persona & executive dossier cards")
    limit: int = Field(10, ge=1, le=50, description="Max matched entities to return")

    def get_query_text(self) -> str:
        return (self.message or self.query or "").strip()


# ── Chatbot Conversational Response ────────────────
class ChatbotQueryResponse(BaseModel):
    query: str
    reply: str
    response: Optional[str] = None  # Frontend compatibility alias
    executive_summary: Optional[str] = None  # 3-4 line quick executive briefing
    intent_detected: str  # e.g. "social_intelligence", "person_lookup", "role_search", "org_lookup", "signal_search", "hierarchy_lookup"
    session_id: Optional[str] = "default_session"
    cache_hit: bool = False
    latency_ms: Optional[float] = None
    processing_steps: List[str] = Field(default_factory=list)  # Visual process tags / thoughts
    matched_people_count: int = 0
    matched_organizations_count: int = 0
    matched_signals_count: int = 0
    matched_posts_count: int = 0
    people: List[ChatbotPersonResult] = Field(default_factory=list)
    posts: List[ChatbotPostResult] = Field(default_factory=list)
    organizations: List[ChatbotOrganizationResult] = Field(default_factory=list)
    lobs: List[ChatbotLOBResult] = Field(default_factory=list)
    signals: List[ChatbotSignalResult] = Field(default_factory=list)
    results: Optional[Dict[str, Any]] = None  # Frontend compatibility container
    suggested_followups: List[str] = Field(default_factory=list)



# ── Structured People Search Request ───────────────
class PeopleSearchFilterRequest(BaseModel):
    person_name: Optional[str] = Field(None, description="Search by person's first or last name (e.g. 'Emily', 'Robin Vince')")
    organization: Optional[str] = Field(None, description="Search by company name or ticker (e.g. 'BNY', 'BK')")
    designation: Optional[str] = Field(None, description="Search by exact or partial designation/title (e.g. 'CEO', 'Head of Asset Servicing', 'CTPO')")
    role: Optional[str] = Field(None, description="Search by target role / seniority (e.g. 'CXO', 'VP', 'Managing Director', 'Director')")
    department_or_lob: Optional[str] = Field(None, description="Filter by business unit or department (e.g. 'Asset Servicing', 'Pershing')")
    min_lead_score: Optional[int] = Field(None, ge=0, le=100, description="Filter leads with score >= min_lead_score")
    is_decision_maker: Optional[bool] = Field(None, description="Filter only confirmed decision makers")
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)


# ── Structured People Search Response ──────────────
class PeopleSearchFilterResponse(BaseModel):
    total_found: int
    offset: int
    limit: int
    items: List[ChatbotPersonResult]


# ── Quick Starter Suggestions ──────────────────────
class ChatbotStarterSuggestion(BaseModel):
    category: str
    title: str
    prompt: str
    description: str


class ChatbotSuggestionsResponse(BaseModel):
    suggestions: List[ChatbotStarterSuggestion]


# ── Streaming Real-Time Execution Event Models ─────
class ProcessStepEvent(BaseModel):
    step_id: str
    title: str
    status: str = "completed"  # in_progress, completed, failed
    details: Optional[str] = None
    icon: Optional[str] = None


class ChatbotStreamEvent(BaseModel):
    event: str  # "step_started", "step_completed", "final_response", "error"
    step: Optional[ProcessStepEvent] = None
    data: Optional[Dict[str, Any]] = None
    reply: Optional[str] = None
    executive_summary: Optional[str] = None

