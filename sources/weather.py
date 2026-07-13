"""Live weather from Open-Meteo (no API key).

Current conditions plus a 7-day forecast for a council's centre coordinates.
"""
from __future__ import annotations

import requests

from cache import cached
from registry import COORDS
from sources.base import SourceResult

SOURCE = "Open-Meteo"
URL = "https://open-meteo.com"

WEATHER_CODES = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 51: "Light Drizzle", 53: "Drizzle", 61: "Light Rain",
    63: "Rain", 65: "Heavy Rain", 71: "Light Snow", 73: "Snow",
    80: "Rain Showers", 95: "Thunderstorm",
}


@cached(ttl=600)
def fetch(location: str) -> SourceResult:
    lat, lon = COORDS.get(location, (53.96, -1.08))
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,uv_index_max,sunrise,sunset"
            f"&timezone=Europe/London&forecast_days=7", timeout=10
        ).json()
        cur = r.get("current", {})
        daily = r.get("daily", {})
        data = {
            "temp": cur.get("temperature_2m"), "feels_like": cur.get("apparent_temperature"),
            "humidity": cur.get("relative_humidity_2m"), "wind": cur.get("wind_speed_10m"),
            "condition": WEATHER_CODES.get(cur.get("weather_code", 0), "Unknown"),
            "forecast": [{"date": daily["time"][i], "max": daily["temperature_2m_max"][i],
                         "min": daily["temperature_2m_min"][i], "rain": daily["precipitation_sum"][i],
                         "uv": daily.get("uv_index_max", [0]*7)[i],
                         "sunrise": daily.get("sunrise", [""] * 7)[i][11:16] if daily.get("sunrise") else "",
                         "sunset": daily.get("sunset", [""] * 7)[i][11:16] if daily.get("sunset") else "",
                         "condition": WEATHER_CODES.get(daily["weather_code"][i], "Unknown")}
                        for i in range(len(daily.get("time", [])))],
        }
        asof = daily["time"][0] if daily.get("time") else None
        return SourceResult(data=data, live=True, asof=asof, source=SOURCE, url=URL)
    except Exception as e:
        return SourceResult(data={"error": str(e)}, live=False, asof=None, source=SOURCE, url=URL)
