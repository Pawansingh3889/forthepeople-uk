"""Tests for the live petitions source. The API is mocked."""
from __future__ import annotations

from unittest import mock

from data import get_petitions
from sources import petitions


def _payload():
    return {"data": [
        {"id": 1, "attributes": {"action": "Small petition", "signature_count": 5_000,
                                 "government_response": None, "debate_threshold_reached_at": None}},
        {"id": 2, "attributes": {"action": "Big debated petition", "signature_count": 240_000,
                                 "government_response": {"summary": "..."},
                                 "debate_threshold_reached_at": "2026-05-01T00:00:00.000Z"}},
        {"id": 3, "attributes": {"action": "Responded petition", "signature_count": 25_000,
                                 "government_response": {"summary": "..."},
                                 "debate_threshold_reached_at": None}},
    ]}


def _resp(payload):
    m = mock.MagicMock()
    m.json.return_value = payload
    return m


class TestPetitionsFetch:
    def test_sorted_by_signatures_desc(self) -> None:
        with mock.patch("sources.petitions.requests.get", return_value=_resp(_payload())):
            result = petitions.fetch()
        assert result.live is True
        counts = [p["signatures"] for p in result.data]
        assert counts == sorted(counts, reverse=True)
        assert result.data[0]["action"] == "Big debated petition"

    def test_url_and_flags(self) -> None:
        with mock.patch("sources.petitions.requests.get", return_value=_resp(_payload())):
            result = petitions.fetch()
        top = result.data[0]
        assert top["url"] == "https://petition.parliament.uk/petitions/2"
        assert top["debated"] is True
        assert top["government_responded"] is True
        small = next(p for p in result.data if p["action"] == "Small petition")
        assert small["debated"] is False
        assert small["government_responded"] is False

    def test_limit_is_respected(self) -> None:
        with mock.patch("sources.petitions.requests.get", return_value=_resp(_payload())):
            result = petitions.fetch(limit=2)
        assert len(result.data) == 2

    def test_skips_malformed_entries(self) -> None:
        payload = {"data": [
            {"id": 9, "attributes": {"action": None, "signature_count": 100}},
            {"id": 10, "attributes": {"action": "Valid", "signature_count": 200}},
            {"id": 11, "attributes": {"action": "No count", "signature_count": None}},
        ]}
        with mock.patch("sources.petitions.requests.get", return_value=_resp(payload)):
            result = petitions.fetch()
        assert [p["action"] for p in result.data] == ["Valid"]

    def test_network_failure_unavailable(self) -> None:
        with mock.patch("sources.petitions.requests.get", side_effect=OSError("down")):
            result = petitions.fetch()
        assert result.live is False
        assert result.data is None

    def test_non_list_payload_unavailable(self) -> None:
        with mock.patch("sources.petitions.requests.get", return_value=_resp({"error": "x"})):
            result = petitions.fetch()
        assert result.live is False


class TestGetPetitionsAdapter:
    def test_live_shape(self) -> None:
        with mock.patch("sources.petitions.requests.get", return_value=_resp(_payload())):
            out = get_petitions()
        assert out["live"] is True
        assert len(out["petitions"]) == 3

    def test_fallback_shape(self) -> None:
        with mock.patch("sources.petitions.requests.get", side_effect=OSError("down")):
            out = get_petitions()
        assert out["live"] is False
        assert out["petitions"] == []
