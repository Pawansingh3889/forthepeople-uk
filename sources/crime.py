"""Live street-level crime from the Police UK open data API (no key).

Two-request flow: ``crime-last-updated`` gives the latest published month,
then ``crimes-street/all-crime`` returns one dict per crime within roughly a
one-mile radius of the given coordinates. The data updates monthly.
"""
from __future__ import annotations

import requests

from cache import cached
from registry import COORDS, UK_ALL
from sources.base import SourceResult

SOURCE = "Police UK"
URL = "https://data.police.uk"

# Police UK street-level categories mapped onto the buckets the UI shows.
CATEGORY_MAP = {
    "anti-social-behaviour": "antisocial",
    "violent-crime": "violent",
    "burglary": "burglary",
    "drugs": "drugs",
    "vehicle-crime": "vehicle",
}


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


@cached(ttl=21_600, cache_if=lambda r: r.live)
def fetch(council: str) -> SourceResult:
    """Counts by category for the latest published month.

    Returns an unavailable result (data=None) when the location has no usable
    coordinates or the API can't be reached; callers decide the fallback. The
    whole-UK view is always unavailable here, because a one-mile radius around
    the UK centroid means nothing.
    """
    coords = COORDS.get(council)
    if not coords or council == UK_ALL:
        return _unavailable()
    lat, lon = coords
    try:
        month = requests.get("https://data.police.uk/api/crime-last-updated", timeout=10).json().get("date")
        crimes = requests.get(
            "https://data.police.uk/api/crimes-street/all-crime",
            params={"lat": lat, "lng": lon, "date": month}, timeout=15,
        ).json()
        if not isinstance(crimes, list):
            return _unavailable()
        counts = {"total": len(crimes), "antisocial": 0, "violent": 0,
                  "burglary": 0, "drugs": 0, "vehicle": 0}
        for c in crimes:
            bucket = CATEGORY_MAP.get(c.get("category"))
            if bucket:
                counts[bucket] += 1
        return SourceResult(data=counts, live=True, asof=month, source=SOURCE, url=URL)
    except Exception:
        return _unavailable()
