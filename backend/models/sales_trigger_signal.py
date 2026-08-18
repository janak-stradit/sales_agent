"""SalesTriggerSignal — Buying Signals, Modernization Triggers & Market Events (Tab 6)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class SalesTriggerSignal(Base):
    __tablename__ = "sales_trigger_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Signal Classification
    signal_type = Column(String(100), nullable=False, index=True)
    category = Column(String(100), default="Sales Intent")
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(Text)

    # Urgency & Priority
    priority = Column(String(50), default="HIGH", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    urgency_score = Column(Integer, default=75)                # 1 to 100
    confidence = Column(String(50), default="HIGH")            # HIGH, MEDIUM, LOW

    # Actionable Sales Intelligence
    recommended_action = Column(Text)                          # Prescriptive playbook / outreach angle
    key_talking_points = Column(JSONB, default=[])

    # Evidence & Provenance
    source_name = Column(String(255), default="Monid Intelligence Stream")
    source_url = Column(String(1000))
    detected_at = Column(DateTime(timezone=True), default=func.now())

    # Workflow Status: NEW, ACTIONED, DISMISSED
    status = Column(String(50), default="NEW", index=True)
    actioned_by = Column(String(100))
    actioned_at = Column(DateTime(timezone=True))
    notes = Column(Text)

    # Raw Payload & Timestamps
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="trigger_signals")
    lob = relationship("AccountLob")
    contact = relationship("Contact")

    __table_args__ = (
        Index("idx_trigger_signals_account_priority", "account_id", "priority"),
        Index("idx_trigger_signals_type_status", "signal_type", "status"),
    )

    def __repr__(self):
        return f"<SalesTriggerSignal(type='{self.signal_type}', title='{self.title}', priority='{self.priority}')>"
