"""SocialIntelligence — Corporate & Executive Social Posts, Activity & Sentiment (Tab 5)."""

import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class SocialIntelligence(Base):
    __tablename__ = "social_intelligence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Classification
    entity_type = Column(String(50), default="EXECUTIVE")     # CORPORATE or EXECUTIVE
    platform = Column(String(50), default="LINKEDIN")          # LINKEDIN, TWITTER, NEWS, BLOG
    author_name = Column(String(255), nullable=False)
    author_title = Column(String(255))
    author_avatar_url = Column(String(500))
    post_url = Column(String(1000))

    # Content
    content = Column(Text, nullable=False)
    headline = Column(String(500))
    post_date = Column(DateTime(timezone=True), default=func.now())
    post_date_formatted = Column(String(100))

    # Engagement Metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    engagement_formatted = Column(String(100))                 # e.g. "342 likes, 48 comments"

    # Sentiment & Semantic Intelligence
    sentiment = Column(String(50), default="POSITIVE")         # POSITIVE, NEUTRAL, NEGATIVE
    sentiment_score = Column(Float, default=0.5)               # -1.0 to 1.0
    topic_tags = Column(ARRAY(String), default=[])             # e.g. ["CloudModernization", "ISO20022", "AssetServicing"]
    pain_point_signals = Column(ARRAY(String), default=[])
    key_entities = Column(JSONB, default=[])

    # Raw Payload & Timestamps
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("Account", back_populates="social_posts")
    contact = relationship("Contact", back_populates="social_posts")

    __table_args__ = (
        Index("idx_social_account_platform", "account_id", "platform"),
        Index("idx_social_contact_date", "contact_id", "post_date"),
    )

    def __repr__(self):
        return f"<SocialIntelligence(author='{self.author_name}', platform='{self.platform}', sentiment='{self.sentiment}')>"
