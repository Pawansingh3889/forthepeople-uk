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


def cached(ttl: int = CACHE_TTL, cache_if: Callable[[Any], bool] | None = None) -> Callable:
    """Cache function results to disk. Falls back to no-cache if diskcache unavailable.

    ``cache_if`` decides whether a freshly computed result is worth keeping:
    sources pass ``lambda r: r.live`` so a transient API failure is retried on
    the next call instead of pinning the fallback for the whole TTL.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _cache is None:
                return fn(*args, **kwargs)
            # Key on module + qualname, not the bare name: every module in
            # sources/ exposes a function called ``fetch``, and keying on the
            # name alone made them share cache entries, so whichever source
            # fetched a council first fed its payload to all the others.
            key = hashlib.md5(
                json.dumps({"fn": f"{fn.__module__}.{fn.__qualname__}", "args": args,
                            "kwargs": sorted(kwargs.items())}).encode()
            ).hexdigest()
            result = _cache.get(key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            if cache_if is None or cache_if(result):
                _cache.set(key, result, expire=ttl)
            return result
        return wrapper
    return decorator
