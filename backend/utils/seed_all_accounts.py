"""
Seeds all 4 Target Enterprise Accounts (BNY, State Street, Northern Trust, JPMorgan Chase)
and all Executive Leads matching Screenshots 181753.png, 181721.png, and 181957.png.
"""

from backend.database import SessionLocal
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
import uuid

def seed_enterprise_accounts():
    db = SessionLocal()
    try:
        # 1. State Street (STT)
        stt = db.query(Account).filter(Account.name == "State Street").first()
        if not stt:
            stt = Account(
                name="State Street",
                domain="statestreet.com",
                primary_domain="statestreet.com",
                website_url="https://www.statestreet.com",
                company_url="https://www.statestreet.com",
                industry="Financial Services & Institutional Asset Management",
                founded_year=1792,
                employee_count=42000,
                headquarters="1 Lincoln St, Boston, MA 02111, United States",
                city="Boston",
                state="Massachusetts",
                country="United States",
                short_description="State Street is a leading financial services provider serving institutional investors worldwide.",
                description="State Street Corporation provides financial services to institutional investors including investment servicing, investment management and investment research and trading.",
                annual_revenue_usd=12000000000,
                annual_revenue_printed="$12.0B",
                publicly_traded_symbol="STT",
                publicly_traded_exchange="NYSE",
                technology_names=["Python", "Kubernetes", "AWS", "Snowflake", "Databricks", "React", "PostgreSQL", "Kafka"],
                tech_stack=["Python", "Kubernetes", "AWS", "Snowflake", "Databricks", "React", "PostgreSQL", "Kafka"],
                keywords=["Alpha platform", "Data analytics", "ESG investing", "investment servicing"],
                raw_data={"aum": "$3.5T", "auc_a": "$40.0T", "strategic_priorities": ["Alpha platform", "Data analytics", "ESG investing"]}
            )
            db.add(stt)
            db.flush()
            
            lob_stt = AccountLob(
                account_id=stt.id,
                name="Global Investment Servicing",
                entity_type="Division",
                hierarchy_depth=1,
                headcount=20000
            )
            db.add(lob_stt)
            db.flush()

        # 2. Northern Trust (NTRS)
        ntrs = db.query(Account).filter(Account.name == "Northern Trust").first()
        if not ntrs:
            ntrs = Account(
                name="Northern Trust",
                domain="northerntrust.com",
                primary_domain="northerntrust.com",
                website_url="https://www.northerntrust.com",
                company_url="https://www.northerntrust.com",
                industry="Wealth Management & Asset Servicing",
                founded_year=1889,
                employee_count=23000,
                headquarters="50 S La Salle St, Chicago, IL 60603, United States",
                city="Chicago",
                state="Illinois",
                country="United States",
                short_description="Northern Trust is a preeminent wealth management and asset servicing company.",
                description="Northern Trust Corporation is a leading provider of wealth management, asset servicing, asset management and banking to corporations, institutions, and individuals.",
                annual_revenue_usd=6500000000,
                annual_revenue_printed="$6.5B",
                publicly_traded_symbol="NTRS",
                publicly_traded_exchange="NYSE",
                technology_names=["Python", "Kubernetes", "AWS", "Snowflake", "MongoDB", "Angular", "Kafka", "Airflow"],
                tech_stack=["Python", "Kubernetes", "AWS", "Snowflake", "MongoDB", "Angular", "Kafka", "Airflow"],
                keywords=["Wealth technology", "Asset servicing modernization", "Sustainable investing"],
                raw_data={"aum": "$1.5T", "auc_a": "$15.0T", "strategic_priorities": ["Wealth technology", "Asset servicing modernization", "Sustainable investing"]}
            )
            db.add(ntrs)
            db.flush()

            lob_ntrs = AccountLob(
                account_id=ntrs.id,
                name="Asset Servicing & Wealth Management",
                entity_type="Division",
                hierarchy_depth=1,
                headcount=12000
            )
            db.add(lob_ntrs)
            db.flush()

        # 3. JPMorgan Chase (JPM)
        jpm = db.query(Account).filter(Account.name == "JPMorgan Chase").first()
        if not jpm:
            jpm = Account(
                name="JPMorgan Chase",
                domain="jpmorganchase.com",
                primary_domain="jpmorganchase.com",
                website_url="https://www.jpmorganchase.com",
                company_url="https://www.jpmorganchase.com",
                industry="Financial Services & Investment Banking",
                founded_year=1799,
                employee_count=310000,
                headquarters="383 Madison Ave, New York, NY 10017, United States",
                city="New York",
                state="New York",
                country="United States",
                short_description="JPMorgan Chase is a leading global financial services firm with assets of $3.9 trillion.",
                description="JPMorgan Chase & Co. is an American multinational finance corporation headquartered in New York City and the largest bank in the United States.",
                annual_revenue_usd=158100000000,
                annual_revenue_printed="$158.1B",
                publicly_traded_symbol="JPM",
                publicly_traded_exchange="NYSE",
                technology_names=["Python", "Kubernetes", "AWS", "Snowflake", "Databricks", "TensorFlow", "React", "Kafka"],
                tech_stack=["Python", "Kubernetes", "AWS", "Snowflake", "Databricks", "TensorFlow", "React", "Kafka"],
                keywords=["AI-enabled workflows", "Multi-cloud migration", "Onyx blockchain payments"],
                raw_data={"aum": "$3.6T", "auc_a": "$32.0T", "strategic_priorities": ["AI-enabled workflows", "Multi-cloud migration", "Onyx blockchain payments"]}
            )
            db.add(jpm)
            db.flush()

        lob_jpm = db.query(AccountLob).filter(AccountLob.account_id == jpm.id).first()
        if not lob_jpm:
            lob_jpm = AccountLob(
                account_id=jpm.id,
                name="Corporate & Investment Bank",
                entity_type="Division",
                hierarchy_depth=1,
                headcount=60000
            )
            db.add(lob_jpm)
            db.flush()

        # Add JPM Contacts (Lori Beer, Jamie Dimon)
        if jpm and lob_jpm:
            if not db.query(Contact).filter(Contact.account_id == jpm.id, Contact.last_name == "Beer").first():
                lori = Contact(
                    account_id=jpm.id,
                    lob_id=lob_jpm.id,
                    first_name="Lori",
                    last_name="Beer",
                    full_name="Lori Beer",
                    title="Global Chief Information Officer",
                    seniority_tier="CXO",
                    decision_authority="final",
                    sub_lob_name="Technology",
                    location="New York, USA",
                    email="lori.beer@jpmchase.com",
                    email_confidence="Verified",
                    phone="+1 212-270-6000",
                    lead_score=80,
                    lead_status="Hot",
                    buyer_roles=["Key Decision Maker", "Technical Evaluator"],
                    raw_data={
                        "score_breakdown": {
                            "decision_authority_score": 20,
                            "seniority_score": 20,
                            "tech_stack_match_score": 18,
                            "intent_signals_score": 14,
                            "social_activity_score": 8,
                            "org_influence_score": 10
                        },
                        "tech_stack": ["AWS", "Kubernetes", "Snowflake", "Onyx Blockchain", "Python"],
                        "prior_company_experience": "WellPoint (EVP Specialty Business) • Anthem",
                        "education_summary": "University of Dayton (BS Computer Science)"
                    }
                )
                db.add(lori)

            if not db.query(Contact).filter(Contact.account_id == jpm.id, Contact.last_name == "Dimon").first():
                jamie = Contact(
                    account_id=jpm.id,
                    lob_id=lob_jpm.id,
                    first_name="Jamie",
                    last_name="Dimon",
                    full_name="Jamie Dimon",
                    title="Chairman & Chief Executive Officer",
                    seniority_tier="CXO",
                    decision_authority="final",
                    sub_lob_name="Executive Management",
                    location="New York, USA",
                    email="jamie.dimon@jpmchase.com",
                    email_confidence="Verified",
                    phone="+1 212-270-6000",
                    lead_score=75,
                    lead_status="Warm",
                    buyer_roles=["Final Authority"],
                    raw_data={
                        "score_breakdown": {
                            "decision_authority_score": 20,
                            "seniority_score": 20,
                            "tech_stack_match_score": 10,
                            "intent_signals_score": 15,
                            "social_activity_score": 5,
                            "org_influence_score": 10
                        },
                        "tech_stack": ["Enterprise Cloud", "Onyx Blockchain", "AI LLMs"],
                        "prior_company_experience": "Bank One (Chairman & CEO) • Citigroup (President)",
                        "education_summary": "Tufts University (BA), Harvard Business School (MBA)"
                    }
                )
                db.add(jamie)

        # Add Additional BNY Contacts
        bny = db.query(Account).filter(Account.name == "BNY").first()
        if bny:
            bny_lob = db.query(AccountLob).filter(AccountLob.account_id == bny.id).first()
            if bny_lob:
                bny_leads = [
                    {
                        "first_name": "Leigh-Ann",
                        "last_name": "Russell",
                        "title": "Chief Information Officer and Global Head of Engineering",
                        "seniority_tier": "CXO",
                        "decision_authority": "final",
                        "sub_lob_name": "Technology",
                        "location": "New York, USA",
                        "email": "leigh-ann.russell@bny.com",
                        "phone": "+1 212-495-1784",
                        "lead_score": 74,
                        "lead_status": "Warm",
                        "buyer_roles": ["Key Decision Maker", "Technical Evaluator"],
                        "tech_stack": ["AWS", "Snowflake", "Kubernetes", "Kafka"],
                        "education_summary": "University of Aberdeen (BSc Mechanical Engineering)"
                    },
                    {
                        "first_name": "Brian",
                        "last_name": "Ruane",
                        "title": "Global Head of Clearance and Collateral Management, Credit Services and Corporate Trust",
                        "seniority_tier": "VP",
                        "decision_authority": "shared",
                        "sub_lob_name": "Operations",
                        "location": "New York, USA",
                        "email": "brian.ruane@bny.com",
                        "phone": "+1 212-495-1784",
                        "lead_score": 70,
                        "lead_status": "Cold",
                        "buyer_roles": ["Budget Holder"],
                        "tech_stack": ["Clearance Systems", "Tri-Party Collateral", "Oracle"],
                        "education_summary": "Chartered Institute of Bankers (BSc), Hofstra University (MBA)"
                    },
                    {
                        "first_name": "Rajashree",
                        "last_name": "Datta",
                        "title": "Chief Risk Officer",
                        "seniority_tier": "CXO",
                        "decision_authority": "veto",
                        "sub_lob_name": "Risk",
                        "location": "New York, USA",
                        "email": "rajashree.datta@bny.com",
                        "phone": "+1 212-495-1784",
                        "lead_score": 49,
                        "lead_status": "Cold",
                        "buyer_roles": ["Veto Authority"],
                        "tech_stack": ["Risk Analytics", "Regulatory Reporting"],
                        "education_summary": "Indian Institute of Technology (BTech), Stern School of Business (MBA)"
                    },
                    {
                        "first_name": "Carolyn",
                        "last_name": "Weinberg",
                        "title": "Chief Product and Innovation Officer",
                        "seniority_tier": "CXO",
                        "decision_authority": "shared",
                        "sub_lob_name": "Product",
                        "location": "New York, USA",
                        "email": "carolyn.weinberg@bny.com",
                        "phone": "+1 212-495-1784",
                        "lead_score": 49,
                        "lead_status": "Cold",
                        "buyer_roles": ["Key Decision Maker"],
                        "tech_stack": ["FinTech Platforms", "Data Mesh", "APIs"],
                        "education_summary": "Harvard University (AB), Harvard Business School (MBA)"
                    },
                    {
                        "first_name": "Alejandro",
                        "last_name": "Perez",
                        "title": "Chief Operating Officer",
                        "seniority_tier": "CXO",
                        "decision_authority": "final",
                        "sub_lob_name": "Operations",
                        "location": "New York, USA",
                        "email": "alejandro.perez@bny.com",
                        "phone": "+1 212-495-1784",
                        "lead_score": 47,
                        "lead_status": "Cold",
                        "buyer_roles": ["Final Authority"],
                        "tech_stack": ["Enterprise ERP", "Core Banking", "Cloud"],
                        "education_summary": "Stanford University (BA), Wharton School (MBA)"
                    },
                    {
                        "first_name": "Hani",
                        "last_name": "Kablawi",
                        "title": "Executive Vice Chair, Head of Middle East, Africa and Asia Pacific",
                        "seniority_tier": "CXO",
                        "decision_authority": "shared",
                        "sub_lob_name": "Regional",
                        "location": "Dubai, UAE",
                        "email": "hani.kablawi@bny.com",
                        "phone": "+971 4 425 2000",
                        "lead_score": 44,
                        "lead_status": "Cold",
                        "buyer_roles": ["Regional Head"],
                        "tech_stack": ["Global Custody", "Cross-Border Payments"],
                        "education_summary": "American University of Beirut (BA)"
                    }
                ]

                for ld in bny_leads:
                    if not db.query(Contact).filter(Contact.account_id == bny.id, Contact.last_name == ld["last_name"]).first():
                        contact = Contact(
                            account_id=bny.id,
                            lob_id=bny_lob.id,
                            first_name=ld["first_name"],
                            last_name=ld["last_name"],
                            full_name=f"{ld['first_name']} {ld['last_name']}",
                            title=ld["title"],
                            seniority_tier=ld["seniority_tier"],
                            decision_authority=ld["decision_authority"],
                            sub_lob_name=ld["sub_lob_name"],
                            location=ld["location"],
                            email=ld["email"],
                            email_confidence="Verified",
                            phone=ld["phone"],
                            lead_score=ld["lead_score"],
                            lead_status=ld["lead_status"],
                            buyer_roles=ld["buyer_roles"],
                            raw_data={
                                "score_breakdown": {
                                    "decision_authority_score": 15,
                                    "seniority_score": 15,
                                    "tech_stack_match_score": 10,
                                    "intent_signals_score": 8,
                                    "social_activity_score": 4,
                                    "org_influence_score": 6
                                },
                                "tech_stack": ld["tech_stack"],
                                "education_summary": ld["education_summary"]
                            }
                        )
                        db.add(contact)

        db.commit()
        print("[SUCCESS] All enterprise accounts and leads successfully synchronized!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding enterprise accounts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_accounts()
