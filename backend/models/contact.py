"""Contact — Executive Decision Maker & Leadership Model (Persona §1 & LOB §3.5)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Identifiers (Persona §1)
    node_id = Column(String(100), index=True)
    contact_id_external = Column(String(100))

    # Basic Contact & Email (Persona §1)
    email = Column(String(255), index=True)
    contact_email = Column(String(255))
    email_confidence = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))
    title = Column(String(255))
    current_title = Column(String(255))

    # Organizational & LOB Alignment (Persona §1 & LOB §3.5)
    sub_lob_name = Column(String(255))
    lob_association = Column(String(255))
    organization = Column(String(255))
    parent_organization = Column(String(255))

    # Seniority & Leadership Classification (Persona §1 & LOB §3.5)
    seniority = Column(String(50))
    seniority_tier = Column(String(50))  # CXO, VP, Director, Tech Lead
    target_persona_type = Column(String(100))  # Tech Decision Maker, Line Executive
    leadership_type = Column(String(100))  # CIO, Tech Leader, Business Head
    buyer_roles = Column(ARRAY(String), default=["Key Decision Maker"])

    # Reporting Hierarchy (Persona §1 & LOB §3.5)
    reports_to_name = Column(String(255))
    reports_to_title = Column(String(255))
    reports_to_path = Column(String(500))
    hierarchy_level = Column(Integer, default=1)

    # Authority & Scoring (Persona §1)
    decision_authority = Column(String(50))
    budget_authority = Column(String(50))
    lead_score = Column(Integer, default=0, index=True)
    lead_status = Column(String(50), default="Warm")  # Hot, Warm, Cold

    # Contact Channels & Geography (Persona §1 & LOB §3.5)
    avatar_url = Column(String(500))
    phone = Column(String(50))
    location = Column(String(255))
    geography = Column(String(100))
    linkedin_url = Column(String(500))
    linkedin_follower_count = Column(Integer, default=0)
    linkedin_connection_count = Column(Integer, default=0)

    # Role Tenure & Validation (Persona §4.2 & LOB §3.5)
    tenure_months = Column(Integer)
    start_date = Column(String(50))
    tenure = Column(String(50))
    current_role_validation_date = Column(String(50))
    remit = Column(Text)
    summary_bio = Column(Text)
    responsibilities = Column(Text)
    relationship_evidence = Column(Text)

    # Classification & Status (LOB §3.5)
    classification = Column(String(100))
    confidence = Column(String(50), default="HIGH")
    source_count = Column(Integer, default=1)
    status = Column(String(50), default="ACTIVE")

    # Document Envelope & Timestamps
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="contacts")
    lob = relationship("AccountLob", back_populates="contacts")
    org_node = relationship("OrgHierarchy", foreign_keys="[OrgHierarchy.contact_id]", back_populates="contact", uselist=False, cascade="all, delete-orphan")
    managed_nodes = relationship("OrgHierarchy", foreign_keys="[OrgHierarchy.manager_id]", back_populates="manager")
    persona = relationship("Persona", back_populates="contact", uselist=False, cascade="all, delete-orphan")
    evidence = relationship("DataSourceEvidence", back_populates="contact", cascade="all, delete-orphan")
    social_posts = relationship("SocialIntelligence", back_populates="contact")

    __table_args__ = (
        Index("idx_contacts_email", "email"),
        Index("idx_contacts_full_name", "full_name"),
        Index("idx_contacts_seniority_tier", "seniority_tier"),
    )

    def __repr__(self):
        return f"<Contact(name='{self.full_name}', title='{self.title}', tier='{self.seniority_tier}')>"
