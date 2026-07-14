"""Tests for the live UKHPI house-price source. All mocked."""
from __future__ import annotations

from unittest import mock

from data import get_housing
from sources import house_prices


def _resp(status=200, price=244_111, ref="2026-03", annual=2.2):
    m = mock.MagicMock()
    m.status_code = status
    m.json.return_value = {"result": {"primaryTopic": {
        "averagePrice": price, "percentageAnnualChange": annual, "refMonth": ref,
    }}}
    return m


class TestSlugDerivation:
    def test_plain_authority(self) -> None:
        assert house_prices._slug(mock.MagicMock(name="x", authority="Leeds")) == "leeds"

    def test_city_of_suffix_moves_to_front(self) -> None:
        entry = mock.MagicMock(authority="Kingston upon Hull, City of")
        entry.name = "Hull"
        assert house_prices._slug(entry) == "city-of-kingston-upon-hull"

    def test_commas_dropped(self) -> None:
        entry = mock.MagicMock(authority="Bournemouth, Christchurch and Poole")
        entry.name = "Bournemouth"
        assert house_prices._slug(entry) == "bournemouth-christchurch-and-poole"

    def test_westminster_override(self) -> None:
        entry = mock.MagicMock(authority="Westminster")
        entry.name = "Westminster"
        assert house_prices._slug(entry) == "city-of-westminster"

    def test_ons_name_beats_council_branding(self) -> None:
        # UKHPI slugs follow the ONS area name ("York"), not the council's
        # branded name ("City of York"). Both verified against the live API.
        entry = mock.MagicMock(authority="City of York")
        entry.name = "York"
        assert house_prices._slug(entry) == "york"
        entry = mock.MagicMock(authority="City of Lincoln")
        entry.name = "Lincoln"
        assert house_prices._slug(entry) == "lincoln"


class TestHousePricesFetch:
    def test_live_path_includes_uk_comparison(self) -> None:
        def route(url, **kwargs):
            if "united-kingdom" in url:
                return _resp(price=289_000)
            return _resp(price=244_111)

        with mock.patch("sources.house_prices.requests.get", side_effect=route):
            result = house_prices.fetch("Leeds")
        assert result.live is True
        assert result.data["avg_price"] == 244_111
        assert result.data["vs_uk"] == 244_111 - 289_000
        assert result.asof == "2026-03"

    def test_walks_back_past_unpublished_months(self) -> None:
        calls = []

        def route(url, **kwargs):
            calls.append(url)
            if "united-kingdom" in url:
                return _resp(price=289_000)
            if len([c for c in calls if "united-kingdom" not in c]) == 1:
                return _resp(status=404)  # newest month not published yet
            return _resp(price=200_000)

        with mock.patch("sources.house_prices.requests.get", side_effect=route):
            result = house_prices.fetch("Leeds")
        assert result.live is True
        assert result.data["avg_price"] == 200_000

    def test_linked_data_refmonth_dict_form(self) -> None:
        m = mock.MagicMock()
        m.status_code = 200
        m.json.return_value = {"result": {"primaryTopic": {
            "averagePrice": 150_000, "refMonth": {"_value": "2026-02"},
        }}}

        def route(url, **kwargs):
            return m

        with mock.patch("sources.house_prices.requests.get", side_effect=route):
            result = house_prices.fetch("Hull")
        assert result.live is True
        assert result.data["month"] == "2026-02"

    def test_unknown_region_missing_endpoint_is_unavailable(self) -> None:
        # UKHPI answers 200 with primaryTopic "elda:missingEndpoint" for a
        # slug it does not know; that must read as unavailable, not crash.
        m = mock.MagicMock()
        m.status_code = 200
        m.json.return_value = {"result": {"primaryTopic": "elda:missingEndpoint"}}
        with mock.patch("sources.house_prices.requests.get", return_value=m):
            result = house_prices.fetch("Leeds")
        assert result.live is False

    def test_all_months_missing_is_unavailable(self) -> None:
        with mock.patch("sources.house_prices.requests.get", return_value=_resp(status=404)):
            result = house_prices.fetch("Leeds")
        assert result.live is False

    def test_network_failure_is_unavailable(self) -> None:
        with mock.patch("sources.house_prices.requests.get", side_effect=OSError("no network")):
            result = house_prices.fetch("Leeds")
        assert result.live is False


class TestGetHousingAdapter:
    def test_live_overlays_price_keeps_sample_fields(self) -> None:
        def route(url, **kwargs):
            return _resp(price=134_685) if "hull" in url else _resp(price=289_000)

        with mock.patch("sources.house_prices.requests.get", side_effect=route):
            out = get_housing("Hull")
        assert out["live"] is True
        assert out["avg_price"] == 134_685
        assert "waiting_list" in out  # indicative field still supplied

    def test_fallback_keeps_legacy_shape(self) -> None:
        with mock.patch("sources.house_prices.requests.get", side_effect=OSError("down")):
            out = get_housing("Hull")
        assert out["live"] is False
        assert out["avg_price"] == 145_000  # indicative HOUSING figure
