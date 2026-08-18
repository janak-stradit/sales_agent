"""AccountTechInitiative — Strategic IT Modernization & Tech Stack Tracking (LOB §3.6)."""

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountTechInitiative(Base):
    __tablename__ = "account_technology_initiatives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Technology & Vendor Details (LOB §3.6)
    technology_name = Column(String(255), nullable=False)
    technology_category = Column(String(100))
    platform_vendor = Column(String(255))
    platform_or_vendor = Column(String(255))
    business_capability = Column(String(255))
    associated_lob_sub_lob = Column(String(255))

    # Initiative Scope & Objectives (LOB §3.6)
    initiative_name = Column(String(255))
    initiative_description = Column(Text)
    objective = Column(Text)
    status = Column(String(50), default="IN_PROGRESS")
    timeline = Column(String(100))
    priority_name = Column(String(100))

    # Pain Points & Business Drivers (LOB §3.6)
    business_rationale = Column(Text)
    related_pain_point = Column(Text)
    related_technology = Column(String(255))

    # Ownership & Governance (LOB §3.6)
    business_owner = Column(String(255))
    technology_owner = Column(String(255))
    responsible_organization = Column(String(255))

    # Classification & Evidence (LOB §3.6)
    classification = Column(String(100))
    confidence = Column(String(50), default="HIGH")
    evidence_date = Column(String(50))
    authoritative_source_flag = Column(Boolean, default=False)

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="tech_initiatives")
    lob = relationship("AccountLob", back_populates="tech_initiatives")

    def __repr__(self):
        return f"<AccountTechInitiative(tech='{self.technology_name}', vendor='{self.platform_vendor}')>"
