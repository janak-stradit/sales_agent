"""
Sales AI Chatbot Service Engine with Hybrid ChromaDB Vector Search.

Processes conversational sales team queries and structured searches across:
  - ChromaDB Vector Embeddings (Semantic similarity on unconstrained queries & synonyms)
  - People / Executives (names, titles, seniority, roles, email, phone)
  - Organizations & Accounts (name, domain, ticker, revenue, tech stack)
  - Lines of Business & Budgets (divisions, heads, platforms)
  - Personas & Social Insights (communication styles, scraped posts, icebreakers)
  - Sales Trigger Signals (buying triggers, urgency scores, recommended outreach)
"""

import re
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.schemas.chatbot_schemas import (
    ChatbotQueryRequest,
    ChatbotQueryResponse,
    ChatbotPersonResult,
    ChatbotOrganizationResult,
    ChatbotLOBResult,
    ChatbotSignalResult,
    PeopleSearchFilterRequest,
    PeopleSearchFilterResponse,
    ChatbotStarterSuggestion,
    ChatbotSuggestionsResponse,
)
from backend.services.vector_store_service import semantic_search

logger = logging.getLogger("chatbot.service")


# ── Helper: Map Contact Model to Chatbot Person Result ──────
def _map_contact_to_person_result(c: Contact, db: Session) -> ChatbotPersonResult:
    persona = db.query(Persona).filter(Persona.contact_id == c.id).first()
    comm_style = persona.communication_style if persona else None
    personal_touch_data = persona.personal_touch if persona and isinstance(persona.personal_touch, dict) else {}

    is_decision = bool(c.decision_authority or c.budget_authority or (c.buyer_roles and len(c.buyer_roles) > 0))

    talking_points = []
    if c.title:
        talking_points.append(f"Target Role: {c.title}")
    if c.decision_authority:
        talking_points.append(f"Decision Authority: {c.decision_authority}")
    if c.budget_authority:
        talking_points.append(f"Budget Scope: {c.budget_authority}")
    if c.sub_lob_name:
        talking_points.append(f"Division Focus: {c.sub_lob_name}")
    if comm_style:
        talking_points.append(f"Communication Style: {comm_style}")

    return ChatbotPersonResult(
        id=c.id,
        full_name=c.full_name or f"{c.first_name or ''} {c.last_name or ''}".strip() or "Executive Contact",
        first_name=c.first_name,
        last_name=c.last_name,
        title=c.title or c.current_title or "Executive",
        seniority=c.seniority,
        seniority_tier=c.seniority_tier or "Executive",
        role=c.target_persona_type or c.leadership_type or c.seniority_tier,
        organization=c.account.name if c.account else (c.organization or "Enterprise Account"),
        account_id=c.account_id,
        sub_lob_name=c.sub_lob_name,
        email=c.email or c.contact_email,
        phone=c.phone,
        location=c.location or c.geography,
        linkedin_url=c.linkedin_url,
        lead_score=c.lead_score or 75,
        lead_status=c.lead_status or "Hot",
        is_decision_maker=is_decision,
        decision_authority=c.decision_authority,
        budget_authority=c.budget_authority,
        reports_to_name=c.reports_to_name,
        summary_bio=c.summary_bio,
        responsibilities=c.responsibilities,
        communication_style=comm_style,
        personal_touch=personal_touch_data,
        key_talking_points=talking_points
    )


# ── Natural Language Intent & Entity Extraction ─────────────
def _extract_intent_and_entities(query: str) -> Dict[str, Any]:
    q_lower = query.lower().strip()

    entities = {
        "intent": "general_intelligence",
        "roles": [],
        "names": [],
        "organizations": [],
        "keywords": [],
        "wants_decision_makers": False,
        "wants_signals": False,
        "wants_org_overview": False,
        "wants_tech_stack": False,
    }

    # Detect specific executive names
    known_names = ["emily", "portney", "robin", "vince", "bridget", "engle", "ranjit", "samra", "hany", "farag", "roman", "regelman"]
    for n in known_names:
        if re.search(rf"\b{n}\b", q_lower):
            entities["names"].append(n)

    # Detect designation & role keywords
    role_patterns = [
        (r"\bceo\b|\bchief executive\b|\bpresident\b", "CEO"),
        (r"\bcto\b|\bchief technology officer\b|\bctpo\b|\bchief product\b", "CTPO / CTO"),
        (r"\bcio\b|\bchief information\b|\bhead of technology\b", "CIO"),
        (r"\bmd\b|\bmanaging director\b", "Managing Director"),
        (r"\bvp\b|\bvice president\b", "Vice President"),
        (r"\bdirector\b", "Director"),
        (r"\bhead of asset servicing\b|\basset servicing\b", "Asset Servicing"),
        (r"\bdecision maker[s]?\b|\bbuyer[s]?\b", "Decision Maker"),
        (r"\btech lead\b|\blead engineer\b|\barchitect\b", "Tech Lead"),
    ]

    for pat, label in role_patterns:
        if re.search(pat, q_lower):
            entities["roles"].append(label)

    if re.search(r"\bdecision maker[s]?\b|\bbuyer[s]?\b|\bauthority\b", q_lower):
        entities["wants_decision_makers"] = True

    if re.search(r"\bsignal[s]?\b|\btrigger[s]?\b|\bbuying\b|\brfp[s]?\b|\bopportunit[y|ies]\b", q_lower):
        entities["wants_signals"] = True

    if re.search(r"\b360\b|\boverview\b|\bfirmographic[s]?\b|\bcompany profile\b", q_lower):
        entities["wants_org_overview"] = True

    if re.search(r"\btech[nology]? stack\b|\bplatform[s]?\b|\btools\b|\bsoftware\b", q_lower):
        entities["wants_tech_stack"] = True

    # Detect common organization names
    org_patterns = [
        (r"\bbny\b|\bbk\b|\bbank of new york\b|\bmellon\b", "BNY"),
        (r"\bgoldman\b|\bgs\b", "Goldman Sachs"),
        (r"\bjpmorgan\b|\bjpm\b|\bchase\b", "JPMorgan Chase"),
        (r"\bpershing\b", "Pershing"),
    ]
    for pat, label in org_patterns:
        if re.search(pat, q_lower):
            entities["organizations"].append(label)

    # Classify main intent
    if entities["wants_signals"] and not entities["names"]:
        entities["intent"] = "signal_search"
    elif (entities["wants_org_overview"] or entities["wants_tech_stack"]) and not entities["names"] and not entities["roles"]:
        entities["intent"] = "org_lookup"
    elif entities["roles"] or entities["names"] or re.search(r"\bwho is\b|\bfind\b|\bshow\b|\bpeople\b|\bperson\b|\bcontact\b|\bexecutive\b|\blead\b", q_lower):
        entities["intent"] = "role_search" if entities["roles"] else "person_lookup"
    elif entities["organizations"]:
        entities["intent"] = "org_lookup"

    return entities


# ── Core Conversational Query Processing Engine (Hybrid Search) ──
def process_chatbot_query(db: Session, request: ChatbotQueryRequest) -> ChatbotQueryResponse:
    query = request.message.strip()
    extracted = _extract_intent_and_entities(query)
    pattern = f"%{query}%"

    stop_words = {"who", "is", "the", "at", "in", "of", "and", "for", "with", "a", "an", "give", "me", "all", "what", "are"}
    raw_words = [w for w in re.split(r"\W+", query) if len(w) > 1]
    words = [w for w in raw_words if w.lower() not in stop_words]

    # ── 1. Query ChromaDB for Semantic Vector Matches ──
    semantic_matches = semantic_search(query, n_results=10)
    vector_matched_contact_ids = set()
    vector_matched_account_ids = set()
    vector_matched_signal_ids = set()
    vector_matched_lob_ids = set()

    for m in semantic_matches:
        meta = m.get("metadata", {})
        entity_type = meta.get("type")
        entity_id = meta.get("entity_id")
        if entity_id:
            try:
                uid = uuid.UUID(entity_id)
                if entity_type == "contact":
                    vector_matched_contact_ids.add(uid)
                elif entity_type == "account":
                    vector_matched_account_ids.add(uid)
                elif entity_type == "signal":
                    vector_matched_signal_ids.add(uid)
                elif entity_type == "lob":
                    vector_matched_lob_ids.add(uid)
            except Exception:
                pass

    # ── 2. Hybrid Contact Scoring (Vector Embeddings + SQL Keywords) ──
    all_contacts = db.query(Contact).all()
    scored_contacts = []
    q_lower = query.lower()

    for c in all_contacts:
        score = 0
        c_full = (c.full_name or "").lower()
        c_title = (c.title or "").lower()
        c_sub = (c.sub_lob_name or "").lower()
        c_seniority = (c.seniority_tier or "").lower()

        # Boost from ChromaDB vector semantic similarity
        if c.id in vector_matched_contact_ids:
            score += 70

        # Exact name match
        for n in extracted["names"]:
            if n in c_full:
                score += 120

        # Exact title / role match
        if "ceo" in q_lower and ("ceo" in c_title or "chief executive" in c_title):
            score += 80
        if "head of asset servicing" in q_lower and ("asset servicing" in c_sub or "asset servicing" in c_title):
            score += 80
        if "asset servicing" in q_lower and "asset servicing" in c_sub:
            score += 40
        if "cio" in q_lower and ("cio" in c_title or "chief information" in c_title or "head of technology" in c_title):
            score += 80
        if "ctpo" in q_lower and ("ctpo" in c_title or "chief technology" in c_title):
            score += 80
        if "vp" in q_lower or "vice president" in q_lower:
            if "vp" in c_seniority or "vice president" in c_title or "vp" in c_title.lower():
                score += 60

        # Decision maker flag
        if extracted["wants_decision_makers"]:
            if c.decision_authority or c.budget_authority:
                score += 30

        # Word overlap
        for w in words:
            w_l = w.lower()
            if w_l in c_full:
                score += 25
            if w_l in c_title:
                score += 20
            if w_l in c_sub:
                score += 15

        # Base score on lead score
        score += (c.lead_score or 0) * 0.1

        if score > 5:
            scored_contacts.append((score, c))

    scored_contacts.sort(key=lambda x: x[0], reverse=True)
    matched_contacts = [c for _, c in scored_contacts[:request.limit]]

    if not matched_contacts:
        matched_contacts = db.query(Contact).order_by(desc(Contact.lead_score)).limit(request.limit).all()

    people_results = [_map_contact_to_person_result(c, db) for c in matched_contacts]

    # ── 3. Organizations Query (Vector + SQL) ──────────
    acc_filters = [Account.name.ilike(pattern), Account.publicly_traded_symbol.ilike(pattern), Account.industry.ilike(pattern)]
    for org in extracted["organizations"]:
        acc_filters.append(Account.name.ilike(f"%{org}%"))
    if vector_matched_account_ids:
        acc_filters.append(Account.id.in_(list(vector_matched_account_ids)))

    matched_accounts = db.query(Account).filter(or_(*acc_filters)).limit(5).all()
    if not matched_accounts:
        matched_accounts = db.query(Account).limit(3).all()

    org_results = []
    for a in matched_accounts:
        exec_count = db.query(Contact).filter(Contact.account_id == a.id).count()
        lob_count = db.query(AccountLob).filter(AccountLob.account_id == a.id).count()
        tech_list = a.tech_stack if isinstance(a.tech_stack, list) else []
        pain_list = a.pain_points if isinstance(a.pain_points, list) else []

        org_results.append(ChatbotOrganizationResult(
            id=a.id,
            name=a.name,
            domain=a.domain or "bny.com",
            ticker=a.publicly_traded_symbol,
            exchange=a.publicly_traded_exchange,
            industry=a.industry,
            employee_count=a.employee_count,
            annual_revenue=a.annual_revenue_printed or "$20.0B",
            market_cap=a.market_cap or "$92.7B",
            headquarters=a.headquarters,
            tech_stack=tech_list,
            pain_points=pain_list,
            total_executives=exec_count,
            total_lobs=lob_count
        ))

    # ── 4. Lines of Business (LOBs) ────────────────────
    lob_filters = [
        AccountLob.name.ilike(pattern),
        AccountLob.business_head.ilike(pattern),
        AccountLob.tech_leader.ilike(pattern),
        AccountLob.tech_leader_title.ilike(pattern),
        AccountLob.intelligence_notes.ilike(pattern)
    ]
    for w in words:
        lob_filters.append(AccountLob.name.ilike(f"%{w}%"))
    if vector_matched_lob_ids:
        lob_filters.append(AccountLob.id.in_(list(vector_matched_lob_ids)))

    matched_lobs = db.query(AccountLob).filter(or_(*lob_filters)).limit(5).all()
    if not matched_lobs:
        matched_lobs = db.query(AccountLob).limit(3).all()

    lob_results = []
    for l in matched_lobs:
        plat_str = ", ".join(l.key_platforms) if isinstance(l.key_platforms, list) else str(l.key_platforms or "")
        lob_results.append(ChatbotLOBResult(
            id=l.id,
            name=l.name,
            account_name=l.account.name if l.account else "Target Account",
            node_type=l.node_type,
            business_head=l.business_head,
            tech_leader=l.tech_leader,
            tech_leader_title=l.tech_leader_title,
            confidence_level=l.confidence_level or "High",
            key_platforms=plat_str,
            intelligence_notes=l.intelligence_notes
        ))

    # ── 5. Sales Trigger Signals (Vector + SQL) ────────
    signal_filters = [SalesTriggerSignal.title.ilike(pattern), SalesTriggerSignal.summary.ilike(pattern), SalesTriggerSignal.category.ilike(pattern)]
    for w in words:
        signal_filters.append(SalesTriggerSignal.title.ilike(f"%{w}%"))
    if vector_matched_signal_ids:
        signal_filters.append(SalesTriggerSignal.id.in_(list(vector_matched_signal_ids)))

    matched_signals = db.query(SalesTriggerSignal).filter(or_(*signal_filters)).order_by(desc(SalesTriggerSignal.urgency_score)).limit(5).all()
    if not matched_signals:
        matched_signals = db.query(SalesTriggerSignal).order_by(desc(SalesTriggerSignal.urgency_score)).limit(5).all()

    signal_results = [
        ChatbotSignalResult(
            id=s.id,
            title=s.title,
            organization=s.account.name if s.account else "Target Account",
            signal_type=s.signal_type,
            category=s.category,
            urgency_score=s.urgency_score or 85,
            priority=s.priority or "HIGH",
            summary=s.summary,
            recommended_action=s.recommended_action,
            source_name=s.source_name
        )
        for s in matched_signals
    ]

    # ── 6. Synthesize Natural Language Conversational Reply ──
    reply_lines = []
    suggested_followups = []

    if extracted["intent"] == "signal_search" and signal_results:
        reply_lines.append(f"Here are the active **buying trigger signals** for {signal_results[0].organization}:")
        for s in signal_results[:3]:
            reply_lines.append(f"• 🔥 **[{s.priority}] {s.title}** (Urgency: **{s.urgency_score}/100**)")
            if s.summary:
                reply_lines.append(f"  📝 {s.summary}")
            if s.recommended_action:
                reply_lines.append(f"  👉 Recommended Outreach: {s.recommended_action}")
        suggested_followups.append("Which executive leads should we contact for this signal?")
        suggested_followups.append("Show all decision makers at BNY")

    elif extracted["intent"] == "org_lookup" and org_results:
        top_org = org_results[0]
        reply_lines.append(f"Here is the organization 360 overview for **{top_org.name}** ({top_org.ticker or 'N/A'}):")
        reply_lines.append(f"• **Industry**: {top_org.industry} | **Revenue**: {top_org.annual_revenue} | **Employees**: {top_org.employee_count:,}" if top_org.employee_count else f"• **Industry**: {top_org.industry} | **Revenue**: {top_org.annual_revenue}")
        reply_lines.append(f"• **Headquarters**: {top_org.headquarters} | **Market Cap**: {top_org.market_cap or '$92.7B'}")
        if top_org.tech_stack:
            reply_lines.append(f"• **Core Technographics**: {', '.join(top_org.tech_stack[:8])}")
        if top_org.pain_points:
            reply_lines.append(f"• **Strategic Pain Points**: {'; '.join(top_org.pain_points[:3])}")
        suggested_followups.append(f"Who are the top decision makers at {top_org.name}?")
        suggested_followups.append(f"What are the active buying triggers for {top_org.name}?")

    elif people_results:
        top_p = people_results[0]
        reply_lines.append(f"I found **{len(people_results)} executive(s)** matching your query:")
        for p in people_results[:3]:
            reply_lines.append(f"• **{p.full_name}** — *{p.title}* at **{p.organization}** (Lead Score: **{p.lead_score}/100**, {p.seniority_tier or 'Executive'})")
            if p.email:
                reply_lines.append(f"  ✉️ Email: `{p.email}` | 📞 Phone: `{p.phone or 'Direct route via switchboard'}`")
            if p.communication_style:
                reply_lines.append(f"  💡 Comm Style: {p.communication_style}")

        if len(people_results) > 3:
            reply_lines.append(f"...and {len(people_results) - 3} additional executive contact(s) available in the dossier list below.")

        suggested_followups.append(f"Show communication style and scraped posts for {top_p.full_name}")
        suggested_followups.append(f"Who does {top_p.full_name} report to?")
        suggested_followups.append(f"What are the active buying signals for {top_p.organization}?")

    full_reply = "\n".join(reply_lines)

    return ChatbotQueryResponse(
        query=query,
        reply=full_reply,
        intent_detected=extracted["intent"],
        matched_people_count=len(people_results),
        matched_organizations_count=len(org_results),
        matched_signals_count=len(signal_results),
        people=people_results,
        organizations=org_results,
        lobs=lob_results,
        signals=signal_results,
        suggested_followups=suggested_followups
    )


# ── Structured Multi-Attribute People Search ────────────────
def search_people_structured(db: Session, filters: PeopleSearchFilterRequest) -> PeopleSearchFilterResponse:
    query = db.query(Contact)

    if filters.person_name:
        p_pat = f"%{filters.person_name}%"
        query = query.filter(or_(
            Contact.full_name.ilike(p_pat),
            Contact.first_name.ilike(p_pat),
            Contact.last_name.ilike(p_pat)
        ))

    if filters.organization:
        o_pat = f"%{filters.organization}%"
        query = query.join(Account, Contact.account_id == Account.id).filter(or_(
            Account.name.ilike(o_pat),
            Account.publicly_traded_symbol.ilike(o_pat),
            Contact.organization.ilike(o_pat)
        ))

    if filters.designation:
        d_pat = f"%{filters.designation}%"
        query = query.filter(or_(
            Contact.title.ilike(d_pat),
            Contact.current_title.ilike(d_pat)
        ))

    if filters.role:
        r_pat = f"%{filters.role}%"
        query = query.filter(or_(
            Contact.seniority_tier.ilike(r_pat),
            Contact.seniority.ilike(r_pat),
            Contact.target_persona_type.ilike(r_pat),
            Contact.leadership_type.ilike(r_pat)
        ))

    if filters.department_or_lob:
        dept_pat = f"%{filters.department_or_lob}%"
        query = query.filter(Contact.sub_lob_name.ilike(dept_pat))

    if filters.min_lead_score is not None:
        query = query.filter(Contact.lead_score >= filters.min_lead_score)

    if filters.is_decision_maker is not None:
        if filters.is_decision_maker:
            query = query.filter(or_(Contact.decision_authority.isnot(None), Contact.budget_authority.isnot(None)))
        else:
            query = query.filter(and_(Contact.decision_authority.is_(None), Contact.budget_authority.is_(None)))

    total = query.count()
    items = query.order_by(desc(Contact.lead_score)).offset(filters.offset).limit(filters.limit).all()

    mapped_items = [_map_contact_to_person_result(c, db) for c in items]

    return PeopleSearchFilterResponse(
        total_found=total,
        offset=filters.offset,
        limit=filters.limit,
        items=mapped_items
    )


# ── Quick Starter Suggestions for Sales Reps ────────────────
def get_chatbot_starter_prompts() -> ChatbotSuggestionsResponse:
    return ChatbotSuggestionsResponse(suggestions=[
        ChatbotStarterSuggestion(
            category="Executive Search",
            title="CEO & C-Suite Leadership",
            prompt="Who is the CEO and President of BNY?",
            description="Find executive leadership, direct reporting lines, and tenure."
        ),
        ChatbotStarterSuggestion(
            category="Decision Makers",
            title="High-Score Decision Makers",
            prompt="Show all confirmed decision makers with lead score above 85 at BNY",
            description="Filter hottest sales opportunities and verified buyer roles."
        ),
        ChatbotStarterSuggestion(
            category="Role & Designation",
            title="VPs & Managing Directors in Asset Servicing",
            prompt="Find all VPs and Managing Directors in Asset Servicing at BNY",
            description="Locate mid-to-senior leadership by division and designation."
        ),
        ChatbotStarterSuggestion(
            category="Persona & Social Intelligence",
            title="Emily Portney's Dossier & Posts",
            prompt="Show me intelligence dossier, communication style, and recent posts for Emily Portney",
            description="Get 100% scraped personal touch data, career timeline, and talking points."
        ),
        ChatbotStarterSuggestion(
            category="Buying Triggers",
            title="Active Sales Signals & Tech RFPs",
            prompt="What are the highest urgency buying signals and tech initiatives for BNY?",
            description="View real-time intent signals, budget expansions, and pain points."
        ),
        ChatbotStarterSuggestion(
            category="Organization 360",
            title="Company Overview & Tech Stack",
            prompt="Give me a 360 overview of BNY Mellon including revenue, employees, and tech stack",
            description="Complete firmographics, legal subsidiaries, and technographics."
        )
    ])
