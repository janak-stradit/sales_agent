"""SignalsService — Buying Signals, Modernization Triggers & Action Playbooks (Tab 6)."""

import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.models.account import Account
from backend.models.contact import Contact
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.schemas.signal_schemas import (
    SalesSignalResponse,
    SalesSignalCreate,
    SalesSignalUpdateStatus,
    SignalStatsResponse,
)

logger = logging.getLogger(__name__)


def list_signals(
    db: Session,
    account_id: Optional[UUID] = None,
    signal_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    min_urgency: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> List[SalesSignalResponse]:
    """Retrieves paginated buying signals with rich filtering."""
    query = db.query(SalesTriggerSignal)

    if account_id:
        query = query.filter(SalesTriggerSignal.account_id == account_id)
    if signal_type:
        query = query.filter(SalesTriggerSignal.signal_type.ilike(signal_type))
    if priority:
        query = query.filter(SalesTriggerSignal.priority.ilike(priority))
    if status:
        query = query.filter(SalesTriggerSignal.status.ilike(status))
    if min_urgency:
        query = query.filter(SalesTriggerSignal.urgency_score >= min_urgency)

    signals = query.order_by(SalesTriggerSignal.urgency_score.desc(), SalesTriggerSignal.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for s in signals:
        contact_name = s.contact.full_name if s.contact else None
        contact_title = s.contact.title if s.contact else None
        results.append(SalesSignalResponse(
            id=s.id,
            account_id=s.account_id,
            account_name=s.account.name if s.account else "Unknown",
            lob_id=s.lob_id,
            lob_name=s.lob.name if s.lob else None,
            contact_id=s.contact_id,
            contact_name=contact_name,
            contact_title=contact_title,
            signal_type=s.signal_type,
            category=s.category or "Sales Intent",
            title=s.title,
            summary=s.summary,
            details=s.details,
            priority=s.priority,
            urgency_score=s.urgency_score,
            confidence=s.confidence,
            recommended_action=s.recommended_action,
            key_talking_points=s.key_talking_points or [],
            source_name=s.source_name,
            source_url=s.source_url,
            status=s.status,
            actioned_by=s.actioned_by,
            actioned_at=s.actioned_at,
            notes=s.notes,
            detected_at=s.detected_at,
            created_at=s.created_at
        ))

    return results


def get_signal_detail(db: Session, signal_id: UUID) -> SalesSignalResponse:
    """Gets detailed info for a single trigger signal with action recommendations."""
    s = db.query(SalesTriggerSignal).filter(SalesTriggerSignal.id == signal_id).first()
    if not s:
        raise ValueError(f"Signal {signal_id} not found")

    contact_name = s.contact.full_name if s.contact else None
    contact_title = s.contact.title if s.contact else None

    return SalesSignalResponse(
        id=s.id,
        account_id=s.account_id,
        account_name=s.account.name if s.account else "Unknown",
        lob_id=s.lob_id,
        lob_name=s.lob.name if s.lob else None,
        contact_id=s.contact_id,
        contact_name=contact_name,
        contact_title=contact_title,
        signal_type=s.signal_type,
        category=s.category or "Sales Intent",
        title=s.title,
        summary=s.summary,
        details=s.details,
        priority=s.priority,
        urgency_score=s.urgency_score,
        confidence=s.confidence,
        recommended_action=s.recommended_action,
        key_talking_points=s.key_talking_points or [],
        source_name=s.source_name,
        source_url=s.source_url,
        status=s.status,
        actioned_by=s.actioned_by,
        actioned_at=s.actioned_at,
        notes=s.notes,
        detected_at=s.detected_at,
        created_at=s.created_at
    )


def create_signal(db: Session, payload: SalesSignalCreate) -> SalesSignalResponse:
    """Creates a new sales trigger signal."""
    sig = SalesTriggerSignal(
        account_id=payload.account_id,
        lob_id=payload.lob_id,
        contact_id=payload.contact_id,
        signal_type=payload.signal_type,
        category=payload.category,
        title=payload.title,
        summary=payload.summary,
        details=payload.details,
        priority=payload.priority,
        urgency_score=payload.urgency_score,
        confidence=payload.confidence,
        recommended_action=payload.recommended_action,
        key_talking_points=payload.key_talking_points,
        source_name=payload.source_name,
        source_url=payload.source_url,
        status="NEW",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(sig)
    db.commit()
    db.refresh(sig)
    return get_signal_detail(db, sig.id)


def update_signal_status(db: Session, signal_id: UUID, payload: SalesSignalUpdateStatus) -> SalesSignalResponse:
    """Updates status of a signal (e.g. from NEW to ACTIONED or DISMISSED)."""
    s = db.query(SalesTriggerSignal).filter(SalesTriggerSignal.id == signal_id).first()
    if not s:
        raise ValueError(f"Signal {signal_id} not found")

    s.status = payload.status
    if payload.status == "ACTIONED":
        s.actioned_by = payload.actioned_by or "Sales Executive"
        s.actioned_at = datetime.now(timezone.utc)
    if payload.notes:
        s.notes = payload.notes

    db.commit()
    db.refresh(s)
    return get_signal_detail(db, signal_id)


def get_signal_stats(db: Session, account_id: Optional[UUID] = None) -> SignalStatsResponse:
    """Computes signal counts by priority, type, and account."""
    query = db.query(SalesTriggerSignal)
    if account_id:
        query = query.filter(SalesTriggerSignal.account_id == account_id)

    total = query.count()
    crit = query.filter(SalesTriggerSignal.priority == "CRITICAL").count()
    high = query.filter(SalesTriggerSignal.priority == "HIGH").count()
    med = query.filter(SalesTriggerSignal.priority == "MEDIUM").count()
    low = query.filter(SalesTriggerSignal.priority == "LOW").count()

    new_cnt = query.filter(SalesTriggerSignal.status == "NEW").count()
    act_cnt = query.filter(SalesTriggerSignal.status == "ACTIONED").count()
    dism_cnt = query.filter(SalesTriggerSignal.status == "DISMISSED").count()

    all_signals = query.all()
    by_type: Dict[str, int] = {}
    by_account: Dict[str, int] = {}

    for s in all_signals:
        by_type[s.signal_type] = by_type.get(s.signal_type, 0) + 1
        aname = s.account.name if s.account else "Unknown"
        by_account[aname] = by_account.get(aname, 0) + 1

    return SignalStatsResponse(
        total_signals=total,
        critical_count=crit,
        high_count=high,
        medium_count=med,
        low_count=low,
        new_count=new_cnt,
        actioned_count=act_cnt,
        dismissed_count=dism_cnt,
        by_type=by_type,
        by_account=by_account
    )
