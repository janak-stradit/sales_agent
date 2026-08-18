"""OrgHierarchy — 1:1 Executive reporting structure and management nodes (Persona §1 & LOB §3.5)."""

import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class OrgHierarchy(Base):
    __tablename__ = "org_hierarchy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Reporting Structure & Path (Persona §1 & LOB §3.5)
    level = Column(Integer, default=1)
    hierarchy_level = Column(Integer, default=1)
    reports_to_path = Column(String(500))  # e.g., '001.002.004'
    reports_to_name = Column(String(255))
    reports_to_title = Column(String(255))
    parent_organization = Column(String(255))

    # Evidence & Authority (LOB §3.5)
    relationship_evidence = Column(Text)
    influence_score = Column(Integer, default=50)
    decision_authority = Column(String(50))
    budget_authority = Column(String(50))
    confidence = Column(String(50), default="HIGH")
    evidence_count = Column(Integer, default=1)

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contact = relationship("Contact", foreign_keys=[contact_id], back_populates="org_node")
    manager = relationship("Contact", foreign_keys=[manager_id], back_populates="managed_nodes")

    def __repr__(self):
        return f"<OrgHierarchy(contact_id='{self.contact_id}', level={self.level}, path='{self.reports_to_path}')>"
