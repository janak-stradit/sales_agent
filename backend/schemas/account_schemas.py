"""Pydantic schemas for Account endpoints (Generic Multi-Organization Architecture)."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ── Funding Events ─────────────────────────────

class FundingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    funding_event_id: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = "USD"
    investors: Optional[str] = None
    news_url: Optional[str] = None


class ProductServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lob_id: Optional[UUID] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    service_name: Optional[str] = None
    service_category: Optional[str] = None
    delivery_function: Optional[str] = None
    validation_status: Optional[str] = "Validated"


class MarketSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lob_id: Optional[UUID] = None
    customer_type: Optional[str] = None
    client_segment: Optional[str] = None
    market_name: Optional[str] = None
    geography: Optional[str] = "Global"
    asset_class: Optional[str] = None


class TechInitiativeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lob_id: Optional[UUID] = None
    technology_name: str
    technology_category: Optional[str] = None
    platform_vendor: Optional[str] = None
    initiative_name: Optional[str] = None
    initiative_description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = "IN_PROGRESS"
    priority_name: Optional[str] = None
    technology_owner: Optional[str] = None


class AccountTechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    technology_name: str
    category: Optional[str] = None
    vendor: Optional[str] = None
    version: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None


class AccountTaxonomyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    code_type: str
    code_value: str
    description: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None


# ── AccountLob ─────────────────────────────────

class LobCreate(BaseModel):
    account_id: UUID
    name: str = Field(..., max_length=255)
    parent_lob_id: Optional[UUID] = None
    suborg_id: Optional[str] = None
    entity_type: Optional[str] = "LOB"
    headcount: Optional[int] = None
    business_head: Optional[str] = None
    tech_leader: Optional[str] = None
    tech_leader_title: Optional[str] = None
    confidence: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None


class LobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    parent_lob_id: Optional[UUID] = None
    suborg_id: Optional[str] = None
    name: str
    entity_type: Optional[str] = "LOB"
    hierarchy_path: Optional[str] = None
    hierarchy_depth: Optional[int] = 1
    headcount: Optional[int] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    business_head: Optional[str] = None
    tech_leader: Optional[str] = None
    tech_leader_title: Optional[str] = None
    confidence: Optional[str] = None
    intelligence_notes: Optional[str] = None
    contact_count: Optional[int] = 0
    created_at: Optional[datetime] = None


# ── Account ────────────────────────────────────

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Acme Corp"])
    company_url: Optional[str] = Field(None, examples=["acme.com"])
    domain: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    headquarters: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    short_description: Optional[str] = None
    annual_revenue_usd: Optional[int] = None
    market_cap_usd: Optional[str] = None
    total_funding_usd: Optional[str] = None
    logo_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    apollo_org_id: Optional[str] = None
    name: str
    domain: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    headquarters: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    short_description: Optional[str] = None
    annual_revenue_usd: Optional[int] = None
    market_cap_usd: Optional[str] = None
    total_funding_usd: Optional[str] = None
    logo_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    technology_names: Optional[List[str]] = []
    tech_stack: Optional[List[str]] = []
    sic_codes: Optional[List[str]] = []
    naics_codes: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    publicly_traded_symbol: Optional[str] = None
    publicly_traded_exchange: Optional[str] = None
    lob_count: Optional[int] = 0
    contact_count: Optional[int] = 0
    decision_maker_count: Optional[int] = 0
    signals_count: Optional[int] = 0
    created_at: Optional[datetime] = None


# ── Full 360 Account Dossier ───────────────────

class Account360Response(BaseModel):
    account: AccountResponse
    lobs: List[LobResponse] = []
    funding_events: List[FundingEventResponse] = []
    products_and_services: List[ProductServiceResponse] = []
    market_segments: List[MarketSegmentResponse] = []
    technology_initiatives: List[TechInitiativeResponse] = []
    executive_summary: Dict[str, Any] = {}
    recent_signals: List[Dict[str, Any]] = []
    recent_social_posts: List[Dict[str, Any]] = []
