"""API Router for Organizational Hierarchy (Tab 4)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from backend.database import get_db
from backend.models.account import Account
from backend.models.contact import Contact
from backend.schemas.hierarchy_schemas import (
    HierarchyTreeNodeResponse,
    SpanOfControlMetricsResponse,
    ReportingChainResponse,
)
from backend.services.hierarchy_service import (
    build_hierarchy_tree,
    get_span_of_control_metrics,
    get_reporting_chain,
)

router = APIRouter()


@router.get("/tree/{account_id}", response_model=List[HierarchyTreeNodeResponse])
def get_hierarchy_tree_endpoint(
    account_id: UUID,
    lob_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get full nested organizational tree representation starting from the CEO / Root level down to leaf nodes.
    Supports filtering by specific Line of Business (LOB).
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return build_hierarchy_tree(db, account_id, lob_id)


@router.get("/spans/{account_id}", response_model=SpanOfControlMetricsResponse)
def get_spans_metrics_endpoint(account_id: UUID, db: Session = Depends(get_db)):
    """
    Get organizational span of control analytics, maximum depth, level distribution,
    and decision authority power distribution for a target account.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return get_span_of_control_metrics(db, account_id)


@router.get("/chain/{contact_id}", response_model=ReportingChainResponse)
def get_contact_chain_endpoint(contact_id: UUID, db: Session = Depends(get_db)):
    """
    Get the complete upward reporting chain to the CEO/Board and downward direct reports
    for a specific executive contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    try:
        return get_reporting_chain(db, contact_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
