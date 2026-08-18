"""PipelineRun — Pipeline Execution Tracking, Multi-Collector Runs & Telemetry (Tab 7)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, ForeignKey, Index, Numeric, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Collection Mode
    collection_mode = Column(String(100), nullable=False, default="full_pipeline", index=True)
    collection_mode_label = Column(String(255))

    # Execution Status: PENDING, RUNNING, COMPLETED, FAILED, PARTIAL
    status = Column(String(50), default="PENDING", index=True)
    progress_percent = Column(Integer, default=0)              # 0 to 100
    current_step = Column(String(255))
    total_steps = Column(Integer, default=1)
    steps_completed = Column(Integer, default=0)
    step_details = Column(JSONB, default=[])                   # List of step statuses and timing

    # Metrics & Yield
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    total_cost_usd = Column(Numeric(10, 4), default=0.0)
    total_latency_seconds = Column(Float, default=0.0)
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("Account", back_populates="pipeline_runs")

    __table_args__ = (
        Index("idx_pipeline_runs_account_status", "account_id", "status"),
    )

    def __repr__(self):
        return f"<PipelineRun(run_id='{self.run_id}', mode='{self.collection_mode}', status='{self.status}')>"
