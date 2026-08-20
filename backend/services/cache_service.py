"""
High-Performance In-Memory Semantic Query Cache with TTL.

Provides sub-10ms response times for high-frequency sales queries and embedding lookups.
Thread-safe with LRU eviction and hit/miss telemetry.
"""

import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict


class SemanticQueryCache:
    """Thread-safe LRU cache with expiration TTL for sales chatbot queries."""

    def __init__(self, max_size: int = 500, ttl_seconds: int = 600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def _normalize_key(self, query: str, session_id: Optional[str] = None) -> str:
        q_norm = query.strip().lower()
        if session_id:
            return f"{session_id}::{q_norm}"
        return q_norm

    def get(self, query: str, session_id: Optional[str] = None) -> Optional[Any]:
        """Retrieves cached response if valid and unexpired."""
        key = self._normalize_key(query, session_id)
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry["data"]

    def set(self, query: str, data: Any, session_id: Optional[str] = None, custom_ttl: Optional[int] = None) -> None:
        """Stores response in cache with TTL."""
        key = self._normalize_key(query, session_id)
        ttl = custom_ttl if custom_ttl is not None else self.ttl_seconds
        expires_at = time.time() + ttl

        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = {
                "data": data,
                "expires_at": expires_at,
                "cached_at": time.time()
            }

            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Evict oldest entry

    def clear(self) -> None:
        """Clears all cached items."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_ratio = round((self._hits / total_requests) * 100, 2) if total_requests > 0 else 0.0
            return {
                "total_cached_items": len(self._cache),
                "max_capacity": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_percent": hit_ratio,
                "ttl_seconds": self.ttl_seconds
            }


# Singleton instance
query_cache = SemanticQueryCache(max_size=1000, ttl_seconds=600)
