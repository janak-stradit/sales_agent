"""
Contact Loader — Loads contacts, 3-level personas, hierarchy nodes, social posts, and buying signals.
"""

import logging
from sqlalchemy.orm import Session
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.org_hierarchy import OrgHierarchy
from backend.models.social_intelligence import SocialIntelligence
from backend.models.sales_trigger_signal import SalesTriggerSignal

logger = logging.getLogger("etl.loaders.contact")


def load_contact_bundle(
    db: Session,
    account: Account,
    people_list: list,
    personas_map: dict,
    hierarchy_list: list,
    social_posts: list,
    signals_list: list
):
    """
    Loads contacts, personas, hierarchy links, social intelligence, and signals for an account.
    """
    logger.info(f"Loading executive contacts & intelligence for: {account.name}")
    
    lobs = db.query(AccountLob).filter(AccountLob.account_id == account.id).all()
    default_lob_id = lobs[0].id if lobs else None

    # 1. Upsert Contacts & Personas
    contact_records = {}
    for p in people_list:
        email = p.get("email")
        full_name = p.get("full_name")

        contact = db.query(Contact).filter(
            Contact.account_id == account.id,
            Contact.full_name == full_name
        ).first()

        persona_data = personas_map.get(full_name, {})
        score_info = p.get("score_breakdown", {})
        total_score = score_info.get("total_score", 80)
        lead_status = score_info.get("tier", "Hot" if total_score >= 80 else "Warm")

        if not contact:
            contact = Contact(
                account_id=account.id,
                lob_id=default_lob_id,
                first_name=p.get("first_name"),
                last_name=p.get("last_name"),
                full_name=full_name,
                title=p.get("title"),
                current_title=p.get("title"),
                seniority_tier=p.get("seniority_tier", "CXO"),
                sub_lob_name=p.get("department", "Management"),
                location=p.get("location", "New York, USA"),
                email=email,
                email_confidence=p.get("email_confidence", "verified"),
                phone=p.get("phone", "+1 212-555-0194"),
                tenure=p.get("tenure_formatted", "3 yrs"),
                tenure_months=p.get("tenure_months", 36),
                decision_authority=p.get("decision_authority", "final"),
                budget_authority=p.get("budget_authority", "full"),
                buyer_roles=p.get("buyer_roles", ["Key Decision Maker"]),
                summary_bio=p.get("summary_bio"),
                linkedin_url=p.get("linkedin_url"),
                lead_score=total_score,
                lead_status=lead_status,
                raw_data={
                    "score_breakdown": score_info,
                    "tech_stack": persona_data.get("tech_stack", []),
                    "operational_pain_points": persona_data.get("operational_pain_points", []),
                    "target_kpis": persona_data.get("target_kpis", []),
                    "prior_company_experience": persona_data.get("prior_company_experience"),
                    "education_summary": persona_data.get("education_summary")
                }
            )
            db.add(contact)
            db.flush()
        else:
            contact.title = p.get("title", contact.title)
            contact.lead_score = total_score
            contact.lead_status = lead_status
            contact.phone = p.get("phone", contact.phone)
            contact.summary_bio = p.get("summary_bio", contact.summary_bio)
            contact.raw_data = {
                "score_breakdown": score_info,
                "tech_stack": persona_data.get("tech_stack", []),
                "operational_pain_points": persona_data.get("operational_pain_points", []),
                "target_kpis": persona_data.get("target_kpis", []),
                "prior_company_experience": persona_data.get("prior_company_experience"),
                "education_summary": persona_data.get("education_summary")
            }

        contact_records[full_name] = contact

        # Upsert Persona
        persona = db.query(Persona).filter(Persona.contact_id == contact.id).first()
        if not persona:
            persona = Persona(
                contact_id=contact.id,
                demographics=persona_data,
                professional_behavior=persona_data,
                personal_touch=persona_data,
                experience=persona_data.get("career_experience_timeline", []),
                tech_stack=persona_data.get("tech_stack", []),
                operational_pain_points=persona_data.get("operational_pain_points", []),
                kpis=persona_data.get("target_kpis", []),
                score_breakdown=score_info
            )
            db.add(persona)
        else:
            persona.demographics = persona_data
            persona.professional_behavior = persona_data
            persona.personal_touch = persona_data
            persona.experience = persona_data.get("career_experience_timeline", [])
            persona.tech_stack = persona_data.get("tech_stack", [])
            persona.operational_pain_points = persona_data.get("operational_pain_points", [])
            persona.kpis = persona_data.get("target_kpis", [])
            persona.score_breakdown = score_info

    db.flush()

    # 2. Upsert Org Hierarchy
    for h in hierarchy_list:
        full_name = h["full_name"]
        contact = contact_records.get(full_name)
        if contact:
            org_node = db.query(OrgHierarchy).filter(OrgHierarchy.contact_id == contact.id).first()
            if not org_node:
                org_node = OrgHierarchy(
                    contact_id=contact.id,
                    level=h.get("level", 2),
                    hierarchy_level=h.get("level", 2),
                    reports_to_name=h.get("reports_to_name"),
                    reports_to_title=h.get("reports_to_title"),
                    reports_to_path=h.get("reports_to_path", "001.002"),
                    influence_score=h.get("influence_score", 80)
                )
                db.add(org_node)
            else:
                org_node.level = h.get("level", org_node.level)
                org_node.reports_to_name = h.get("reports_to_name", org_node.reports_to_name)

    db.flush()

    # 3. Upsert Social Intelligence
    for post in social_posts:
        author = post.get("author_name")
        headline = post.get("headline")
        existing_post = db.query(SocialIntelligence).filter(
            SocialIntelligence.account_id == account.id,
            SocialIntelligence.headline == headline
        ).first()

        matching_contact = contact_records.get(author)
        if not existing_post:
            db.add(SocialIntelligence(
                account_id=account.id,
                contact_id=matching_contact.id if matching_contact else None,
                platform=post.get("platform", "LINKEDIN"),
                author_name=author,
                author_title=post.get("author_title"),
                headline=headline,
                content=post.get("content", ""),
                topic_tags=post.get("topic_tags", []),
                engagement_formatted=post.get("engagement_formatted"),
                post_date_formatted=post.get("post_date_formatted"),
                sentiment=post.get("sentiment_label", "POSITIVE"),
                sentiment_score=post.get("sentiment_score", 0.95)
            ))

    db.flush()

    # 4. Upsert Buying Signals
    for sig in signals_list:
        title = sig.get("title")
        existing_sig = db.query(SalesTriggerSignal).filter(
            SalesTriggerSignal.account_id == account.id,
            SalesTriggerSignal.title == title
        ).first()

        if not existing_sig:
            db.add(SalesTriggerSignal(
                account_id=account.id,
                signal_type=sig.get("signal_type", "STRATEGIC_INITIATIVE"),
                category=sig.get("event_category", "Modernization"),
                title=title,
                summary=sig.get("summary", ""),
                urgency_score=sig.get("urgency_score", 85),
                priority=sig.get("priority", "HIGH"),
                status=sig.get("status", "OPEN"),
                recommended_action=sig.get("recommended_action")
            ))

    db.flush()
    logger.info(f"Loaded {len(contact_records)} contacts, hierarchy, social & signals successfully.")
