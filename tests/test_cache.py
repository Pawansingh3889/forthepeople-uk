"""Regression tests for the caching layer.

The important one: every module in sources/ exposes a function named
``fetch``, so cache keys must include the module. Keying on the bare
function name let ``population.fetch("Hull")`` poison the cache entry that
``crime.fetch("Hull")`` and ``house_prices.fetch("Hull")`` then read back,
which surfaced as a KeyError('avg_price') in get_housing the first time one
test exercised several sources for the same council. This test mocks the
HTTP layer, so it catches the collision with or without network.
"""
from __future__ import annotations

from unittest import mock

from sources import crime, population


def _population_resp():
    m = mock.MagicMock()
    m.json.return_value = {"obs": [{"obs_value": {"value": 267_000},
                                    "time": {"value": 2024}}]}
    return m


def _crime_route(url, *args, **kwargs):
    m = mock.MagicMock()
    if "crime-last-updated" in url:
        m.json.return_value = {"date": "2026-05"}
    else:
        m.json.return_value = [{"category": "burglary"}]
    return m


class TestUnavailableResultsAreNotCached:
    def test_fallback_is_retried_next_call(self) -> None:
        # First call fails (network down), second succeeds. Without cache_if
        # the failure would be pinned for the whole TTL.
        with mock.patch("sources.population.requests.get", side_effect=OSError("down")):
            first = population.fetch("Hull")
        assert first.live is False
        with mock.patch("sources.population.requests.get", return_value=_population_resp()):
            second = population.fetch("Hull")
        assert second.live is True
        assert second.data["population"] == 267_000

    def test_live_result_is_cached(self) -> None:
        with mock.patch("sources.population.requests.get", return_value=_population_resp()) as m:
            population.fetch("Hull")
            population.fetch("Hull")
        assert m.call_count == 1  # second call served from cache


class TestSameNamedFetchersDoNotShareCacheEntries:
    def test_population_then_crime_for_same_council(self) -> None:
        with mock.patch("sources.population.requests.get", return_value=_population_resp()):
            pop = population.fetch("Hull")
        assert pop.data["population"] == 267_000

        with mock.patch("sources.crime.requests.get", side_effect=_crime_route):
            crime_result = crime.fetch("Hull")

        # Before the module-qualified cache key, this came back as the
        # cached population payload.
        assert crime_result.source == "Police UK"
        assert "total" in crime_result.data
        assert "population" not in crime_result.data
