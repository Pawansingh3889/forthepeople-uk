"""Live air quality from the Open-Meteo Air Quality API (no key).

Current European Air Quality Index (EAQI) plus the main pollutants for a
council's centre coordinates. Same provider and no-key pattern as weather.
"""
from __future__ import annotations

import requests

from cache import cached
from registry import COORDS, UK_ALL
from sources.base import SourceResult

SOURCE = "Open-Meteo Air Quality"
URL = "https://open-meteo.com"


def aqi_band(aqi) -> str:
    """European AQI band label. Bands per the EAQI definition."""
    if aqi is None:
        return "Unknown"
    if aqi <= 20:
        return "Good"
    if aqi <= 40:
        return "Fair"
    if aqi <= 60:
        return "Moderate"
    if aqi <= 80:
        return "Poor"
    if aqi <= 100:
        return "Very poor"
    return "Extremely poor"


def _unavailable() -> SourceResult:
    return SourceResult(data=None, live=False, asof=None, source=SOURCE, url=URL)


@cached(ttl=1800)
def fetch(council: str) -> SourceResult:
    """Current EAQI + pollutants. The whole-UK centroid is skipped as a single
    point that would not represent the country."""
    coords = COORDS.get(council)
    if not coords or council == UK_ALL:
        return _unavailable()
    lat, lon = coords
    try:
        r = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": lat, "longitude": lon,
                "current": "european_aqi,pm2_5,pm10,nitrogen_dioxide,ozone",
                "timezone": "Europe/London",
            }, timeout=10,
        ).json()
        cur = r.get("current") or {}
        aqi = cur.get("european_aqi")
        if aqi is None:
            return _unavailable()
        return SourceResult(
            data={
                "aqi": aqi, "band": aqi_band(aqi),
                "pm2_5": cur.get("pm2_5"), "pm10": cur.get("pm10"),
                "no2": cur.get("nitrogen_dioxide"), "ozone": cur.get("ozone"),
            },
            live=True, asof=cur.get("time"), source=SOURCE, url=URL,
        )
    except Exception:
        return _unavailable()
