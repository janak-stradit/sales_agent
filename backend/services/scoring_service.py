"""
ScoringService — Lead score calculator (0–100).

Scoring breakdown:
  +25  Decision maker
  +20  C-Suite / VP seniority
  +15  Relevant tech stack
  +20  Intent signals (pain points)
  +10  Active LinkedIn presence
  +10  High influence score
  ────
  100  Maximum possible
"""

from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.org_hierarchy import OrgHierarchy


RELEVANT_TECH = {"aws", "azure", "snowflake", "databricks", "salesforce", "kubernetes", "terraform"}
INTENT_KEYWORDS = {"digital transformation", "ai", "cloud", "automation", "modernization", "migration"}


def calculate_lead_score(
    contact: Contact,
    persona: Persona = None,
    hierarchy: OrgHierarchy = None,
) -> int:
    """Calculate a 0–100 lead score for a contact."""
    score = 0

    # Decision maker: +25
    if contact.is_decision_maker:
        score += 25

    # Seniority: +20 for C-Suite/VP, +10 for Director
    seniority = (contact.seniority or "").lower()
    if seniority in ("c-suite", "vp"):
        score += 20
    elif seniority == "director":
        score += 10
    elif seniority == "manager":
        score += 5

    # Tech stack relevance: +15
    if persona and persona.professional_behavior:
        tech = {t.lower() for t in persona.professional_behavior.get("tech_stack", [])}
        if tech & RELEVANT_TECH:
            score += 15

    # Intent signals from pain points: +20
    if persona and persona.professional_behavior:
        pains = {p.lower() for p in persona.professional_behavior.get("pain_points", [])}
        if pains & INTENT_KEYWORDS:
            score += 20

    # Active LinkedIn: +10
    if persona and persona.personal_touch:
        activity_score = persona.personal_touch.get("linkedin_activity_score", 0)
        if activity_score > 50:
            score += 10

    # Influence score from hierarchy: +10
    if hierarchy and hierarchy.influence_score and hierarchy.influence_score > 70:
        score += 10

    return min(score, 100)
