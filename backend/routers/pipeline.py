"""API Router for Pipeline Collection & Engine Controls (Tab 7 & Screenshot 2)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any

from backend.database import get_db
from backend.models.account import Account
from backend.models.pipeline_run import PipelineRun
from backend.schemas.pipeline_schemas import (
    PipelineTriggerRequest,
    PipelineRunResponse,
    WarehouseStatusResponse,
    COLLECTION_MODE_LABELS,
)
from backend.services.pipeline_service import (
    execute_pipeline_mode,
    list_pipeline_runs,
    get_warehouse_live_status,
)

router = APIRouter()


@router.get("/modes")
def get_collection_modes():
    """
    Returns the list of 8 collection modes matching the Trigger Pipeline Collection Modal in Screenshot 2:
    1. Full Pipeline (All Collectors + Lead Scoring + Export)
    2. Corporate Profile & Segments
    3. Social Media (Corporate & Executive)
    4. Organizational Hierarchy & Spans
    5. Personnel & Social Enrichment
    6. News & Sales Signals
    7. Lead Scoring Engine Only
    8. monid.ai Export Sync
    """
    return [
        {"key": k, "label": v}
        for k, v in COLLECTION_MODE_LABELS.items()
    ]


@router.post("/trigger", response_model=PipelineRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline_collection(
    payload: PipelineTriggerRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger a collection pipeline for a target account using any of the 8 supported modes.
    Tracks step-by-step progress, latency, cost, and yield records.
    """
    try:
        acc_uuid = UUID(str(payload.account_id))
        account = db.query(Account).filter(Account.id == acc_uuid).first()
    except (ValueError, TypeError):
        account = db.query(Account).filter(Account.name.ilike(f"%{payload.account_id}%")).first()

    if not account:
        raise HTTPException(status_code=404, detail="Target account not found")

    try:
        run = await execute_pipeline_mode(
            db=db,
            account_id=account.id,
            mode=payload.collection_mode
        )
        return PipelineRunResponse(
            id=run.id,
            run_id=run.run_id,
            account_id=run.account_id,
            account_name=account.name,
            collection_mode=run.collection_mode,
            collection_mode_label=run.collection_mode_label,
            status=run.status,
            progress_percent=run.progress_percent,
            current_step=run.current_step,
            total_steps=run.total_steps,
            steps_completed=run.steps_completed,
            step_details=run.step_details or [],
            records_created=run.records_created,
            records_updated=run.records_updated,
            total_cost_usd=float(run.total_cost_usd or 0.0),
            total_latency_seconds=float(run.total_latency_seconds or 0.0),
            error_message=run.error_message,
            started_at=run.started_at,
            completed_at=run.completed_at,
            created_at=run.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@router.get("/runs", response_model=List[PipelineRunResponse])
def get_pipeline_runs_endpoint(
    account_id: Optional[UUID] = None,
    mode: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List past and active pipeline execution runs with duration, cost, records yield, and step progress.
    """
    return list_pipeline_runs(db=db, account_id=account_id, mode=mode, status=status, limit=limit)


@router.get("/runs/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run_detail(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get step-by-step progress and logs for a specific pipeline execution run."""
    run = db.query(PipelineRun).filter(PipelineRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    return PipelineRunResponse(
        id=run.id,
        run_id=run.run_id,
        account_id=run.account_id,
        account_name=run.account.name if run.account else "Unknown",
        collection_mode=run.collection_mode,
        collection_mode_label=run.collection_mode_label or COLLECTION_MODE_LABELS.get(run.collection_mode, run.collection_mode),
        status=run.status,
        progress_percent=run.progress_percent,
        current_step=run.current_step,
        total_steps=run.total_steps,
        steps_completed=run.steps_completed,
        step_details=run.step_details or [],
        records_created=run.records_created,
        records_updated=run.records_updated,
        total_cost_usd=float(run.total_cost_usd or 0.0),
        total_latency_seconds=float(run.total_latency_seconds or 0.0),
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at
    )


@router.get("/warehouse-status", response_model=WarehouseStatusResponse)
async def get_warehouse_status_endpoint(
    db: Session = Depends(get_db)
):
    """
    Get live status of the PostgreSQL Data Warehouse and Monid.ai API sync
    matching the bottom-left UI status widget in Screenshot 1.
    """
    return await get_warehouse_live_status(db)
