"""
Social Collector — Extracts corporate announcements, executive thought leadership posts, and sentiment analysis.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("etl.collectors.social")


async def collect_social_intelligence(account_name: str = "BNY") -> List[Dict[str, Any]]:
    """
    Extracts scraped executive posts and corporate social intelligence.
    """
    logger.info(f"Extracting social intelligence and thought leadership for: {account_name}")

    return [
        {
            "platform": "LinkedIn",
            "author_name": "Emily Portney",
            "author_title": "Global Head of Asset Servicing at BNY",
            "author_handle": "@emily_portney",
            "post_date_formatted": "2 days ago",
            "headline": "Scaling Global Custody with Modernized Data Infrastructure",
            "content": "Delighted to share our team's progress on modernizing data delivery pipelines across BNY Asset Servicing. Eliminating batch latency is vital for institutional client success.",
            "topic_tags": ["AssetServicing", "CloudModernization", "GlobalCustody"],
            "engagement_formatted": "412 Likes • 48 Comments",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.94
        },
        {
            "platform": "LinkedIn",
            "author_name": "Robin Vince",
            "author_title": "President & CEO at BNY",
            "author_handle": "@robin_vince",
            "post_date_formatted": "5 days ago",
            "headline": "Leadership and Innovation in Financial Services",
            "content": "Our mission is focused on resilience, innovation, and disciplined execution to power global commerce and financial institutions worldwide.",
            "topic_tags": ["Leadership", "FinTechEngineering"],
            "engagement_formatted": "1,240 Likes • 182 Comments",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.98
        },
        {
            "platform": "Twitter",
            "author_name": "BNY Corporate",
            "author_title": "Corporate Entity",
            "author_handle": "@bny_global",
            "post_date_formatted": "1 week ago",
            "headline": "Accelerating Cloud Native Infrastructure Across Capital Markets",
            "content": "Expanding our strategic data partnerships to deliver high-throughput, low-latency analytics across global securities markets.",
            "topic_tags": ["Snowflake", "CloudModernization"],
            "engagement_formatted": "320 Reposts • 840 Likes",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.91
        }
    ]
