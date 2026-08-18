"""AccountMarketSegment — Target Customers, Segments, Geographies & Asset Classes (LOB §3.4)."""

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountMarketSegment(Base):
    __tablename__ = "account_market_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Customer & Segment Identification (LOB §3.4)
    customer_type = Column(String(100))
    client_segment = Column(String(100))
    organization_size = Column(String(100))
    customer_description = Column(Text)

    # Market, Geography & Asset Class (LOB §3.4)
    market_name = Column(String(255))
    market_category = Column(String(100))
    geography = Column(String(100))
    industry = Column(String(100))
    asset_class = Column(String(100))
    served_segment = Column(String(100))
    served_geography = Column(String(100))

    # Offering & Parent Mappings (LOB §3.4)
    offering_relationship = Column(String(255))
    parent_lob_sub_lob = Column(String(255))

    # Classification & Evidence (LOB §3.4)
    classification = Column(String(100))
    confidence = Column(String(50), default="HIGH")
    evidence_url = Column(String(1000))
    authoritative_source_flag = Column(Boolean, default=False)

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="market_segments")
    lob = relationship("AccountLob", back_populates="market_segments")

    def __repr__(self):
        return f"<AccountMarketSegment(segment='{self.client_segment}', market='{self.market_name}')>"
