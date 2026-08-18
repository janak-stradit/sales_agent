"""API Router for Sales Trigger Signals (Tab 6)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from backend.database import get_db
from backend.schemas.signal_schemas import (
    SalesSignalResponse,
    SalesSignalCreate,
    SalesSignalUpdateStatus,
    SignalStatsResponse,
)
from backend.services.signals_service import (
    list_signals,
    get_signal_detail,
    update_signal_status,
    get_signal_stats,
)

router = APIRouter()


@router.get("/", response_model=List[SalesSignalResponse])
def list_signals_endpoint(
    account_id: Optional[UUID] = None,
    signal_type: Optional[str] = None,   # LEADERSHIP_CHANGE, TECH_STACK_MODERNIZATION, etc.
    priority: Optional[str] = None,      # CRITICAL, HIGH, MEDIUM, LOW
    status: Optional[str] = None,        # NEW, ACTIONED, DISMISSED
    min_urgency: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List sales trigger signals and modernization buying events.
    Supports filtering by account, signal type, urgency score, and workflow status.
    """
    return list_signals(
        db=db,
        account_id=account_id,
        signal_type=signal_type,
        priority=priority,
        status=status,
        min_urgency=min_urgency,
        limit=limit,
        offset=offset
    )


@router.get("/stats", response_model=SignalStatsResponse)
def get_signal_stats_endpoint(
    account_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated signal metrics by urgency priority, category, and target accounts.
    """
    return get_signal_stats(db=db, account_id=account_id)


@router.get("/{signal_id}", response_model=SalesSignalResponse)
def get_signal_detail_endpoint(
    signal_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get full buying signal detail with context, source evidence URL, and recommended outreach playbook.
    """
    try:
        return get_signal_detail(db=db, signal_id=signal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{signal_id}/status", response_model=SalesSignalResponse)
def update_signal_status_endpoint(
    signal_id: UUID,
    payload: SalesSignalUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Update workflow status for a signal (e.g. mark as ACTIONED or DISMISSED with notes).
    """
    try:
        return update_signal_status(db=db, signal_id=signal_id, payload=payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
