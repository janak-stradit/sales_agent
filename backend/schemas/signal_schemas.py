"""Pydantic schemas for Sales Trigger Signals (Tab 6)."""

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class SalesSignalBase(BaseModel):
    account_id: UUID
    lob_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    signal_type: str
    category: str = "Sales Intent"
    title: str
    summary: str
    details: Optional[str] = None
    priority: str = "HIGH"
    urgency_score: int = 75
    confidence: str = "HIGH"
    recommended_action: Optional[str] = None
    key_talking_points: List[str] = []
    source_name: str = "Monid Intelligence Stream"
    source_url: Optional[str] = None


class SalesSignalCreate(SalesSignalBase):
    pass


class SalesSignalUpdateStatus(BaseModel):
    status: str  # NEW, ACTIONED, DISMISSED
    actioned_by: Optional[str] = None
    notes: Optional[str] = None


class SalesSignalResponse(SalesSignalBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_name: Optional[str] = None
    lob_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    status: str
    actioned_by: Optional[str] = None
    actioned_at: Optional[datetime] = None
    notes: Optional[str] = None
    detected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class SignalStatsResponse(BaseModel):
    total_signals: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    new_count: int
    actioned_count: int
    dismissed_count: int
    by_type: Dict[str, int]
    by_account: Dict[str, int]
