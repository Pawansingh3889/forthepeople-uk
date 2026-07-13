"""Tests for the live MPs source (UK Parliament Members API).

All mocked — the constituency search is substring-based upstream, so the
word-boundary filter is the load-bearing part: "Hull" must keep Kingston
upon Hull and drop Solihull.
"""
from __future__ import annotations

from unittest import mock

from data import get_mp_data
from sources import mps


def _search_payload():
    """Realistic search response for "Hull", Solihull pollution included."""
    def constituency(cid, name, member_id, member_name, party):
        return {"value": {
            "id": cid, "name": name,
            "currentRepresentation": {"member": {"value": {
                "id": member_id, "nameDisplayAs": member_name,
                "latestParty": {"name": party},
            }}},
        }}
    return {"items": [
        constituency(3910, "Birmingham Hodge Hill and Solihull North", 1171, "Liam Byrne", "Labour"),
        constituency(4128, "Kingston upon Hull East", 4030, "Karl Turner", "Independent"),
        constituency(4129, "Kingston upon Hull North and Cottingham", 1533, "Dame Diana Johnson", "Labour"),
        constituency(4130, "Kingston upon Hull West and Haltemprice", 4645, "Emma Hardy", "Labour"),
        constituency(4294, "Solihull West and Shirley", 5197, "Dr Neil Shastri-Hurst", "Conservative"),
    ]}


def _route(search_payload, majority=3920):
    def route(url, *args, **kwargs):
        m = mock.MagicMock()
        if "LatestElectionResult" in url:
            m.json.return_value = {"value": {"majority": majority}}
        else:
            m.json.return_value = search_payload
        return m
    return route


class TestMpsFetch:
    def test_word_boundary_filter_drops_solihull(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=_route(_search_payload())):
            result = mps.fetch("Hull")
        assert result.live is True
        names = [m["constituency"] for m in result.data]
        assert all("Kingston upon Hull" in n for n in names)
        assert len(names) == 3
        assert not any("Solihull" in n for n in names)

    def test_entries_carry_party_majority_and_live_flag(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=_route(_search_payload())):
            result = mps.fetch("Hull")
        east = next(m for m in result.data if m["constituency"] == "Kingston upon Hull East")
        assert east["name"] == "Karl Turner"
        assert east["party"] == "Independent"
        assert east["majority"] == 3920
        assert east["live"] is True

    def test_vacant_seat_skipped(self) -> None:
        payload = _search_payload()
        payload["items"][1]["value"]["currentRepresentation"] = None
        with mock.patch("sources.mps.requests.get", side_effect=_route(payload)):
            result = mps.fetch("Hull")
        assert result.live is True
        assert len(result.data) == 2

    def test_no_matches_is_unavailable(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=_route({"items": []})):
            result = mps.fetch("Hull")
        assert result.live is False
        assert result.data is None

    def test_network_failure_is_unavailable(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=OSError("no network")):
            result = mps.fetch("Hull")
        assert result.live is False

    def test_uk_all_never_hits_api(self) -> None:
        with mock.patch("sources.mps.requests.get") as mocked:
            result = mps.fetch("United Kingdom")
        mocked.assert_not_called()
        assert result.live is False


class TestGetMpDataAdapter:
    def test_live_result_passes_through(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=_route(_search_payload())):
            result = get_mp_data("Hull")
        assert all(m.get("live") for m in result)

    def test_fallback_to_static_table(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=OSError("down")):
            result = get_mp_data("Hull")
        assert result[0]["name"] == "Karl Turner"
        assert not result[0].get("live")

    def test_fallback_pointer_for_unknown_council(self) -> None:
        with mock.patch("sources.mps.requests.get", side_effect=OSError("down")):
            result = get_mp_data("Atlantis")
        assert result[0]["name"] == "Check gov.uk"
