"""DataSourceEvidence — Web Search Citations, Official Site Verification & Crawl Logs (LOB §3.7)."""

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class DataSourceEvidence(Base):
    __tablename__ = "data_source_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Source Identification & URLs (LOB §3.7)
    source_title = Column(String(500))
    source_url = Column(String(1000), nullable=False)
    domain = Column(String(255), index=True)
    favicon = Column(String(500))

    # Content & Excerpts (LOB §3.7)
    highlight = Column(Text)
    highlighted_excerpt = Column(Text)
    full_content = Column(Text)
    content = Column(Text)
    author_list = Column(ARRAY(String), default=[])

    # Timestamps (LOB §3.7)
    publication_timestamp = Column(DateTime(timezone=True))
    last_crawled_timestamp = Column(DateTime(timezone=True))
    published_time = Column(String(50))
    last_crawled_time = Column(String(50))

    # Verification & Authority (LOB §3.7)
    official_domain_flag = Column(Boolean, default=False)
    source_type = Column(String(100))
    authority_level = Column(String(100))
    claim_identifier = Column(String(100))
    supported_field = Column(String(100))
    validation_result = Column(String(50), default="VALIDATED")
    conflicting_source_flag = Column(Boolean, default=False)

    # De-duplication & Canonical Identifiers (LOB §3.7)
    canonical_url = Column(String(1000))
    source_hash = Column(String(255))
    duplicate_group_id = Column(String(100))
    duplicate_group_identifier = Column(String(100))

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="evidence")
    lob = relationship("AccountLob", back_populates="evidence")
    contact = relationship("Contact", back_populates="evidence")

    def __repr__(self):
        return f"<DataSourceEvidence(domain='{self.domain}', official={self.official_domain_flag})>"
