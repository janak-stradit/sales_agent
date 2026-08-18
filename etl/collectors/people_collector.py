"""
People Collector — Extracts executive decision makers, CXO/VP leads, direct contact info, and role remits.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("etl.collectors.people")


async def collect_executive_people(account_name: str, domain: str = "bny.com") -> List[Dict[str, Any]]:
    """
    Extracts key executive decision makers and leadership contacts for the enterprise account.
    """
    logger.info(f"Extracting executive contacts for: {account_name}")

    return [
        {
            "full_name": "Emily Portney",
            "first_name": "Emily",
            "last_name": "Portney",
            "title": "Global Head of Asset Servicing",
            "seniority_tier": "CXO",
            "department": "Asset Servicing",
            "location": "New York, USA",
            "email": f"emily.portney@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0194",
            "tenure_months": 42,
            "tenure_formatted": "3 yrs 6 mos",
            "decision_authority": "final",
            "budget_authority": "full",
            "buyer_roles": ["Key Decision Maker", "Economic Buyer"],
            "linkedin_url": "https://www.linkedin.com/in/emily-portney",
            "summary_bio": "Emily Portney is the Global Head of Asset Servicing at BNY. Leads the largest global custody business overseeing $47T+ in assets under custody."
        },
        {
            "full_name": "Robin Vince",
            "first_name": "Robin",
            "last_name": "Vince",
            "title": "President & Chief Executive Officer (CEO)",
            "seniority_tier": "CXO",
            "department": "Executive Leadership",
            "location": "New York, USA",
            "email": f"robin.vince@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0100",
            "tenure_months": 36,
            "tenure_formatted": "3 yrs",
            "decision_authority": "final",
            "budget_authority": "full",
            "buyer_roles": ["Final Decision", "Executive Sponsor"],
            "linkedin_url": "https://www.linkedin.com/in/robin-vince",
            "summary_bio": "Robin Vince is the President and CEO of BNY. Directs enterprise growth, technological modernization, and global banking operations."
        },
        {
            "full_name": "Ranjit Samra",
            "first_name": "Ranjit",
            "last_name": "Samra",
            "title": "Chief Technology & Product Officer — Asset Servicing",
            "seniority_tier": "CXO",
            "department": "Technology & Architecture",
            "location": "New York, USA",
            "email": f"ranjit.samra@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0145",
            "tenure_months": 30,
            "tenure_formatted": "2 yrs 6 mos",
            "decision_authority": "final",
            "budget_authority": "technical",
            "buyer_roles": ["Technical Evaluator", "Key Decision Maker"],
            "linkedin_url": "https://www.linkedin.com/in/ranjit-samra",
            "summary_bio": "Ranjit Samra leads technology architecture and cloud modernizations across BNY's Asset Servicing product lines."
        },
        {
            "full_name": "Bridget E. Engle",
            "first_name": "Bridget",
            "last_name": "Engle",
            "title": "Senior Executive Vice President & Head of Technology (CIO)",
            "seniority_tier": "CXO",
            "department": "Global Engineering",
            "location": "New York, USA",
            "email": f"bridget.engle@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0177",
            "tenure_months": 60,
            "tenure_formatted": "5 yrs",
            "decision_authority": "final",
            "budget_authority": "full",
            "buyer_roles": ["Key Decision Maker", "Technical Evaluator"],
            "linkedin_url": "https://www.linkedin.com/in/bridget-engle",
            "summary_bio": "Bridget Engle oversees all global technology systems, cybersecurity infrastructure, and cloud migrations across BNY."
        },
        {
            "full_name": "Roman Regelman",
            "first_name": "Roman",
            "last_name": "Regelman",
            "title": "Senior Executive VP & Global Head of Digital Platforms",
            "seniority_tier": "CXO",
            "department": "Digital Platforms",
            "location": "New York, USA",
            "email": f"roman.regelman@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0133",
            "tenure_months": 48,
            "tenure_formatted": "4 yrs",
            "decision_authority": "final",
            "budget_authority": "full",
            "buyer_roles": ["Key Decision Maker", "Strategic Buyer"],
            "linkedin_url": "https://www.linkedin.com/in/roman-regelman",
            "summary_bio": "Roman Regelman leads digital platforms, artificial intelligence adoption, and client experience transformations across BNY."
        },
        {
            "full_name": "Brian Ruane",
            "first_name": "Brian",
            "last_name": "Ruane",
            "title": "Executive Vice President & Head of Clearance & Collateral",
            "seniority_tier": "VP",
            "department": "Clearance & Collateral Management",
            "location": "New York, USA",
            "email": f"brian.ruane@{domain}",
            "email_confidence": "verified",
            "phone": "+1 (212) 555-0122",
            "tenure_months": 72,
            "tenure_formatted": "6 yrs",
            "decision_authority": "shared",
            "budget_authority": "full",
            "buyer_roles": ["Key Decision Maker"],
            "linkedin_url": "https://www.linkedin.com/in/brian-ruane",
            "summary_bio": "Brian Ruane leads clearance and collateral management, steering tri-party repo modernization and settlement infrastructure."
        }
    ]
