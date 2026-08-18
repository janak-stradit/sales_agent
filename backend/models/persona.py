"""Persona — 1:1 3-Level Prospect Intelligence model (Persona §4.2, §4.3, §4.4)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Scrape Origin & Integrity Flags (Persona §4.4)
    is_scraped = Column(Boolean, default=True)
    is_ai_generated = Column(Boolean, default=False)
    scraping_source = Column(String(100), default="Apify LinkedIn Scraper")
    scraping_status = Column(String(50), default="SUCCESS")
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Level 1: Demographics & Career Trajectory (Persona §4.2)
    age_estimate = Column(Integer)
    tenure_months = Column(Integer)
    location = Column(String(255))
    education_degree = Column(String(255))
    education_institution = Column(String(255))
    education_grad_year = Column(Integer)
    prior_company = Column(String(255))
    prior_title = Column(String(255))
    prior_duration_months = Column(Integer)
    education = Column(JSONB, default=[])
    certifications = Column(JSONB, default=[])
    experience = Column(JSONB, default=[])
    career_trajectory = Column(JSONB, default=[])
    career_timeline = Column(JSONB, default=[])
    skills = Column(ARRAY(String), default=[])
    demographics = Column(JSONB, default={})

    # Level 2: Professional Behavior, Tech Stack & Intent (Persona §4.3)
    tech_stack = Column(ARRAY(String), default=[])
    operational_pain_points = Column(ARRAY(String), default=[])
    kpis = Column(ARRAY(String), default=[])
    budget_authority = Column(String(50))
    decision_authority = Column(String(50))
    intent_signals = Column(JSONB, default=[])
    professional_behavior = Column(JSONB, default={})

    # Level 3: Scraped Personal Touch (100% Scraped via Apify / Monid MCP) (Persona §4.4)
    engagement_rate = Column(String(50))
    communication_style = Column(String(100))
    professional_interests = Column(ARRAY(String), default=[])
    social_platforms = Column(JSONB, default={})
    social_platforms_linkedin = Column(String(500))
    social_platforms_twitter = Column(String(500))
    social_platforms_portal = Column(String(500))
    social_platforms_facebook = Column(String(500))
    social_platforms_instagram = Column(String(500))
    recent_scraped_posts = Column(JSONB, default=[])
    post_platform = Column(String(50))
    post_date = Column(String(50))
    post_content = Column(Text)
    post_engagement = Column(String(100))
    post_topic_focus = Column(String(255))
    personal_touch = Column(JSONB, default={})

    # AI Synthesis Insights (Icebreakers & Pitch)
    ai_summary = Column(Text)
    ice_breakers = Column(ARRAY(String), default=[])
    value_proposition = Column(Text)
    objections = Column(ARRAY(String), default=[])
    score_breakdown = Column(JSONB, default={})

    # Metadata & Envelope
    last_enriched = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contact = relationship("Contact", back_populates="persona")

    __table_args__ = (
        Index("idx_personas_tech_stack", "tech_stack", postgresql_using="gin"),
        Index("idx_personas_pain_points", "operational_pain_points", postgresql_using="gin"),
        Index("idx_personas_demographics", "demographics", postgresql_using="gin"),
        Index("idx_personas_behavior", "professional_behavior", postgresql_using="gin"),
        Index("idx_personas_personal_touch", "personal_touch", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Persona(contact_id='{self.contact_id}', scraped={self.is_scraped}, source='{self.scraping_source}')>"
