"""Live UK Parliament petitions (open JSON, no key).

The top open petitions by signature count, national rather than council-level.
Two thresholds matter and the UI shows progress toward them: 10,000 signatures
gets a government response, 100,000 makes a petition eligible for debate.
"""
from __future__ import annotations

import requests

from cache import cached
from sources.base import SourceResult

SOURCE = "UK Parliament petitions"
URL = "https://petition.parliament.uk"
RESPONSE_THRESHOLD = 10_000
DEBATE_THRESHOLD = 100_000


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


@cached(ttl=3600, cache_if=lambda r: r.live)
def fetch(limit: int = 15) -> SourceResult:
    """Top `limit` open petitions, most-signed first."""
    try:
        r = requests.get(f"{URL}/petitions.json", params={"state": "open"}, timeout=15).json()
    except Exception:
        return _unavailable()
    items = r.get("data")
    if not isinstance(items, list):
        return _unavailable()
    petitions = []
    for p in items:
        attrs = p.get("attributes") or {}
        action = attrs.get("action")
        count = attrs.get("signature_count")
        if not action or not isinstance(count, int):
            continue
        petitions.append({
            "action": action,
            "signatures": count,
            "url": f"{URL}/petitions/{p.get('id')}",
            "government_responded": attrs.get("government_response") is not None,
            "debated": attrs.get("debate_threshold_reached_at") is not None,
        })
    if not petitions:
        return _unavailable()
    petitions.sort(key=lambda x: -x["signatures"])
    return SourceResult(data=petitions[:limit], live=True, asof=None, source=SOURCE, url=URL)
