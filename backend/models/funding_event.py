"""FundingEvent — Capital raise and investor tracking model (Apollo §7)."""

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class FundingEvent(Base):
    __tablename__ = "funding_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Apollo §7 Funding Information
    funding_event_id = Column(String(100))
    date = Column(String(50))
    funded_at = Column(String(50))
    type = Column(String(100))
    round = Column(String(100))
    amount = Column(String(50))
    money_raised = Column(String(50))
    currency = Column(String(20), default="USD")
    investors = Column(Text)
    news_url = Column(String(500))

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="funding_events_rel")

    def __repr__(self):
        return f"<FundingEvent(type='{self.type}', amount='{self.amount}')>"
