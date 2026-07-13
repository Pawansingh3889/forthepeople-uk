"""Tests for the Ask tab's plumbing. All Claude API calls are mocked."""
from __future__ import annotations

from unittest import mock

import ask


class TestBuildContext:
    def test_contains_council_and_provenance(self) -> None:
        ctx = ask.build_context("Hull")
        assert "Hull" in ctx
        assert "provenance" in ctx
        assert "indicative_sample" in ctx
        assert "population" in ctx

    def test_schemes_are_summarised(self) -> None:
        ctx = ask.build_context("Leeds")
        assert "Universal Credit" in ctx


class TestAskClaude:
    def _resp(self, status=200, payload=None):
        m = mock.MagicMock()
        m.status_code = status
        m.json.return_value = payload or {"content": [{"type": "text", "text": "Answer here."}]}
        return m

    def test_happy_path_sends_grounded_request(self) -> None:
        with mock.patch("ask.requests.post", return_value=self._resp()) as post:
            out = ask.ask_claude("What is the council tax?", "Hull", "sk-test")
        assert out == {"answer": "Answer here."}
        _, kwargs = post.call_args
        assert kwargs["headers"]["x-api-key"] == "sk-test"
        assert kwargs["json"]["max_tokens"] == ask.MAX_ANSWER_TOKENS
        body_text = kwargs["json"]["messages"][0]["content"]
        assert "Hull" in body_text
        assert "provenance" in body_text

    def test_blank_question_never_hits_api(self) -> None:
        with mock.patch("ask.requests.post") as post:
            out = ask.ask_claude("   ", "Hull", "sk-test")
        post.assert_not_called()
        assert "error" in out

    def test_missing_key_never_hits_api(self) -> None:
        with mock.patch("ask.requests.post") as post:
            out = ask.ask_claude("A question", "Hull", "")
        post.assert_not_called()
        assert "error" in out

    def test_rejected_key(self) -> None:
        with mock.patch("ask.requests.post", return_value=self._resp(status=401)):
            out = ask.ask_claude("A question", "Hull", "sk-bad")
        assert "key" in out["error"].lower()

    def test_overloaded_api(self) -> None:
        with mock.patch("ask.requests.post", return_value=self._resp(status=529)):
            out = ask.ask_claude("A question", "Hull", "sk-test")
        assert "error" in out

    def test_network_failure(self) -> None:
        with mock.patch("ask.requests.post", side_effect=OSError("no network")):
            out = ask.ask_claude("A question", "Hull", "sk-test")
        assert "error" in out

    def test_question_is_truncated(self) -> None:
        long_question = "why " * 500  # far beyond MAX_QUESTION_CHARS
        with mock.patch("ask.requests.post", return_value=self._resp()) as post:
            ask.ask_claude(long_question, "Hull", "sk-test")
        body_text = post.call_args.kwargs["json"]["messages"][0]["content"]
        assert long_question.strip() not in body_text
        assert long_question.strip()[:ask.MAX_QUESTION_CHARS] in body_text


class TestKeywordFallback:
    def test_energy_query_finds_energy_schemes(self) -> None:
        results = ask.keyword_fallback("help with energy bills this winter")
        assert results
        blob = " ".join(f"{r['name']} {r['detail']}" for r in results).lower()
        assert "energy" in blob or "winter" in blob or "fuel" in blob

    def test_gibberish_returns_empty(self) -> None:
        assert ask.keyword_fallback("zzqxv") == []

    def test_stopwords_alone_return_empty(self) -> None:
        assert ask.keyword_fallback("what help with this") == []


class TestHourlyBudget:
    def test_counter_increments_and_reads_back(self) -> None:
        before = ask.hourly_used()
        ask.record_use()
        assert ask.hourly_used() == before + 1
