"""
Redis cache utility — caches Monid API responses to avoid duplicate calls.
TTL default: 7 days (configurable via CACHE_TTL_SECONDS).
"""

import json
import redis
import logging
from typing import Optional
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Redis Connection ───────────────────────────
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def cache_get(key: str) -> Optional[dict]:
    """Get cached JSON value by key."""
    try:
        data = redis_client.get(key)
        if data:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


def cache_set(key: str, value: dict, ttl: int = None) -> None:
    """Set cached JSON value with TTL."""
    try:
        ttl = ttl or settings.CACHE_TTL_SECONDS
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


def cache_delete(key: str) -> None:
    """Delete a cached value."""
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")


def make_cache_key(prefix: str, *args) -> str:
    """Build a cache key from prefix and arguments."""
    parts = [str(a) for a in args if a]
    return f"salesai:{prefix}:{':'.join(parts)}"
