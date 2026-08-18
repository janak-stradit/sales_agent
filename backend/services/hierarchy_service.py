"""HierarchyService — Organizational Hierarchy Tree & Span-of-Control Analytics (Tab 4)."""

import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.account import Account
from backend.models.contact import Contact
from backend.models.org_hierarchy import OrgHierarchy
from backend.schemas.hierarchy_schemas import (
    HierarchyTreeNodeResponse,
    SpanOfControlMetricsResponse,
    ReportingChainNode,
    ReportingChainResponse,
)

logger = logging.getLogger(__name__)


def build_hierarchy_tree(
    db: Session,
    account_id: UUID,
    lob_id: Optional[UUID] = None
) -> List[HierarchyTreeNodeResponse]:
    """
    Builds a full nested hierarchical tree structure starting from root nodes (Level 1 / CEO / Top Executives).
    """
    query = (
        db.query(Contact, OrgHierarchy)
        .join(OrgHierarchy, Contact.id == OrgHierarchy.contact_id)
        .filter(Contact.account_id == account_id)
    )
    if lob_id:
        query = query.filter(Contact.lob_id == lob_id)

    results = query.order_by(OrgHierarchy.level, Contact.lead_score.desc()).all()

    if not results:
        return []

    nodes_by_id: Dict[UUID, Dict[str, Any]] = {}
    manager_to_children: Dict[Optional[UUID], List[UUID]] = {}

    for contact, hier in results:
        first = contact.first_name or ""
        last = contact.last_name or ""
        avatar_initials = f"{first[:1]}{last[:1]}".upper() if (first or last) else "EP"
        lead_status = "Hot" if contact.lead_score >= 80 else ("Warm" if contact.lead_score >= 50 else "Cold")

        node_data = {
            "id": hier.id,
            "contact_id": contact.id,
            "full_name": contact.full_name or f"{first} {last}".strip(),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "title": contact.title or "Executive",
            "email": contact.email,
            "phone": contact.phone,
            "avatar_url": contact.avatar_url,
            "avatar_initials": avatar_initials,
            "location": contact.location or "New York, USA",
            "seniority_tier": contact.seniority_tier or "CXO",
            "target_persona_type": contact.target_persona_type or "Executive Decision Maker",
            "decision_authority": hier.decision_authority or contact.decision_authority or "final",
            "budget_authority": hier.budget_authority or contact.budget_authority or "full",
            "lead_score": contact.lead_score,
            "lead_status": lead_status,
            "level": hier.level,
            "reports_to_path": str(hier.reports_to_path) if hier.reports_to_path else None,
            "manager_id": hier.manager_id,
            "manager_name": hier.reports_to_name,
            "lob_id": contact.lob_id,
            "lob_name": contact.lob.name if contact.lob else None,
            "direct_reports_count": 0,
            "total_subtree_count": 0,
            "children": []
        }
        nodes_by_id[contact.id] = node_data

        mgr_id = hier.manager_id
        if mgr_id not in manager_to_children:
            manager_to_children[mgr_id] = []
        manager_to_children[mgr_id].append(contact.id)

    def attach_children(contact_id: UUID) -> Dict[str, Any]:
        node = nodes_by_id[contact_id]
        child_ids = manager_to_children.get(contact_id, [])
        children = []
        total_sub = 0

        for cid in child_ids:
            if cid in nodes_by_id:
                child_node = attach_children(cid)
                children.append(child_node)
                total_sub += 1 + child_node["total_subtree_count"]

        node["direct_reports_count"] = len(children)
        node["total_subtree_count"] = total_sub
        node["children"] = children
        return node

    root_ids = manager_to_children.get(None, [])
    if not root_ids:
        min_level = min(n["level"] for n in nodes_by_id.values())
        root_ids = [cid for cid, n in nodes_by_id.items() if n["level"] == min_level]

    root_trees = []
    for rid in root_ids:
        if rid in nodes_by_id:
            root_trees.append(HierarchyTreeNodeResponse(**attach_children(rid)))

    return root_trees


def get_span_of_control_metrics(db: Session, account_id: UUID) -> SpanOfControlMetricsResponse:
    """Calculates hierarchy depth, manager spans of control, and decision power distribution."""
    account = db.query(Account).filter(Account.id == account_id).first()
    account_name = account.name if account else "Unknown Account"

    hier_nodes = (
        db.query(OrgHierarchy, Contact)
        .join(Contact, OrgHierarchy.contact_id == Contact.id)
        .filter(Contact.account_id == account_id)
        .all()
    )

    if not hier_nodes:
        return SpanOfControlMetricsResponse(
            account_id=account_id,
            account_name=account_name,
            max_depth=1,
            total_nodes=0,
            average_span_of_control=0.0,
            level_distribution={},
            decision_power_distribution={},
            top_decision_nodes=[]
        )

    max_depth = max((h.level for h, _ in hier_nodes), default=1)
    total_nodes = len(hier_nodes)

    managers: Dict[UUID, int] = {}
    for h, _ in hier_nodes:
        if h.manager_id:
            managers[h.manager_id] = managers.get(h.manager_id, 0) + 1

    avg_span = sum(managers.values()) / len(managers) if managers else 0.0

    level_dist: Dict[int, int] = {}
    for h, _ in hier_nodes:
        level_dist[h.level] = level_dist.get(h.level, 0) + 1

    decision_dist: Dict[str, int] = {}
    for h, c in hier_nodes:
        auth = h.decision_authority or c.decision_authority or "none"
        decision_dist[auth] = decision_dist.get(auth, 0) + 1

    top_nodes = []
    for h, c in sorted(hier_nodes, key=lambda pair: pair[1].lead_score, reverse=True)[:5]:
        top_nodes.append({
            "contact_id": str(c.id),
            "name": c.full_name,
            "title": c.title,
            "level": h.level,
            "decision_authority": h.decision_authority or c.decision_authority,
            "direct_reports": managers.get(c.id, 0),
            "lead_score": c.lead_score
        })

    return SpanOfControlMetricsResponse(
        account_id=account_id,
        account_name=account_name,
        max_depth=max_depth,
        total_nodes=total_nodes,
        average_span_of_control=round(avg_span, 1),
        level_distribution=level_dist,
        decision_power_distribution=decision_dist,
        top_decision_nodes=top_nodes
    )


def get_reporting_chain(db: Session, contact_id: UUID) -> ReportingChainResponse:
    """Gets the upward reporting chain to CEO and direct subordinates for a contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ValueError(f"Contact {contact_id} not found")

    hierarchy = contact.org_node

    upward_chain = []
    curr = hierarchy
    visited = set()

    while curr and curr.manager_id and curr.manager_id not in visited:
        visited.add(curr.manager_id)
        mgr_contact = db.query(Contact).filter(Contact.id == curr.manager_id).first()
        if not mgr_contact:
            break
        mgr_hier = mgr_contact.org_node
        upward_chain.append(ReportingChainNode(
            contact_id=mgr_contact.id,
            full_name=mgr_contact.full_name,
            title=mgr_contact.title,
            level=mgr_hier.level if mgr_hier else 1,
            decision_authority=mgr_contact.decision_authority or "final",
            budget_authority=mgr_contact.budget_authority or "full",
            reports_to_path=str(mgr_hier.reports_to_path) if mgr_hier and mgr_hier.reports_to_path else None
        ))
        curr = mgr_hier

    subordinate_hierarchies = db.query(OrgHierarchy, Contact).join(Contact, OrgHierarchy.contact_id == Contact.id).filter(OrgHierarchy.manager_id == contact_id).all()

    direct_reports = [
        ReportingChainNode(
            contact_id=c.id,
            full_name=c.full_name,
            title=c.title,
            level=h.level,
            decision_authority=c.decision_authority or "operational",
            budget_authority=c.budget_authority or "delegated",
            reports_to_path=str(h.reports_to_path) if h.reports_to_path else None
        )
        for h, c in subordinate_hierarchies
    ]

    return ReportingChainResponse(
        contact_id=contact.id,
        full_name=contact.full_name,
        title=contact.title,
        upward_chain=upward_chain,
        direct_reports=direct_reports,
        total_subordinates_count=len(direct_reports)
    )
