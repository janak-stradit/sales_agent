"""
Playbook Generator — Generates personalized cold outreach assets, objection handling battlecards,
and 14-day multi-touch sales cadences.
"""

from typing import Dict, Any, List


def generate_cold_outreach_playbook(contact: Dict[str, Any], persona: Dict[str, Any], account_name: str = "BNY") -> Dict[str, Any]:
    """Generates 1-click cold email, LinkedIn DM, phone hook, and objection battlecards."""
    first_name = contact.get("first_name") or "there"
    title = contact.get("title") or "Executive Leader"
    tech_stack = persona.get("tech_stack") or ["Snowflake", "AWS"]
    primary_tech = tech_stack[0] if tech_stack else "modern data architecture"
    pain_points = persona.get("operational_pain_points") or [f"data synchronization latency across {account_name}"]
    primary_pain = pain_points[0]
    kpis = persona.get("target_kpis") or ["sub-second data delivery SLAs"]

    email_subject = f"Quick question on data infrastructure at {account_name}"
    email_body = f"""Hi {first_name},

Saw your recent post on cloud modernization — really resonated with how you're steering technology strategy at {account_name}.

Given your focus on {kpis[0]}, we've helped similar institutional leaders tackle {primary_pain.lower()} without ripping and replacing their {primary_tech} stack.

We recently helped a peer eliminate 85% of downstream reconciliation lag while cutting infrastructure overhead.

Would you be open to a brief 10-minute intro this Thursday at 2:00 PM to see how we benchmark against your 2026 roadmap?

Best regards,
[Your Name]
Enterprise Sales Team"""

    linkedin_dm = f"Hi {first_name}, loved your thoughts on modernizing institutional infrastructure. We're helping enterprise leaders in capital markets resolve {primary_pain.lower()} on top of {primary_tech}. Would love to connect and share our benchmark findings!"

    cold_call_opening = f"Hi {first_name}, I know I'm catching you unannounced. The reason for my call is your leadership of technology at {account_name}. We're working with enterprise leaders to resolve {primary_pain.lower()} across {primary_tech} environments. Do you have 60 seconds for me to tell you why we called?"

    objections = [
        {
            "id": "obj-build",
            "objection": "We are building this internally with our engineering team.",
            "category": "Build vs. Buy",
            "recommended_rebuttal": f"Completely respect that — most Tier-1 institutions at {account_name}'s scale start in-house. Where we partner is eliminating the 18-month maintenance backlog so your engineers stay focused on proprietary IP rather than data plumbing.",
            "delivery_tone": "Consultative & Respectful",
            "battlecard_note": "Acknowledge internal engineering caliber; pivot immediately to time-to-market and opportunity cost."
        },
        {
            "id": "obj-vendor",
            "objection": "We are locked into our existing multi-year vendor contract.",
            "category": "Contract Lock-In",
            "recommended_rebuttal": f"Understood. We actually sit on top of your existing {primary_tech} stack without requiring contract termination or migration risk. Let's benchmark the performance delta so you have the data ahead of your next renewal cycle.",
            "delivery_tone": "Strategic & Non-Disruptive",
            "battlecard_note": "Emphasize zero-migration overlay architecture and pre-renewal benchmark leverage."
        },
        {
            "id": "obj-budget",
            "objection": "We don't have an allocated budget line item this quarter.",
            "category": "Budget Timing",
            "recommended_rebuttal": f"Totally fair. Given your {kpis[0]} targets for 2026, let's complete a 5-day architectural proof-of-concept now so you have validated numbers ready for your Q3 budget cycle.",
            "delivery_tone": "Low-Pressure & ROI-Oriented",
            "battlecard_note": "Offer zero-risk POC evaluation to secure line-item inclusion in upcoming procurement cycle."
        },
        {
            "id": "obj-email",
            "objection": "Just send me an email and I'll review it with my team.",
            "category": "Gatekeeping / Deflection",
            "recommended_rebuttal": f"Happy to do that {first_name}. To ensure I send only the relevant 1-page architecture brief, are you primarily focused on {primary_pain} or broader {primary_tech} cost optimization?",
            "delivery_tone": "Sharp & Qualifying",
            "battlecard_note": "Agree to email immediately, then ask a binary qualifying question to uncover active technical focus."
        }
    ]

    return {
        "recommended_angle": f"Zero-Lag Architecture on {primary_tech}",
        "email_subject": email_subject,
        "email_body": email_body,
        "linkedin_dm": linkedin_dm,
        "cold_call_opening": cold_call_opening,
        "value_proposition": f"Enabling {account_name} to eliminate data reconciliation bottlenecks and achieve sub-second latency across {primary_tech} architectures.",
        "objection_handling_list": objections
    }


def generate_14day_cadence(contact: Dict[str, Any], playbook: Dict[str, Any], account_name: str = "BNY") -> List[Dict[str, Any]]:
    """Generates the 5-step 14-day multi-touch sales cadence."""
    first_name = contact.get("first_name") or "there"
    return [
        {
            "step": 1,
            "day": "Day 1",
            "channel": "Email",
            "channel_icon": "fa-envelope text-blue-500",
            "title": "Trigger-Based Cold Email",
            "description": f"Personalized email addressing active latency bottlenecks and operational SLAs.",
            "status": "READY",
            "preview": playbook.get("email_subject", "Quick question on data infrastructure")
        },
        {
            "step": 2,
            "day": "Day 3",
            "channel": "LinkedIn",
            "channel_icon": "fa-brands fa-linkedin text-blue-600",
            "title": "LinkedIn Connection & Post Engagement",
            "description": f"Like/comment on {first_name}'s recent thought leadership post and send concise InMail note.",
            "status": "READY",
            "preview": (playbook.get("linkedin_dm") or "")[:70] + "..."
        },
        {
            "step": 3,
            "day": "Day 7",
            "channel": "Phone",
            "channel_icon": "fa-phone text-emerald-500",
            "title": "15-Second Direct Elevator Hook",
            "description": f"Targeted direct line call with respectful permission-based opening.",
            "status": "READY",
            "preview": (playbook.get("cold_call_opening") or "")[:70] + "..."
        },
        {
            "step": 4,
            "day": "Day 10",
            "channel": "Email Followup",
            "channel_icon": "fa-file-lines text-indigo-500",
            "title": "Technical Benchmark Architecture One-Pager",
            "description": f"Share 1-page PDF case study comparing zero-lag streaming vs legacy batch.",
            "status": "READY",
            "preview": f"Re: {playbook.get('email_subject', '')} — 1-page architecture benchmark attached"
        },
        {
            "step": 5,
            "day": "Day 14",
            "channel": "Email",
            "channel_icon": "fa-calendar-check text-amber-500",
            "title": "Executive Breakup & Calendar Link",
            "description": f"Polite closing note leaving open door for {first_name}'s Q3/Q4 budget planning cycle.",
            "status": "READY",
            "preview": f"Permission to close the loop for {account_name}?"
        }
    ]
