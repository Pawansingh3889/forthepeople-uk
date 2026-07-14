"""Live average house prices from the HM Land Registry UK House Price Index.

The UKHPI linked-data API is keyless but keyed by region slug, not GSS code,
so the slug is derived from the registry's authority name (with an override
table for the awkward ones). Publication lags a couple of months, so the
fetch walks back from two months ago until a month responds. The UK-wide
figure for the same month gives the vs-UK comparison.
"""
from __future__ import annotations

from datetime import date

import requests

from cache import cached
from registry import REGISTRY, UK_ALL
from sources.base import SourceResult

SOURCE = "HM Land Registry UKHPI"
URL = "https://landregistry.data.gov.uk/app/ukhpi"
BASE = "https://landregistry.data.gov.uk/data/ukhpi/region"

UK_SLUG = "united-kingdom"
SLUG_OVERRIDES = {
    "Westminster": "city-of-westminster",
}


def _slug(entry) -> str:
    if entry.name in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[entry.name]
    authority = entry.authority
    # "Kingston upon Hull, City of" -> "City of Kingston upon Hull"
    if authority.endswith(", City of"):
        authority = "City of " + authority[: -len(", City of")]
    return authority.replace(",", "").replace(".", "").lower().replace(" ", "-")


def _month_candidates(count: int = 4) -> list[str]:
    """Recent months, newest first, starting two months back."""
    today = date.today()
    months = []
    year, month = today.year, today.month
    for back in range(2, 2 + count):
        y, m = year, month - back
        while m < 1:
            m += 12
            y -= 1
        months.append(f"{y:04d}-{m:02d}")
    return months


def _region_month(slug: str, month: str) -> dict | None:
    r = requests.get(f"{BASE}/{slug}/month/{month}.json", timeout=15)
    if r.status_code != 200:
        return None
    topic = (r.json().get("result") or {}).get("primaryTopic") or {}
    price = topic.get("averagePrice")
    if not isinstance(price, (int, float)):
        return None
    ref = topic.get("refMonth", month)
    if isinstance(ref, dict):  # linked-data form: {"_value": "2026-03", ...}
        ref = ref.get("_value", month)
    return {
        "avg_price": int(price),
        "annual_change": topic.get("percentageAnnualChange"),
        "month": str(ref),
    }


@cached(ttl=86_400, cache_if=lambda r: r.live)
def fetch(council: str) -> SourceResult:
    entry = REGISTRY.get(council)
    if not entry:
        return _unavailable()
    slug = UK_SLUG if council == UK_ALL else _slug(entry)
    try:
        for month in _month_candidates():
            data = _region_month(slug, month)
            if not data:
                continue
            if slug != UK_SLUG:
                uk = _region_month(UK_SLUG, data["month"])
                data["vs_uk"] = data["avg_price"] - uk["avg_price"] if uk else None
            return SourceResult(data=data, live=True, asof=data["month"],
                                source=SOURCE, url=URL)
    except Exception:
        pass
    return _unavailable()


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)
