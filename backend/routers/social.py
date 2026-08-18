"""API Router for Social Intelligence (Tab 5)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from backend.database import get_db
from backend.models.contact import Contact
from backend.models.account import Account
from backend.schemas.social_schemas import (
    SocialPostResponse,
    SocialAnalyticsResponse,
    ExecutiveSocialProfileResponse,
)
from backend.services.social_service import (
    list_social_posts,
    get_social_analytics,
    get_executive_social_profile,
)

router = APIRouter()


@router.get("/feed", response_model=List[SocialPostResponse])
def get_social_feed_endpoint(
    account_id: Optional[UUID] = None,
    contact_id: Optional[UUID] = None,
    platform: Optional[str] = None,      # LINKEDIN, TWITTER, NEWS
    sentiment: Optional[str] = None,     # POSITIVE, NEUTRAL, NEGATIVE
    entity_type: Optional[str] = None,   # CORPORATE, EXECUTIVE
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get paginated social intelligence feed from corporate accounts and executive leadership.
    Supports filtering by platform, sentiment, entity type, and full-text keyword search.
    """
    return list_social_posts(
        db=db,
        account_id=account_id,
        contact_id=contact_id,
        platform=platform,
        sentiment=sentiment,
        entity_type=entity_type,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get("/analytics", response_model=SocialAnalyticsResponse)
def get_social_analytics_endpoint(
    account_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated sentiment analysis, platform breakdown, and trending modernization topic tags
    across target accounts.
    """
    return get_social_analytics(db=db, account_id=account_id)


@router.get("/executive/{contact_id}", response_model=ExecutiveSocialProfileResponse)
def get_executive_social_endpoint(
    contact_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get individual executive's scraped LinkedIn footprint, followers, recent posts, and sentiment trends.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Executive contact not found")

    try:
        return get_executive_social_profile(db=db, contact_id=contact_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
