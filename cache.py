"""API response caching for ForThePeople UK.

Uses diskcache for persistent caching of government API responses.
Reduces API calls and speeds up page loads.

Inspired by PyCon DE 2026: "Wetterdienst" (Gutzmann) — diskcache + stamina for resilience.
"""
from __future__ import annotations

import hashlib
import json
import os
from functools import wraps
from typing import Any, Callable

CACHE_DIR = os.getenv("FTP_CACHE_DIR", ".cache/api")
CACHE_TTL = int(os.getenv("FTP_CACHE_TTL", "3600"))  # 1 hour default

try:
    import diskcache
    _cache = diskcache.Cache(CACHE_DIR)
except ImportError:
    _cache = None


def cached(ttl: int = CACHE_TTL) -> Callable:
    """Cache function results to disk. Falls back to no-cache if diskcache unavailable."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _cache is None:
                return fn(*args, **kwargs)
            key = hashlib.md5(
                json.dumps({"fn": fn.__name__, "args": args, "kwargs": sorted(kwargs.items())}).encode()
            ).hexdigest()
            result = _cache.get(key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            _cache.set(key, result, expire=ttl)
            return result
        return wrapper
    return decorator
