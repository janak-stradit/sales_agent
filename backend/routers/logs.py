"""API Router for Tool Execution Logs & Telemetry (Tab 7)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy import func

from backend.database import get_db
from backend.models.tool_execution_log import ToolExecutionLog
from backend.schemas.pipeline_schemas import ToolLogResponse, TelemetryStatsResponse

router = APIRouter()


@router.get("/", response_model=List[ToolLogResponse])
def list_logs_endpoint(
    provider: Optional[str] = None,
    endpoint: Optional[str] = None,
    status: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List raw tool execution telemetry logs with filters for provider, endpoint, status, and run_id.
    """
    query = db.query(ToolExecutionLog)
    if provider:
        query = query.filter(ToolExecutionLog.provider.ilike(f"%{provider}%"))
    if endpoint:
        query = query.filter(ToolExecutionLog.endpoint.ilike(f"%{endpoint}%"))
    if status:
        query = query.filter(ToolExecutionLog.status.ilike(status))
    if run_id:
        query = query.filter(ToolExecutionLog.run_id == run_id)

    logs = query.order_by(ToolExecutionLog.created_at.desc()).offset(offset).limit(limit).all()

    return [
        ToolLogResponse(
            id=log.id,
            run_id=log.run_id,
            account_id=log.account_id,
            account_name=log.account.name if log.account else None,
            provider=log.provider,
            endpoint=log.endpoint,
            status=log.status,
            reported_cost_value=float(log.reported_cost_value or 0.0),
            overall_latency=float(log.overall_latency or 0.0),
            billed_units=log.billed_units or 0,
            provider_http_status=log.provider_http_status or 200,
            created_at=log.created_at
        )
        for log in logs
    ]


@router.get("/stats", response_model=TelemetryStatsResponse)
def get_telemetry_stats_endpoint(db: Session = Depends(get_db)):
    """
    Get aggregated telemetry metrics: total calls, success rate, cost, latency, and provider distribution.
    """
    total = db.query(ToolExecutionLog).count()
    if total == 0:
        return TelemetryStatsResponse(
            total_tool_calls=0,
            success_rate_percent=100.0,
            total_cost_usd=0.0,
            avg_latency_seconds=0.0,
            provider_breakdown={},
            status_breakdown={}
        )

    success_cnt = db.query(ToolExecutionLog).filter(ToolExecutionLog.status.in_(["SUCCESS", "COMPLETED", "SUCCEEDED"])).count()
    total_cost = db.query(func.coalesce(func.sum(ToolExecutionLog.reported_cost_value), 0.0)).scalar() or 0.0
    avg_latency = db.query(func.coalesce(func.avg(ToolExecutionLog.overall_latency), 0.0)).scalar() or 0.0

    all_logs = db.query(ToolExecutionLog).all()
    prov_dist: Dict[str, int] = {}
    stat_dist: Dict[str, int] = {}

    for l in all_logs:
        prov_dist[l.provider] = prov_dist.get(l.provider, 0) + 1
        stat_dist[l.status] = stat_dist.get(l.status, 0) + 1

    return TelemetryStatsResponse(
        total_tool_calls=total,
        success_rate_percent=round((success_cnt / total) * 100, 1),
        total_cost_usd=round(float(total_cost), 4),
        avg_latency_seconds=round(float(avg_latency), 2),
        provider_breakdown=prov_dist,
        status_breakdown=stat_dist
    )
