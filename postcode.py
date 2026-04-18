"""UK postcode lookup via postcodes.io.

Public API, free, no auth, Open Government Licence v3.0 (already listed
in NOTICE under the ONS / gov.uk chain). Returns admin-district and
parliamentary-constituency information for any valid UK postcode.

No new dependency — uses stdlib ``urllib`` so the project stays inside
its two-package runtime envelope (streamlit + requests, now just
streamlit since requests became unused).

Cached for 24 hours via ``cache.cached`` because the same postcode
resolves to the same admin district for years at a time and there's no
value in re-hitting the API on every sidebar keystroke.
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any

from cache import cached

POSTCODES_API = "https://api.postcodes.io/postcodes"
REQUEST_TIMEOUT_SECONDS = 5
CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _normalise(postcode: str) -> str:
    """Strip whitespace and upper-case. Empty string survives empty."""
    return postcode.strip().upper().replace(" ", "")


@cached(ttl=CACHE_TTL_SECONDS)
def lookup_postcode(postcode: str) -> dict[str, Any] | None:
    """Resolve a UK postcode to admin metadata.

    Returns the postcodes.io ``result`` payload on success, ``None`` on
    any failure (invalid postcode, network error, non-200 response).
    The caller decides how to present the failure to the user.
    """
    normalised = _normalise(postcode)
    if not normalised:
        return None
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            f"{POSTCODES_API}/{normalised}",
            headers={"User-Agent": "forthepeople-uk"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None
    if payload.get("status") != 200:
        return None
    result = payload.get("result")
    return result if isinstance(result, dict) else None


def find_council(
    postcode_result: dict[str, Any],
    councils: dict[str, list[str]],
) -> tuple[str, str] | None:
    """Match a postcodes.io result to a (region, council) in our dataset.

    postcodes.io returns admin names like "City of York", "London
    Borough of Camden", or plain "Leeds"; our council list uses the
    short form ("York", "Camden", "Leeds"). The match strategy is:

    1. Check ``admin_district`` and ``parliamentary_constituency`` for
       an exact case-insensitive match against any council name.
    2. Fall back to substring match (handles the "City of ..." /
       "London Borough of ..." prefixes).
    3. Return ``None`` if nothing matches, so the caller can surface a
       useful message rather than guessing.
    """
    if not isinstance(postcode_result, dict):
        return None

    candidates = [
        str(postcode_result.get("admin_district") or ""),
        str(postcode_result.get("parliamentary_constituency") or ""),
    ]
    candidates = [c.lower() for c in candidates if c]
    if not candidates:
        return None

    # Pass 1 — exact match.
    for region, council_list in councils.items():
        for council in council_list:
            council_lower = council.lower()
            if any(c == council_lower for c in candidates):
                return region, council

    # Pass 2 — substring. Sort by council-name length descending so
    # "Stoke-on-Trent" matches before "Stoke".
    all_councils = [
        (region, council)
        for region, council_list in councils.items()
        for council in council_list
    ]
    all_councils.sort(key=lambda rc: -len(rc[1]))
    for region, council in all_councils:
        council_lower = council.lower()
        if any(council_lower in c for c in candidates):
            return region, council

    return None
