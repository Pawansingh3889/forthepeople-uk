"""Tests for data fetching functions.

Tests use live APIs where possible (free, no auth required).
Falls back gracefully on network failures.
"""
from __future__ import annotations

from data import (
    get_weather,
    get_schemes,
    get_essential_services,
    councils,
)
from validators import validate_weather, validate_crime, validate_api_response


class TestCouncilDirectory:
    def test_all_regions_present(self) -> None:
        expected = {
            "Yorkshire and the Humber", "North East", "North West",
            "East Midlands", "West Midlands", "East of England",
            "London", "South East", "South West",
        }
        assert set(councils.keys()) == expected

    def test_each_region_has_councils(self) -> None:
        for region, council_list in councils.items():
            assert len(council_list) > 0, f"{region} has no councils"

    def test_hull_in_yorkshire(self) -> None:
        assert "Hull" in councils["Yorkshire and the Humber"]


class TestWeather:
    def test_get_weather_returns_dict(self) -> None:
        result = get_weather("York")
        assert isinstance(result, dict)
        assert "temp" in result or "error" in result

    def test_validate_weather_good(self) -> None:
        v = validate_weather({"temp": 15.0, "humidity": 60})
        assert v.valid

    def test_validate_weather_missing_temp(self) -> None:
        v = validate_weather({"humidity": 60})
        assert not v.valid

    def test_validate_weather_out_of_range(self) -> None:
        v = validate_weather({"temp": 999})
        assert not v.valid

    def test_validate_weather_empty(self) -> None:
        v = validate_weather({})
        assert not v.valid


class TestSchemes:
    def test_schemes_returns_list(self) -> None:
        result = get_schemes()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_each_scheme_has_name(self) -> None:
        for scheme in get_schemes():
            assert "name" in scheme


class TestEssentialServices:
    def test_returns_list(self) -> None:
        result = get_essential_services()
        assert isinstance(result, list)
        assert len(result) > 0


class TestValidators:
    def test_generic_validator_empty(self) -> None:
        v = validate_api_response(None, "weather")
        assert not v.valid

    def test_generic_validator_unknown_source(self) -> None:
        v = validate_api_response({"data": True}, "unknown_api")
        assert v.valid

    def test_crime_negative_count(self) -> None:
        v = validate_crime({"total": -5})
        assert not v.valid
