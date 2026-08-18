"""AccountLob — Lines of Business, Sub-Divisions & Hierarchical Units (LOB §3.1, §3.2 & Apollo §8/§10)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountLob(Base):
    __tablename__ = "account_lobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Identifiers & Entity Names (LOB §3.1, §3.2 & Apollo §8)
    suborg_id = Column(String(100), index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_name = Column(String(255))
    normalized_name = Column(String(255))
    business_unit_name = Column(String(255))
    entity_type = Column(String(100), default="LOB")  # LOB, Sub-LOB, Division, Business Unit
    node_name = Column(String(255))
    node_type = Column(String(100))

    # Hierarchy & Relationship Path (LOB §3.1, §3.2)
    parent_entity = Column(String(255))
    parent_lob_name = Column(String(255))
    child_entity = Column(String(255))
    child_node = Column(String(255))
    parent_child_relationship = Column(String(255))
    relationship_type = Column(String(100))
    relationship_description = Column(Text)
    hierarchy_path = Column(String(500))
    hierarchy_depth = Column(Integer, default=1)

    # Scale & Firmographics (Apollo §8)
    headcount = Column(Integer)
    estimated_num_employees = Column(Integer)
    website_url = Column(String(500))
    country = Column(String(100))
    industries = Column(ARRAY(String), default=[])
    functions = Column(ARRAY(String), default=[])
    responsibilities = Column(ARRAY(String), default=[])

    # Leadership (Apollo §10 & LOB §3.5)
    business_head = Column(String(255))
    division_leader = Column(String(255))
    tech_leader = Column(String(255))
    tech_leader_title = Column(String(255))

    # AI & Research Intelligence (Apollo §10 & LOB §3.1)
    confidence = Column(String(50), default="MEDIUM")
    confidence_level = Column(String(50))
    key_platforms = Column(ARRAY(String), default=[])
    intelligence_notes = Column(Text)
    short_description = Column(Text)
    detailed_description = Column(Text)
    supporting_statement = Column(Text)
    classification = Column(String(100))
    classification_type = Column(String(100))
    validation_status = Column(String(50), default="UNVALIDATED")
    evidence_count = Column(Integer, default=0)
    authoritative_source_flag = Column(Boolean, default=False)

    # Citation Metadata (LOB §3.1)
    source_title = Column(String(500))
    source_url = Column(String(1000))
    highlighted_excerpt = Column(Text)
    excerpt = Column(Text)
    full_content = Column(Text)
    content = Column(Text)
    publication_timestamp = Column(DateTime(timezone=True))
    crawl_timestamp = Column(DateTime(timezone=True))
    published_time = Column(String(50))
    last_crawled_time = Column(String(50))

    # Envelope & Timestamps
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="lobs")
    parent_lob = relationship("AccountLob", remote_side=[id], backref="sub_lobs")
    products_services = relationship("AccountProductService", back_populates="lob", cascade="all, delete-orphan")
    market_segments = relationship("AccountMarketSegment", back_populates="lob", cascade="all, delete-orphan")
    tech_initiatives = relationship("AccountTechInitiative", back_populates="lob", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="lob", cascade="all, delete-orphan")
    evidence = relationship("DataSourceEvidence", back_populates="lob", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_account_lobs_name", "name"),
        Index("idx_account_lobs_hierarchy_path", "hierarchy_path"),
    )

    def __repr__(self):
        return f"<AccountLob(name='{self.name}', type='{self.entity_type}', depth={self.hierarchy_depth})>"
