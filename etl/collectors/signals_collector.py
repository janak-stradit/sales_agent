"""
Signals Collector — Extracts high-urgency buying trigger signals, intent events, and strategic initiatives.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("etl.collectors.signals")


async def collect_intent_signals(account_name: str = "BNY") -> List[Dict[str, Any]]:
    """
    Extracts sales trigger signals, urgency levels, and recommended sales plays.
    """
    logger.info(f"Extracting sales buying trigger signals for: {account_name}")

    return [
        {
            "signal_type": "STRATEGIC_INITIATIVE",
            "event_category": "Cloud & Data Modernization",
            "title": f"Leadership Strategic Push in {account_name} Asset Servicing Technology",
            "summary": f"{account_name} has initiated an enterprise-wide modernization mandate to reduce custodial latency and improve real-time client reporting.",
            "urgency_score": 92,
            "priority": "CRITICAL",
            "detected_at": "2026-08-16T14:30:00Z",
            "status": "OPEN",
            "recommended_action": "Outreach to Emily Portney and Ranjit Samra highlighting latency reduction benchmarks on Snowflake & Kafka."
        },
        {
            "signal_type": "EXECUTIVE_EXPANSION",
            "event_category": "Executive Mandate",
            "title": f"{account_name} Appoints Head of Digital Platforms to Accelerate AI",
            "summary": "Expansion of digital platform leadership focused on automating reconciliation and trade lifecycle management.",
            "urgency_score": 85,
            "priority": "HIGH",
            "detected_at": "2026-08-14T09:15:00Z",
            "status": "OPEN",
            "recommended_action": "Present AI-driven automated reporting architecture brief to Roman Regelman."
        },
        {
            "signal_type": "BUDGET_ALLOCATION",
            "event_category": "Annual Procurement",
            "title": f"{account_name} Q3/Q4 Strategic Technology Investment Allocation",
            "summary": "Annual technology infrastructure budget confirmed for capital expenditure on sub-second data streaming layers.",
            "urgency_score": 80,
            "priority": "HIGH",
            "detected_at": "2026-08-12T11:00:00Z",
            "status": "OPEN",
            "recommended_action": "Initiate 14-day multi-touch cadence with key decision makers to schedule POC evaluations."
        }
    ]
