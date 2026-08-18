"""AccountTechnology — Normalized Enterprise Technology Stack and detected software."""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountTechnology(Base):
    __tablename__ = "account_technologies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    technology_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100))                       # Cloud, Analytics, Core Banking, CRM, Security
    vendor = Column(String(255))                         # AWS, Snowflake, Salesforce, Oracle, Microsoft
    version = Column(String(50))
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    account = relationship("Account", back_populates="technologies")

    __table_args__ = (
        Index("idx_account_tech_name", "account_id", "technology_name"),
        Index("idx_account_tech_category", "category"),
    )

    def __repr__(self):
        return f"<AccountTechnology(name='{self.technology_name}', vendor='{self.vendor}')>"
