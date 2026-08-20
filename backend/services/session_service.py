"""
Multi-Turn Conversational Memory & Coreference Resolution Engine.

Manages conversational state across user sessions, resolves ambiguous pronouns
(e.g., "his email", "what did she post?", "their budget") back to target entities,
and maintains sliding context windows.
"""

import re
import time
import threading
from typing import Dict, List, Optional, Any


class ConversationTurn:
    def __init__(self, query: str, reply: str, intent: str, entities: Dict[str, Any]):
        self.query = query
        self.reply = reply
        self.intent = intent
        self.entities = entities
        self.timestamp = time.time()


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turns: List[ConversationTurn] = []
        self.last_active_person: Optional[str] = None
        self.last_active_organization: Optional[str] = "BNY"
        self.last_active_role: Optional[str] = None
        self.last_active_topic: Optional[str] = None
        self.last_updated = time.time()

    def add_turn(self, query: str, reply: str, intent: str, entities: Dict[str, Any], top_person_name: Optional[str] = None):
        turn = ConversationTurn(query, reply, intent, entities)
        self.turns.append(turn)
        # Keep last 10 turns
        if len(self.turns) > 10:
            self.turns.pop(0)

        # Update last active entities: prioritize top matched persona returned to user
        if top_person_name:
            self.last_active_person = top_person_name.strip()
        elif entities.get("names"):
            self.last_active_person = entities["names"][0]

        if entities.get("organizations"):
            self.last_active_organization = entities["organizations"][0]
        if entities.get("roles"):
            self.last_active_role = entities["roles"][0]

        self.last_updated = time.time()


class ConversationSessionManager:
    """Thread-safe multi-turn session and coreference resolution manager."""

    def __init__(self, session_ttl_seconds: int = 1800):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = threading.RLock()
        self.session_ttl = session_ttl_seconds

    def get_or_create_session(self, session_id: Optional[str] = None) -> SessionState:
        with self._lock:
            sid = session_id or "default_session"
            if sid not in self._sessions:
                self._sessions[sid] = SessionState(sid)
            return self._sessions[sid]

    def resolve_coreferences(self, query: str, session_id: Optional[str] = None) -> (str, Dict[str, Any]):
        """
        Resolves pronouns ('he', 'his', 'she', 'her', 'they', 'the company', 'this person')
        to previously established entities in the conversation context.
        """
        session = self.get_or_create_session(session_id)
        q_lower = query.lower().strip()
        resolved_query = query
        injected_context = {}

        person_pronoun_pattern = r"\b(he|him|his|she|her|this person|this executive|this leader|the executive)\b"
        org_pronoun_pattern = r"\b(the company|the bank|the firm|the organization|they|their company)\b"

        # Resolve Person Pronouns
        if session.last_active_person and re.search(person_pronoun_pattern, q_lower):
            last_p = session.last_active_person
            # Replace pronoun in copy for extraction
            resolved_query = re.sub(r"\b(his|her)\b", f"{last_p}'s", resolved_query, flags=re.IGNORECASE)
            resolved_query = re.sub(r"\b(he|she|him|this person|this executive|the executive)\b", last_p, resolved_query, flags=re.IGNORECASE)
            injected_context["resolved_person"] = last_p

        # Resolve Organization Pronouns
        if session.last_active_organization and re.search(org_pronoun_pattern, q_lower):
            last_org = session.last_active_organization
            resolved_query = re.sub(r"\b(their company|the bank|the firm|the organization|the company)\b", last_org, resolved_query, flags=re.IGNORECASE)
            injected_context["resolved_organization"] = last_org

        return resolved_query, injected_context

    def record_turn(
        self,
        session_id: Optional[str],
        query: str,
        reply: str,
        intent: str,
        entities: Dict[str, Any],
        top_person_name: Optional[str] = None
    ):
        with self._lock:
            sid = session_id or "default_session"
            if sid not in self._sessions:
                self._sessions[sid] = SessionState(sid)
            self._sessions[sid].add_turn(query, reply, intent, entities, top_person_name=top_person_name)


# Singleton session manager
session_manager = ConversationSessionManager()
