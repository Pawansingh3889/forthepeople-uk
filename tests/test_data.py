"""Tests for data fetching functions.

Tests use live APIs where possible (free, no auth required).
Falls back gracefully on network failures.
"""
from __future__ import annotations

from unittest import mock

from data import (
    UK_ALL,
    COORDS,
    councils,
    get_council_data,
    get_essential_services,
    get_schemes,
    get_weather,
)
from validators import validate_weather, validate_crime, validate_api_response


class TestCouncilDirectory:
    def test_all_regions_present(self) -> None:
        # Every English region from the ONS nine-region split must be
        # present. The "United Kingdom (national)" pseudo-region sits
        # alongside them as the whole-UK rollup; we require it to exist
        # but don't pin the exact set, so a future Scotland/Wales/NI
        # region addition doesn't break this test.
        required = {
            "Yorkshire and the Humber", "North East", "North West",
            "East Midlands", "West Midlands", "East of England",
            "London", "South East", "South West",
            "United Kingdom (national)",
        }
        assert required.issubset(set(councils.keys()))

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
    def test_schemes_returns_dict_of_categories(self) -> None:
        # Contract: ``get_schemes`` returns a dict keyed by category
        # (``business``, ``housing``, ``energy``, etc.), each value being
        # a list of scheme dicts.
        result = get_schemes()
        assert isinstance(result, dict)
        assert len(result) > 0
        for category, schemes in result.items():
            assert isinstance(category, str)
            assert isinstance(schemes, list)

    def test_each_scheme_has_name(self) -> None:
        for schemes in get_schemes().values():
            for scheme in schemes:
                assert isinstance(scheme, dict), f"expected dict, got {type(scheme)}"
                assert "name" in scheme, f"scheme missing 'name' key: {scheme}"


class TestEssentialServices:
    def test_returns_dict_of_categories(self) -> None:
        # Contract: ``get_essential_services`` returns a dict keyed by
        # category (``emergency``, ``health``, ``social``, etc.), each
        # value being a list of service dicts.
        result = get_essential_services()
        assert isinstance(result, dict)
        assert len(result) > 0
        for category, services in result.items():
            assert isinstance(category, str)
            assert isinstance(services, list)


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


class TestGetWeatherSunriseRegression:
    """Regression for the ``[""][7]`` typo in the sunrise/sunset defaults.

    ``dict.get("key", default)`` evaluates ``default`` eagerly, so a
    literal ``[""][7]`` raises IndexError at call time even when the
    ``.get`` key is present. Open-Meteo started returning ``sunrise`` /
    ``sunset`` in daily payloads, which made the ``if daily.get("sunrise")``
    branch live and the typo started blowing up every weather fetch.

    The fix uses ``[""] * 7`` (a 7-element list) as the default. These
    tests assert ``get_weather`` never raises IndexError regardless of
    whether the API payload includes sunrise/sunset.
    """

    def _mocked_requests(self, daily_extra: dict) -> mock.MagicMock:
        """Return a requests.get-compatible mock returning a realistic payload."""
        seven_dates = [f"2026-04-{18+i:02d}" for i in range(7)]
        payload = {
            "current": {
                "temperature_2m": 12.0,
                "apparent_temperature": 11.0,
                "relative_humidity_2m": 70,
                "wind_speed_10m": 10,
                "weather_code": 2,
            },
            "daily": {
                "time": seven_dates,
                "temperature_2m_max": [14.0] * 7,
                "temperature_2m_min": [8.0] * 7,
                "precipitation_sum": [0.0] * 7,
                "weather_code": [2] * 7,
                **daily_extra,
            },
        }
        m = mock.MagicMock()
        m.json.return_value = payload
        return m

    def test_weather_ok_without_sunrise_field(self) -> None:
        from data import get_weather as gw
        with mock.patch("data.requests.get", return_value=self._mocked_requests({})):
            result = gw("TestTownNoSunrise")
        assert "error" not in result, f"get_weather raised: {result.get('error')}"
        assert len(result["forecast"]) == 7
        assert all(f["sunrise"] == "" for f in result["forecast"])

    def test_weather_ok_with_sunrise_field(self) -> None:
        from data import get_weather as gw
        seven_sunrises = [f"2026-04-{18+i:02d}T05:30:00" for i in range(7)]
        seven_sunsets = [f"2026-04-{18+i:02d}T20:15:00" for i in range(7)]
        with mock.patch(
            "data.requests.get",
            return_value=self._mocked_requests({"sunrise": seven_sunrises, "sunset": seven_sunsets}),
        ):
            result = gw("TestTownWithSunrise")
        assert "error" not in result, f"get_weather raised: {result.get('error')}"
        assert len(result["forecast"]) == 7
        assert result["forecast"][0]["sunrise"] == "05:30"
        assert result["forecast"][0]["sunset"] == "20:15"


class TestWholeUK:
    """The UK-wide pseudo-council must be a first-class option, not a
    fallback into ``_default_data``."""

    def test_uk_all_is_in_councils_dict(self) -> None:
        region_keys = list(councils.keys())
        uk_region = next((r for r in region_keys if UK_ALL in councils[r]), None)
        assert uk_region is not None, "UK_ALL must be selectable from the sidebar"

    def test_uk_all_has_coords(self) -> None:
        # Weather + map widgets index into COORDS; missing here means the
        # whole-UK view crashes on those tabs.
        assert UK_ALL in COORDS
        lat, lon = COORDS[UK_ALL]
        # Rough sanity: UK centroid sits around 54N, 2W.
        assert 49 < lat < 60
        assert -8 < lon < 2

    def test_get_council_data_returns_rich_payload_for_uk_all(self) -> None:
        data = get_council_data(UK_ALL)
        # Must not fall through to ``_default_data`` — the "Data Coming
        # Soon" marker string only appears in that fallback.
        for issue in data["key_issues"]:
            assert "Data Coming Soon" not in issue.get("description", "")
        assert data["population"] > 60_000_000, "UK population sanity"
