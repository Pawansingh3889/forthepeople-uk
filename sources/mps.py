"""Live MPs from the UK Parliament Members API (no key).

Finds the constituencies matching a council's name (or its registry
``mp_search`` override), then reads each one's current member, party and —
where the extra lookup succeeds — the majority from the latest election
result. Data is published under the Open Parliament Licence v3.0.
"""
from __future__ import annotations

import re

import requests

from cache import cached
from registry import REGISTRY, UK_ALL
from sources.base import SourceResult

SOURCE = "UK Parliament"
URL = "https://members.parliament.uk"
API = "https://members-api.parliament.uk/api"


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


def _majority(member_id: int) -> int | None:
    try:
        result = requests.get(f"{API}/Members/{member_id}/LatestElectionResult", timeout=10).json()
        majority = result.get("value", {}).get("majority")
        return majority if isinstance(majority, int) else None
    except Exception:
        return None


@cached(ttl=86_400, cache_if=lambda r: r.live)
def fetch(council: str) -> SourceResult:
    """Current MPs for the constituencies matching a council.

    The Parliament search is substring-based ("Hull" also returns the
    Solihull constituencies), so results are filtered to whole-word matches
    of the search term. Councils whose constituencies share no words with
    their name (for example Camden's Holborn and St Pancras) come back
    unavailable and the caller falls back to its static table.
    """
    entry = REGISTRY.get(council)
    if not entry or council == UK_ALL:
        return _unavailable()
    term = entry.mp_search or entry.name
    try:
        r = requests.get(
            f"{API}/Location/Constituency/Search",
            params={"searchText": term, "skip": 0, "take": 20}, timeout=10,
        ).json()
        word = re.compile(rf"\b{re.escape(term)}\b")
        mps = []
        for item in r.get("items", []):
            value = item.get("value", {})
            name = value.get("name", "")
            if not word.search(name):
                continue
            member = ((value.get("currentRepresentation") or {}).get("member") or {}).get("value") or {}
            if not member.get("nameDisplayAs"):
                continue  # vacant seat
            mp = {
                "name": member["nameDisplayAs"],
                "party": (member.get("latestParty") or {}).get("name", "Unknown"),
                "constituency": name,
                "live": True,
            }
            majority = _majority(member["id"]) if member.get("id") else None
            if majority is not None:
                mp["majority"] = majority
            mps.append(mp)
        if not mps:
            return _unavailable()
        mps.sort(key=lambda m: m["constituency"])
        return SourceResult(data=mps, live=True, asof=None, source=SOURCE, url=URL)
    except Exception:
        return _unavailable()
