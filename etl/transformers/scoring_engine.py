"""
Scoring Engine — Multi-Factor 100-point lead scoring breakdown calculation.
Evaluates 6 weighted dimensions:
1. Decision Authority (Max 20 pts)
2. Seniority Tier (Max 20 pts)
3. Technographics Match (Max 20 pts)
4. Intent Signals & Strategic Initiatives (Max 20 pts)
5. Social & Thought Leadership Activity (Max 10 pts)
6. Organizational Influence & Span (Max 10 pts)
"""

from typing import Dict, Any


def calculate_lead_score_breakdown(contact_data: Dict[str, Any], persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates granular 6-factor score breakdown for a lead."""
    
    # 1. Decision Authority Score (0-20)
    auth = (contact_data.get("decision_authority") or "final").lower()
    if auth in ["final", "sole"]:
        auth_score = 20
    elif auth in ["shared", "veto"]:
        auth_score = 16
    elif auth in ["influencer", "technical"]:
        auth_score = 12
    else:
        auth_score = 8

    # 2. Seniority Tier Score (0-20)
    tier = (contact_data.get("seniority_tier") or "CXO").upper()
    if tier in ["CXO", "C-SUITE", "PRESIDENT", "CEO", "CIO", "CTO"]:
        seniority_score = 20
    elif tier in ["EVP", "SVP", "SENIOR EXECUTIVE VP"]:
        seniority_score = 18
    elif tier in ["VP", "VICE PRESIDENT", "MANAGING DIRECTOR"]:
        seniority_score = 15
    elif tier in ["DIRECTOR", "HEAD"]:
        seniority_score = 12
    else:
        seniority_score = 8

    # 3. Technographics Match Score (0-20)
    tech_list = persona_data.get("tech_stack") or ["Snowflake", "AWS", "Kafka"]
    high_value_techs = ["snowflake", "aws", "kubernetes", "kafka", "databricks", "terraform"]
    match_count = sum(1 for t in tech_list if any(h in t.lower() for h in high_value_techs))
    tech_score = min(20, max(10, match_count * 4))

    # 4. Intent Signals & Initiatives Score (0-20)
    pain_points = persona_data.get("operational_pain_points") or []
    intent_score = 20 if len(pain_points) >= 2 else 14

    # 5. Social & Thought Leadership Score (0-10)
    social_posts = persona_data.get("recent_scraped_posts") or []
    social_score = 10 if len(social_posts) >= 1 else 6

    # 6. Organizational Influence Score (0-10)
    org_score = 10 if tier in ["CXO", "EVP", "C-SUITE"] else 8

    total = auth_score + seniority_score + tech_score + intent_score + social_score + org_score
    total = min(100, max(0, total))

    status = "Hot" if total >= 80 else ("Warm" if total >= 50 else "Cold")

    return {
        "decision_authority_score": auth_score,
        "seniority_score": seniority_score,
        "tech_stack_match_score": tech_score,
        "intent_signals_score": intent_score,
        "social_activity_score": social_score,
        "org_influence_score": org_score,
        "total_score": total,
        "max_score": 100,
        "tier": status
    }
