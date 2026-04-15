"""API response validation for ForThePeople UK.

Validates government API responses before they reach the dashboard.
Inspired by PyCon DE 2026: "Ship Data with Confidence" (Sequeira).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiValidation:
    valid: bool
    source: str
    message: str


def validate_weather(data: dict) -> ApiValidation:
    """Validate Open-Meteo weather response."""
    if not data or not isinstance(data, dict):
        return ApiValidation(False, "open-meteo", "Empty or invalid response")
    if "temp" not in data or data["temp"] is None:
        return ApiValidation(False, "open-meteo", "Missing temperature")
    if not (-50 <= data["temp"] <= 50):
        return ApiValidation(False, "open-meteo", f"Temperature {data['temp']}C out of range")
    return ApiValidation(True, "open-meteo", "OK")


def validate_crime(data: dict) -> ApiValidation:
    """Validate Police UK crime stats response."""
    if not data or not isinstance(data, dict):
        return ApiValidation(False, "police-uk", "Empty or invalid response")
    if "total" in data and data["total"] < 0:
        return ApiValidation(False, "police-uk", "Negative crime count")
    return ApiValidation(True, "police-uk", "OK")


def validate_council(data: dict) -> ApiValidation:
    """Validate council data response."""
    if not data or not isinstance(data, dict):
        return ApiValidation(False, "council", "Empty or invalid response")
    return ApiValidation(True, "council", "OK")


def validate_api_response(data: Any, source: str) -> ApiValidation:
    """Generic validation dispatcher."""
    validators = {
        "weather": validate_weather,
        "crime": validate_crime,
        "council": validate_council,
    }
    validator = validators.get(source)
    if validator:
        return validator(data)
    if not data:
        return ApiValidation(False, source, "Empty response")
    return ApiValidation(True, source, "OK")
