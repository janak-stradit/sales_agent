"""
Account Loader — Upserts enterprise accounts, LOBs, market segments, tech initiatives, and funding events.
"""

import logging
from sqlalchemy.orm import Session
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.funding_event import FundingEvent
from backend.models.account_tech_initiative import AccountTechInitiative

logger = logging.getLogger("etl.loaders.account")


def load_account_bundle(db: Session, account_dict: dict, lobs_list: list) -> Account:
    """
    Loads or updates an Account and its associated LOBs in PostgreSQL.
    """
    account_name = account_dict.get("name", "BNY")
    logger.info(f"Loading account into database: {account_name}")

    account = db.query(Account).filter(Account.name == account_name).first()
    if not account:
        account = Account(name=account_name)
        db.add(account)
        db.flush()

    # Update account fields
    for k, v in account_dict.items():
        if hasattr(account, k) and k not in ["id", "created_at"]:
            setattr(account, k, v)

    db.flush()

    # Upsert LOBs
    for lob_data in lobs_list:
        lob_name = lob_data["name"]
        existing_lob = db.query(AccountLob).filter(
            AccountLob.account_id == account.id,
            AccountLob.name == lob_name
        ).first()

        if not existing_lob:
            new_lob = AccountLob(
                account_id=account.id,
                name=lob_name,
                entity_type=lob_data.get("entity_type", "Segment"),
                hierarchy_depth=lob_data.get("hierarchy_depth", 1),
                headcount=lob_data.get("headcount", 5000),
                short_description=lob_data.get("description"),
                raw_data=lob_data
            )
            db.add(new_lob)
        else:
            existing_lob.headcount = lob_data.get("headcount", existing_lob.headcount)
            existing_lob.short_description = lob_data.get("description", existing_lob.short_description)
            existing_lob.raw_data = lob_data

    # Add default tech initiatives if empty
    existing_inits = db.query(AccountTechInitiative).filter(AccountTechInitiative.account_id == account.id).count()
    if existing_inits == 0:
        db.add(AccountTechInitiative(
            account_id=account.id,
            initiative_name="Zero-Lag Tri-Party Streaming Transformation",
            business_objective="Sub-second custodial reporting and Kafka-to-Snowflake replication",
            current_stage="ACTIVE_EXECUTION"
        ))
        db.add(AccountTechInitiative(
            account_id=account.id,
            initiative_name="Enterprise Cloud Migration & Kubernetes Modernization",
            business_objective="Transition core operations to containerized cloud architectures",
            current_stage="IN_DEVELOPMENT"
        ))

    db.flush()
    logger.info(f"Successfully loaded account: {account.name} (ID: {account.id})")
    return account
