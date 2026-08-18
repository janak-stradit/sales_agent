"""Pydantic schemas for Pipeline & Engine Controls (Tab 7)."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional, Literal
from uuid import UUID
from datetime import datetime


CollectionModeType = Literal[
    "full_pipeline",
    "corporate_profile",
    "social_media",
    "org_hierarchy",
    "personnel_enrichment",
    "sales_signals",
    "lead_scoring",
    "monid_export_sync"
]

COLLECTION_MODE_LABELS = {
    "full_pipeline": "Full Pipeline (All Collectors + Lead Scoring + Export)",
    "corporate_profile": "Corporate Profile & Segments",
    "social_media": "Social Media (Corporate & Executive)",
    "org_hierarchy": "Organizational Hierarchy & Spans",
    "personnel_enrichment": "Personnel & Social Enrichment",
    "sales_signals": "News & Sales Signals",
    "lead_scoring": "Lead Scoring Engine Only",
    "monid_export_sync": "monid.ai Export Sync",
}


class PipelineTriggerRequest(BaseModel):
    account_id: UUID
    collection_mode: CollectionModeType = "full_pipeline"
    run_sync: bool = False


class PipelineStepDetail(BaseModel):
    step_name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    records_yielded: Optional[int] = 0
    message: Optional[str] = None


class PipelineRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: str
    account_id: UUID
    account_name: Optional[str] = None
    collection_mode: str
    collection_mode_label: Optional[str] = None
    status: str
    progress_percent: int
    current_step: Optional[str] = None
    total_steps: int
    steps_completed: int
    step_details: List[Dict[str, Any]] = []
    records_created: int = 0
    records_updated: int = 0
    total_cost_usd: float = 0.0
    total_latency_seconds: float = 0.0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class WarehouseStatusResponse(BaseModel):
    status: str = "Live"
    version: str = "v2.4.0"
    connection_healthy: bool = True
    database_type: str = "PostgreSQL Data Warehouse + monid.ai API Sync"
    database_url_masked: str
    total_records: int
    table_counts: Dict[str, int]
    monid_api_status: str
    monid_balance_usd: float
    last_sync_timestamp: Optional[datetime] = None


class ToolLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: str
    account_id: Optional[UUID] = None
    account_name: Optional[str] = None
    provider: str
    endpoint: str
    status: str
    reported_cost_value: float = 0.0
    overall_latency: float = 0.0
    billed_units: int = 0
    provider_http_status: int = 200
    created_at: Optional[datetime] = None


class TelemetryStatsResponse(BaseModel):
    total_tool_calls: int
    success_rate_percent: float
    total_cost_usd: float
    avg_latency_seconds: float
    provider_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
