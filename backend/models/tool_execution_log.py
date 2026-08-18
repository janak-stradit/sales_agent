"""ToolExecutionLog — API Collection, Execution Telemetry & Billing Audit model (Apollo §1 & LOB §3.8)."""

import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Index, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class ToolExecutionLog(Base):
    __tablename__ = "tool_execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(100), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Provider & Endpoint Details (Apollo §1 & LOB §3.8)
    provider = Column(String(100), nullable=False)
    provider_id = Column(String(100))
    provider_name = Column(String(100))
    endpoint = Column(String(255), nullable=False)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, RATE_LIMITED
    caller = Column(String(100))

    # Query Details (Apollo §1 & LOB §3.8, §4)
    input_query = Column(Text)
    original_query = Column(Text)
    generated_queries = Column(JSONB, default=[])
    max_queries = Column(Integer)
    search_options = Column(JSONB, default={})
    generated_query_count = Column(Integer, default=0)

    # HTTP & Performance Metrics (Apollo §1 & LOB §3.8, §5)
    provider_response_http_status = Column(Integer, default=200)
    provider_http_status = Column(Integer, default=200)
    result_count = Column(Integer, default=0)
    billed_units = Column(Integer, default=0)
    full_content_token_count = Column(Integer, default=0)
    overall_latency = Column(Float, default=0.0)
    per_query_latency = Column(JSONB, default=[])

    # Pricing & Cost Tracking (Apollo §1 & LOB §3.8, §5)
    price_type = Column(String(50))
    price_amount = Column(Numeric(10, 4), default=0.0)
    price_currency = Column(String(20), default="USD")
    price_notes = Column(Text)
    tier_label = Column(String(50))
    unit_size = Column(String(50))
    pricing_condition = Column(String(255))
    cost = Column(Numeric(10, 4), default=0.0)
    cost_currency = Column(String(20), default="USD")
    reported_cost_value = Column(Numeric(10, 4), default=0.0)
    reported_cost_currency = Column(String(20), default="USD")
    reported_cost_unit = Column(String(50))

    # Diagnostic & Hint Metadata (Apollo §1 & LOB §3.8)
    inspect_schema_version_id = Column(String(100))
    documentation_url = Column(String(500))
    raw_response_location = Column(String(500))
    retrieve_response_hint = Column(String(500))
    find_company_domain_hint = Column(String(500))

    # Full Payload Envelopes
    input_payload = Column(JSONB, default={})
    raw_response = Column(JSONB, default={})

    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_timestamp = Column(DateTime(timezone=True))
    completed_timestamp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="execution_logs")

    __table_args__ = (
        Index("idx_tool_logs_run_id", "run_id"),
        Index("idx_tool_logs_provider_endpoint", "provider", "endpoint"),
    )

    def __repr__(self):
        return f"<ToolExecutionLog(run_id='{self.run_id}', provider='{self.provider}', cost={self.reported_cost_value})>"
