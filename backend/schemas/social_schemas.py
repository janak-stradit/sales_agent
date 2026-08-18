"""Pydantic schemas for Social Intelligence (Tab 5)."""

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class SocialPostBase(BaseModel):
    account_id: UUID
    contact_id: Optional[UUID] = None
    entity_type: str = "EXECUTIVE"
    platform: str = "LINKEDIN"
    author_name: str
    author_title: Optional[str] = None
    author_avatar_url: Optional[str] = None
    post_url: Optional[str] = None
    content: str
    headline: Optional[str] = None
    post_date_formatted: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    engagement_rate: float = 0.0
    engagement_formatted: Optional[str] = None
    sentiment: str = "POSITIVE"
    sentiment_score: float = 0.5
    topic_tags: List[str] = []
    pain_point_signals: List[str] = []


class SocialPostCreate(SocialPostBase):
    pass


class SocialPostResponse(SocialPostBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_name: Optional[str] = None
    post_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class TrendingTopicItem(BaseModel):
    topic: str
    count: int
    sentiment: str


class SocialAnalyticsResponse(BaseModel):
    total_posts: int
    sentiment_distribution: Dict[str, float]  # positive_pct, neutral_pct, negative_pct
    average_sentiment_score: float
    platform_distribution: Dict[str, int]
    trending_topics: List[TrendingTopicItem]
    average_engagement_rate: float
    top_engaging_posts: List[SocialPostResponse]


class ExecutiveSocialProfileResponse(BaseModel):
    contact_id: UUID
    author_name: str
    author_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    follower_count: int = 0
    connection_count: int = 0
    total_posts: int
    average_sentiment_score: float
    sentiment_label: str
    top_topics: List[str]
    recent_posts: List[SocialPostResponse]
