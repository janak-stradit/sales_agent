"""SQLAlchemy models registry (Generic Multi-Organization Account Architecture)."""

# ── Generic Account Models ──────────────────────
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.account_product_service import AccountProductService
from backend.models.account_market_segment import AccountMarketSegment
from backend.models.account_tech_initiative import AccountTechInitiative
from backend.models.account_technology import AccountTechnology
from backend.models.account_taxonomy import AccountTaxonomy

# ── Shared Models ────────────────────────────────
from backend.models.contact import Contact
from backend.models.org_hierarchy import OrgHierarchy
from backend.models.persona import Persona
from backend.models.funding_event import FundingEvent
from backend.models.data_source_evidence import DataSourceEvidence
from backend.models.tool_execution_log import ToolExecutionLog
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.social_intelligence import SocialIntelligence
from backend.models.pipeline_run import PipelineRun

__all__ = [
    "Account",
    "AccountLob",
    "AccountProductService",
    "AccountMarketSegment",
    "AccountTechInitiative",
    "AccountTechnology",
    "AccountTaxonomy",
    "Contact",
    "OrgHierarchy",
    "Persona",
    "FundingEvent",
    "DataSourceEvidence",
    "ToolExecutionLog",
    "SalesTriggerSignal",
    "SocialIntelligence",
    "PipelineRun",
]