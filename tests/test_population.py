"""Tests for the live ONS/Nomis population source. All mocked."""
from __future__ import annotations

from unittest import mock

from data import get_population
from sources import population


def _resp(obs):
    m = mock.MagicMock()
    m.json.return_value = {"obs": obs}
    return m


def _leeds_obs(value=845_189, year=2024):
    return [{"obs_value": {"value": value}, "time": {"value": year},
             "geography": {"description": "Leeds"}}]


class TestPopulationFetch:
    def test_live_path(self) -> None:
        with mock.patch("sources.population.requests.get", return_value=_resp(_leeds_obs())):
            result = population.fetch("Leeds")
        assert result.live is True
        assert result.data == {"population": 845_189, "year": "2024"}

    def test_recoded_authority_retries_old_gss(self) -> None:
        # Sheffield's current code returns nothing on stale Nomis vintages;
        # the fetch must retry the pre-recode code.
        calls = []

        def route(url, params=None, **kwargs):
            calls.append(params["geography"])
            return _resp(_leeds_obs(556_500) if params["geography"] == "E08000019" else [])

        with mock.patch("sources.population.requests.get", side_effect=route):
            result = population.fetch("Sheffield")
        assert calls == ["E08000039", "E08000019"]
        assert result.live is True
        assert result.data["population"] == 556_500

    def test_no_observations_anywhere_is_unavailable(self) -> None:
        with mock.patch("sources.population.requests.get", return_value=_resp([])):
            result = population.fetch("Leeds")
        assert result.live is False

    def test_network_failure_is_unavailable(self) -> None:
        with mock.patch("sources.population.requests.get", side_effect=OSError("no network")):
            result = population.fetch("Leeds")
        assert result.live is False

    def test_unknown_council_never_hits_api(self) -> None:
        with mock.patch("sources.population.requests.get") as mocked:
            result = population.fetch("Atlantis")
        mocked.assert_not_called()
        assert result.live is False


class TestGetPopulationAdapter:
    def test_live_passes_through(self) -> None:
        with mock.patch("sources.population.requests.get", return_value=_resp(_leeds_obs())):
            out = get_population("Leeds")
        assert out == {"population": 845_189, "year": "2024", "live": True}

    def test_fallback_uses_indicative_figure(self) -> None:
        with mock.patch("sources.population.requests.get", side_effect=OSError("down")):
            out = get_population("Leeds")
        assert out["live"] is False
        assert out["population"] == 812_000  # indicative COUNCIL_DATA figure
