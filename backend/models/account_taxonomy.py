"""AccountTaxonomy — Normalized Industry Classifications, SIC/NAICS codes, and Keywords."""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountTaxonomy(Base):
    __tablename__ = "account_taxonomies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    code_type = Column(String(50), nullable=False, index=True)   # SIC, NAICS, INDUSTRY_TAG, KEYWORD, SECTOR
    code_value = Column(String(255), nullable=False, index=True) # e.g. "6211", "522110", "asset servicing"
    description = Column(String(255))                           # Human-readable title
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    account = relationship("Account", back_populates="taxonomies")

    __table_args__ = (
        Index("idx_account_tax_type_val", "account_id", "code_type", "code_value"),
    )

    def __repr__(self):
        return f"<AccountTaxonomy(type='{self.code_type}', value='{self.code_value}')>"
