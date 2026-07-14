"""Live population from the ONS mid-year estimates, via the Nomis API (no key).

Nomis (run for the ONS) accepts GSS codes directly, which is exactly what the
registry stores. One wrinkle: ONS re-codes an authority after a boundary
change (Sheffield and Barnsley most recently), and Nomis vintages can lag
behind the geocoder, so an empty result for the current code retries once
with the authority's previous code.
"""
from __future__ import annotations

import requests

from cache import cached
from registry import REGISTRY
from sources.base import SourceResult

SOURCE = "ONS via Nomis"
URL = "https://www.nomisweb.co.uk"
API = "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.json"

# Current GSS code -> the code it replaced. Tried second when the current
# one returns no observations.
OLD_GSS_ALIASES = {
    "E08000039": "E08000019",  # Sheffield
    "E08000038": "E08000016",  # Barnsley
}


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


@cached(ttl=86_400, cache_if=lambda r: r.live)
def fetch(council: str) -> SourceResult:
    """Latest mid-year total population for the council's authority.

    The whole-UK view works too: K02000001 is a valid Nomis geography.
    """
    entry = REGISTRY.get(council)
    if not entry:
        return _unavailable()
    for code in (entry.gss, OLD_GSS_ALIASES.get(entry.gss)):
        if not code:
            continue
        try:
            r = requests.get(API, params={
                "geography": code, "date": "latest",
                "gender": 0, "c_age": 200, "measures": 20100,
            }, timeout=15).json()
        except Exception:
            return _unavailable()
        obs = r.get("obs") or []
        if not obs:
            continue
        value = (obs[0].get("obs_value") or {}).get("value")
        year = (obs[0].get("time") or {}).get("value")
        if isinstance(value, (int, float)) and value > 0:
            return SourceResult(data={"population": int(value), "year": str(year)},
                                live=True, asof=str(year), source=SOURCE, url=URL)
    return _unavailable()
