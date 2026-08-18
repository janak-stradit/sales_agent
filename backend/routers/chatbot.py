"""API Router for AI Chatbot Assistant."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.contact import Contact
from backend.models.account import Account
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.social_intelligence import SocialIntelligence
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/query")
def query_chatbot(req: ChatRequest, db: Session = Depends(get_db)):
    query = (req.query or "").strip()
    if not query:
        return {
            "response": "Hello! I am your Sales AI Assistant. Ask me anything about target accounts, executive leads, seniority tiers, buying signals, or team roles.",
            "results": {"contacts": [], "accounts": [], "signals": []}
        }
    
    # Database search
    words = [w.strip() for w in query.split() if len(w.strip()) > 1]
    
    if words:
        # Contacts: Match if for every word, at least one field matches
        contact_conditions = []
        for w in words:
            pat = f"%{w}%"
            contact_conditions.append(or_(
                Contact.full_name.ilike(pat),
                Contact.title.ilike(pat),
                Contact.seniority_tier.ilike(pat),
                Contact.account.has(Account.name.ilike(pat))
            ))
        matched_contacts = db.query(Contact).filter(and_(*contact_conditions)).limit(5).all()
        
        # Accounts: Match if for every word, at least one field matches
        acc_conditions = []
        for w in words:
            pat = f"%{w}%"
            acc_conditions.append(or_(
                Account.name.ilike(pat),
                Account.domain.ilike(pat),
                Account.industry.ilike(pat)
            ))
        matched_accounts = db.query(Account).filter(and_(*acc_conditions)).limit(5).all()
        
        # Signals: Match if for every word, at least one field matches
        sig_conditions = []
        for w in words:
            pat = f"%{w}%"
            sig_conditions.append(or_(
                SalesTriggerSignal.title.ilike(pat),
                SalesTriggerSignal.summary.ilike(pat),
                SalesTriggerSignal.category.ilike(pat),
                SalesTriggerSignal.account.has(Account.name.ilike(pat))
            ))
        matched_signals = db.query(SalesTriggerSignal).filter(and_(*sig_conditions)).limit(5).all()

        # Social Posts: Match if for every word, at least one field matches
        social_conditions = []
        for w in words:
            pat = f"%{w}%"
            social_conditions.append(or_(
                SocialIntelligence.author_name.ilike(pat),
                SocialIntelligence.content.ilike(pat),
                SocialIntelligence.platform.ilike(pat),
                SocialIntelligence.account.has(Account.name.ilike(pat))
            ))
        matched_social = db.query(SocialIntelligence).filter(and_(*social_conditions)).limit(5).all()
    else:
        # Fallback to single pattern matching
        pat = f"%{query}%"
        matched_contacts = db.query(Contact).filter(or_(
            Contact.full_name.ilike(pat),
            Contact.title.ilike(pat),
            Contact.seniority_tier.ilike(pat),
            Contact.account.has(Account.name.ilike(pat))
        )).limit(5).all()
        
        matched_accounts = db.query(Account).filter(or_(
            Account.name.ilike(pat),
            Account.domain.ilike(pat),
            Account.industry.ilike(pat)
        )).limit(5).all()
        
        matched_signals = db.query(SalesTriggerSignal).filter(or_(
            SalesTriggerSignal.title.ilike(pat),
            SalesTriggerSignal.summary.ilike(pat),
            SalesTriggerSignal.category.ilike(pat),
            SalesTriggerSignal.account.has(Account.name.ilike(pat))
        )).limit(5).all()

        matched_social = db.query(SocialIntelligence).filter(or_(
            SocialIntelligence.author_name.ilike(pat),
            SocialIntelligence.content.ilike(pat),
            SocialIntelligence.platform.ilike(pat),
            SocialIntelligence.account.has(Account.name.ilike(pat))
        )).limit(5).all()
    
    # Construct a natural language response
    response_parts = []
    
    if matched_contacts:
        response_parts.append(f"### matching contacts ({len(matched_contacts)})")
        for c in matched_contacts:
            acc_name = c.account.name if c.account else "Unknown Account"
            response_parts.append(f"- **{c.full_name}** - {c.title} @ *{acc_name}* (Seniority: `{c.seniority_tier or 'Unknown'}`, Lead Score: `{c.lead_score}`)  \n  📧 {c.email or 'No email'}")
    
    if matched_accounts:
        response_parts.append(f"### matching target accounts ({len(matched_accounts)})")
        for a in matched_accounts:
            response_parts.append(f"- **{a.name}** ({a.domain or 'No Domain'}) - {a.industry or 'Technology'} | Revenue: `{a.annual_revenue_printed or 'N/A'}`")
            
    if matched_signals:
        response_parts.append(f"### buying signals ({len(matched_signals)})")
        for s in matched_signals:
            response_parts.append(f"- **{s.title or s.signal_type}** ({s.priority} priority) - *{s.summary or ''}*")

    if matched_social:
        response_parts.append(f"### matching social media posts ({len(matched_social)})")
        for s in matched_social:
            platform_icon = "💼" if s.platform == "LINKEDIN" else "🐦"
            response_parts.append(f"- **{s.author_name}** ({s.author_title or 'Executive'}) on {platform_icon} *{s.platform}*:\n  \"{s.content[:150]}...\"  \n  Sentiment: `{s.sentiment}` | Engagement: `{s.engagement_formatted or 'N/A'}`")
            
    if not response_parts:
        response_text = f"I couldn't find any direct matches for **\"{query}\"** in our records. Try searching for:\n- Company name (e.g. `BNY`)\n- Seniority level (e.g. `CXO` or `VP`)\n- Role keywords (e.g. `Director` or `Lead`)\n- Contact name (e.g. `Emily` or `Vince`)"
    else:
        response_text = "Here is what I found in our database:\n\n" + "\n\n".join(response_parts)
        
    # Serialize results to return as structured data
    contacts_data = [{
        "id": str(c.id),
        "full_name": c.full_name,
        "title": c.title,
        "seniority_tier": c.seniority_tier,
        "account_name": c.account.name if c.account else "Unknown",
        "lead_score": c.lead_score,
        "email": c.email
    } for c in matched_contacts]
    
    accounts_data = [{
        "id": str(a.id),
        "name": a.name,
        "domain": a.domain,
        "industry": a.industry,
        "employee_count": a.employee_count
    } for a in matched_accounts]
    
    signals_data = [{
        "id": str(s.id),
        "title": s.title or s.signal_type,
        "priority": s.priority,
        "recommended_action": s.recommended_action
    } for s in matched_signals]

    social_data = [{
        "id": str(s.id),
        "author_name": s.author_name,
        "author_title": s.author_title,
        "platform": s.platform,
        "content": s.content,
        "sentiment": s.sentiment,
        "engagement": s.engagement_formatted
    } for s in matched_social]
    
    return {
        "response": response_text,
        "results": {
            "contacts": contacts_data,
            "accounts": accounts_data,
            "signals": signals_data,
            "social": social_data
        }
    }
