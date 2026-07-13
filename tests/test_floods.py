"""Tests for the live flood-warnings source. The API is mocked.

The load-bearing distinction: an empty items array is a real answer (checked,
none active) and must come back live with an empty list, not as unavailable.
"""
from __future__ import annotations

from unittest import mock

from data import get_floods
from sources import floods


def _resp(items):
    m = mock.MagicMock()
    m.json.return_value = {"items": items}
    return m


_WARNINGS = [
    {"severity": "Flood alert", "severityLevel": 3, "description": "River Hull",
     "floodArea": {"riverOrSea": "River Hull"}, "message": "Be prepared", "timeRaised": "2026-07-13T06:00"},
    {"severity": "Severe flood warning", "severityLevel": 1, "description": "Humber bank",
     "floodArea": {"riverOrSea": "Humber"}, "message": "Danger to life", "timeRaised": "2026-07-13T05:00"},
]


class TestFetch:
    def test_empty_is_live_not_unavailable(self) -> None:
        with mock.patch("sources.floods.requests.get", return_value=_resp([])):
            res = floods.fetch("Hull")
        assert res.live is True
        assert res.data == []

    def test_warnings_sorted_by_severity(self) -> None:
        with mock.patch("sources.floods.requests.get", return_value=_resp(_WARNINGS)):
            res = floods.fetch("Hull")
        assert res.live is True
        # severest first: level 1 before level 3
        assert [w["level"] for w in res.data] == [1, 3]
        assert res.data[0]["severity"] == "Severe flood warning"
        assert res.data[0]["river_or_sea"] == "Humber"

    def test_severity_label_filled_from_level(self) -> None:
        items = [{"severityLevel": 2, "description": "X", "floodArea": {}}]
        with mock.patch("sources.floods.requests.get", return_value=_resp(items)):
            res = floods.fetch("Hull")
        assert res.data[0]["severity"] == "Flood warning"

    def test_network_failure_unavailable(self) -> None:
        with mock.patch("sources.floods.requests.get", side_effect=OSError("down")):
            res = floods.fetch("Hull")
        assert res.live is False
        assert res.data is None

    def test_non_list_unavailable(self) -> None:
        with mock.patch("sources.floods.requests.get", return_value=_resp(None)):
            res = floods.fetch("Hull")
        assert res.live is False

    def test_uk_all_skipped(self) -> None:
        with mock.patch("sources.floods.requests.get") as mocked:
            res = floods.fetch("United Kingdom")
        mocked.assert_not_called()
        assert res.live is False


class TestAdapter:
    def test_none_active(self) -> None:
        with mock.patch("sources.floods.requests.get", return_value=_resp([])):
            out = get_floods("Hull")
        assert out == {"warnings": [], "live": True}

    def test_unavailable(self) -> None:
        with mock.patch("sources.floods.requests.get", side_effect=OSError("x")):
            out = get_floods("Hull")
        assert out == {"warnings": None, "live": False}
