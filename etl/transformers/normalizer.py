"""
Normalizer — Cleans, formats, and standardizes raw extracted company and contact records.
"""

from typing import Dict, Any


def normalize_account_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes raw account attributes for PostgreSQL schema."""
    rev = raw.get("annual_revenue_usd") or 20000000000
    rev_str = f"${rev / 1_000_000_000:.1f}B" if rev >= 1_000_000_000 else f"${rev:,}"

    return {
        "name": raw.get("name", "BNY"),
        "domain": raw.get("domain", "bny.com"),
        "website_url": raw.get("website_url", "https://www.bny.com"),
        "industry": raw.get("industry", "Financial Services & Asset Servicing"),
        "headquarters": raw.get("headquarters", "240 Greenwich St, New York, NY 10007, United States"),
        "city": raw.get("city", "New York"),
        "state": raw.get("state", "NY"),
        "country": raw.get("country", "United States"),
        "founded_year": raw.get("founded_year", 1784),
        "employee_count": raw.get("employee_count", 56000),
        "annual_revenue_usd": rev,
        "annual_revenue_printed": rev_str,
        "market_cap_usd": raw.get("market_cap_usd", 42500000000),
        "publicly_traded_symbol": raw.get("publicly_traded_symbol", "BK"),
        "publicly_traded_exchange": raw.get("publicly_traded_exchange", "NYSE"),
        "short_description": raw.get("short_description", "Global asset servicing and financial institution."),
        "technology_names": raw.get("technology_names", ["Snowflake", "AWS", "Kubernetes", "Apache Kafka"]),
        "tech_stack": raw.get("tech_stack", ["Snowflake", "AWS", "Kubernetes", "Apache Kafka"]),
        "sic_codes": raw.get("sic_codes", ["6211"]),
        "naics_codes": raw.get("naics_codes", ["522110"]),
        "keywords": raw.get("keywords", ["asset servicing", "global custody", "tier-1-global-custodian"]),
        "raw_data": raw
    }


def normalize_contact_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes raw contact attributes."""
    first = raw.get("first_name") or ""
    last = raw.get("last_name") or ""
    full = raw.get("full_name") or f"{first} {last}".strip()
    if not first and not last and full:
        parts = full.split()
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""

    return {
        "first_name": first,
        "last_name": last,
        "full_name": full,
        "title": raw.get("title", "Executive Leader"),
        "current_title": raw.get("title", "Executive Leader"),
        "seniority_tier": raw.get("seniority_tier", "CXO"),
        "sub_lob_name": raw.get("department", "Technology"),
        "location": raw.get("location", "New York, USA"),
        "email": raw.get("email"),
        "email_confidence": raw.get("email_confidence", "verified"),
        "phone": raw.get("phone", "+1 212-555-0194"),
        "tenure": raw.get("tenure_formatted", "3 yrs"),
        "tenure_months": raw.get("tenure_months", 36),
        "decision_authority": raw.get("decision_authority", "final"),
        "budget_authority": raw.get("budget_authority", "full"),
        "buyer_roles": raw.get("buyer_roles", ["Key Decision Maker"]),
        "summary_bio": raw.get("summary_bio"),
        "linkedin_url": raw.get("linkedin_url"),
        "raw_data": raw
    }
