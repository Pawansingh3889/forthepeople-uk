"""Live flood warnings from the Environment Agency flood-monitoring API (no key).

Active warnings within about 30km of a council's centre. An empty list is a
real, useful answer ("checked, none active") and is returned as live with no
warnings; only a failed call is treated as unavailable.
"""
from __future__ import annotations

import requests

from cache import cached
from registry import COORDS, UK_ALL
from sources.base import SourceResult

SOURCE = "Environment Agency"
URL = "https://check-for-flooding.service.gov.uk"

# severityLevel meanings per the EA reference. 4 = no longer in force.
SEVERITY = {
    1: "Severe flood warning",
    2: "Flood warning",
    3: "Flood alert",
    4: "Warning no longer in force",
}


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


@cached(ttl=1800, cache_if=lambda r: r.live)
def fetch(council: str) -> SourceResult:
    """Flood warnings near the council. live + [] means checked and none active."""
    coords = COORDS.get(council)
    if not coords or council == UK_ALL:
        return _unavailable()
    lat, lon = coords
    try:
        r = requests.get(
            "https://environment.data.gov.uk/flood-monitoring/id/floods",
            params={"lat": lat, "long": lon, "dist": 30}, timeout=15,
        ).json()
    except Exception:
        return _unavailable()
    items = r.get("items")
    if not isinstance(items, list):
        return _unavailable()
    warnings = []
    for it in items:
        level = it.get("severityLevel")
        area = it.get("floodArea") or {}
        warnings.append({
            "severity": it.get("severity") or SEVERITY.get(level, "Unknown"),
            "level": level,
            "description": it.get("description", ""),
            "river_or_sea": area.get("riverOrSea", ""),
            "message": it.get("message", ""),
            "time_raised": it.get("timeRaised", ""),
        })
    warnings.sort(key=lambda w: (w["level"] if isinstance(w["level"], int) else 9))
    return SourceResult(data=warnings, live=True, asof=None, source=SOURCE, url=URL)
