"""Account — Complete Apollo & Enterprise Organization Enrichment model."""

import uuid
from sqlalchemy import (
    Column, String, Integer, BigInteger, Text, Boolean, DateTime, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class Account(Base):
    __tablename__ = "accounts"

    # Primary Key & Identification (Apollo §2)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apollo_org_id = Column(String(100), index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), index=True)
    primary_domain = Column(String(255), index=True)
    website_url = Column(String(500))
    company_url = Column(String(500))

    # Basic Firmographics (Apollo §2)
    founded_year = Column(Integer)
    employee_count = Column(Integer)
    estimated_num_employees = Column(Integer)
    short_description = Column(Text)
    description = Column(Text)
    retail_location_count = Column(Integer, default=0)
    num_retail_locations = Column(Integer, default=0)
    num_languages = Column(Integer, default=0)
    languages = Column(ARRAY(String), default=[])
    snippets_loaded = Column(Boolean, default=False)
    owned_by_organization_id = Column(String(100))

    # Financial Information (Apollo §6)
    organization_revenue = Column(BigInteger)
    organization_revenue_printed = Column(String(50))
    annual_revenue = Column(BigInteger)
    annual_revenue_printed = Column(String(50))
    annual_revenue_usd = Column(BigInteger)
    market_cap = Column(String(50))
    market_cap_usd = Column(String(50))
    publicly_traded_symbol = Column(String(50))
    publicly_traded_exchange = Column(String(50))
    alexa_ranking = Column(Integer)
    total_funding = Column(String(50))
    total_funding_printed = Column(String(50))
    total_funding_usd = Column(String(50))
    latest_funding_round_date = Column(String(50))
    latest_funding_stage = Column(String(50))

    # Suborganizations Count (Apollo §8)
    num_suborganizations = Column(Integer, default=0)

    # Contact & Social Information (Apollo §3)
    phone = Column(String(50))
    primary_phone = Column(JSONB, default={})
    sanitized_phone = Column(String(50))
    linkedin_uid = Column(String(100))
    linkedin_url = Column(String(500))
    twitter_url = Column(String(500))
    facebook_url = Column(String(500))
    angellist_url = Column(String(500))
    crunchbase_url = Column(String(500))
    logo_url = Column(String(500))

    # Location Information (Apollo §4)
    raw_address = Column(String(500))
    street_address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(50))
    country = Column(String(100))
    headquarters = Column(String(500))

    # Industry Classification (Apollo §5)
    industry = Column(String(100), index=True)
    industries = Column(ARRAY(String), default=[])
    secondary_industries = Column(ARRAY(String), default=[])
    sic_codes = Column(ARRAY(String), default=[])
    naics_codes = Column(ARRAY(String), default=[])
    industry_tag_id = Column(String(100))
    industry_tag_hash = Column(JSONB, default={})

    # Keywords & Technographics (Apollo §9)
    keywords = Column(ARRAY(String), default=[])
    tech_stack = Column(ARRAY(String), default=[])
    technology_names = Column(ARRAY(String), default=[])
    pain_points = Column(ARRAY(String), default=[])

    # Document Envelope & Timestamps
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    technologies = relationship("AccountTechnology", back_populates="account", cascade="all, delete-orphan")
    taxonomies = relationship("AccountTaxonomy", back_populates="account", cascade="all, delete-orphan")
    funding_events_rel = relationship("FundingEvent", back_populates="account", cascade="all, delete-orphan")
    lobs = relationship("AccountLob", back_populates="account", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="account", cascade="all, delete-orphan")
    products_services = relationship("AccountProductService", back_populates="account", cascade="all, delete-orphan")
    market_segments = relationship("AccountMarketSegment", back_populates="account", cascade="all, delete-orphan")
    tech_initiatives = relationship("AccountTechInitiative", back_populates="account", cascade="all, delete-orphan")
    evidence = relationship("DataSourceEvidence", back_populates="account", cascade="all, delete-orphan")
    execution_logs = relationship("ToolExecutionLog", back_populates="account")
    trigger_signals = relationship("SalesTriggerSignal", back_populates="account", cascade="all, delete-orphan")
    social_posts = relationship("SocialIntelligence", back_populates="account", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_accounts_name", "name"),
        Index("idx_accounts_domain", "domain"),
        Index("idx_accounts_sic_codes", "sic_codes", postgresql_using="gin"),
        Index("idx_accounts_naics_codes", "naics_codes", postgresql_using="gin"),
        Index("idx_accounts_keywords", "keywords", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Account(name='{self.name}', domain='{self.domain}')>"
