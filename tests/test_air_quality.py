"""Tests for the live air quality source. The API is mocked."""
from __future__ import annotations

from unittest import mock

from data import get_air_quality
from sources import air_quality


def _resp(current):
    m = mock.MagicMock()
    m.json.return_value = {"current": current}
    return m


_GOOD = {"time": "2026-07-13T21:00", "european_aqi": 26, "pm2_5": 5.0,
         "pm10": 12.9, "nitrogen_dioxide": 2.4, "ozone": 66.0}


class TestAqiBand:
    def test_bands(self) -> None:
        assert air_quality.aqi_band(10) == "Good"
        assert air_quality.aqi_band(30) == "Fair"
        assert air_quality.aqi_band(50) == "Moderate"
        assert air_quality.aqi_band(70) == "Poor"
        assert air_quality.aqi_band(90) == "Very poor"
        assert air_quality.aqi_band(150) == "Extremely poor"
        assert air_quality.aqi_band(None) == "Unknown"


class TestFetch:
    def test_live_reading(self) -> None:
        with mock.patch("sources.air_quality.requests.get", return_value=_resp(_GOOD)):
            res = air_quality.fetch("Hull")
        assert res.live is True
        assert res.data["aqi"] == 26
        assert res.data["band"] == "Fair"
        assert res.data["pm2_5"] == 5.0
        assert res.asof == "2026-07-13T21:00"

    def test_missing_aqi_unavailable(self) -> None:
        with mock.patch("sources.air_quality.requests.get", return_value=_resp({"pm2_5": 5})):
            res = air_quality.fetch("Hull")
        assert res.live is False

    def test_network_failure(self) -> None:
        with mock.patch("sources.air_quality.requests.get", side_effect=OSError("down")):
            res = air_quality.fetch("Hull")
        assert res.live is False

    def test_uk_all_skipped(self) -> None:
        with mock.patch("sources.air_quality.requests.get") as mocked:
            res = air_quality.fetch("United Kingdom")
        mocked.assert_not_called()
        assert res.live is False

    def test_unknown_council_skipped(self) -> None:
        with mock.patch("sources.air_quality.requests.get") as mocked:
            res = air_quality.fetch("Atlantis")
        mocked.assert_not_called()
        assert res.live is False


class TestAdapter:
    def test_live_shape(self) -> None:
        with mock.patch("sources.air_quality.requests.get", return_value=_resp(_GOOD)):
            out = get_air_quality("Leeds")
        assert out["live"] is True
        assert out["band"] == "Fair"

    def test_fallback_shape(self) -> None:
        with mock.patch("sources.air_quality.requests.get", side_effect=OSError("x")):
            out = get_air_quality("Leeds")
        assert out == {"live": False}
