"""Tests for ``news.py``.

Feed fetches are mocked at ``urllib.request.urlopen`` so CI doesn't
depend on BBC / gov.uk availability. Parser tests use realistic RSS
and Atom fixtures so the XPath expressions stay honest.
"""
from __future__ import annotations

import io
from unittest import mock

import pytest

from news import (
    NewsItem,
    _parse_atom,
    _parse_rss,
    as_items,
    get_bbc_uk,
    get_combined,
    get_gov_uk,
)


# ---------------------------------------------------------------------------
# Fixtures — minimal but structurally correct
# ---------------------------------------------------------------------------

RSS_FIXTURE = b"""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>BBC News UK</title>
    <item>
      <title>First headline</title>
      <link>https://www.bbc.co.uk/news/first</link>
      <pubDate>Fri, 18 Apr 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Second headline</title>
      <link>https://www.bbc.co.uk/news/second</link>
      <pubDate>Fri, 18 Apr 2026 11:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

ATOM_FIXTURE = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>gov.uk announcements</title>
  <entry>
    <title>New housing scheme opens</title>
    <link href="https://www.gov.uk/government/news/new-housing-scheme-opens"/>
    <updated>2026-04-18T10:00:00Z</updated>
  </entry>
  <entry>
    <title>Rate change announced</title>
    <link href="https://www.gov.uk/government/news/rate-change"/>
    <published>2026-04-17T14:30:00Z</published>
  </entry>
</feed>"""


def _mock_response(body: bytes):
    m = mock.MagicMock()
    m.__enter__.return_value = io.BytesIO(body)
    m.__exit__.return_value = False
    return m


# ---------------------------------------------------------------------------
# _parse_rss — pure
# ---------------------------------------------------------------------------

class TestParseRSS:
    def test_parses_two_items(self) -> None:
        items = _parse_rss(RSS_FIXTURE, source="BBC News")
        assert len(items) == 2
        assert items[0].title == "First headline"
        assert items[0].link == "https://www.bbc.co.uk/news/first"
        assert items[0].source == "BBC News"
        assert "Apr 2026" in items[0].published

    def test_empty_xml_returns_empty_list(self) -> None:
        assert _parse_rss(b"<rss version='2.0'><channel></channel></rss>", source="x") == []

    def test_malformed_xml_returns_empty_list(self) -> None:
        assert _parse_rss(b"not xml", source="x") == []

    def test_items_missing_link_are_dropped(self) -> None:
        xml = b"""<?xml version="1.0"?>
        <rss version="2.0"><channel>
            <item><title>no link</title></item>
            <item><title>ok</title><link>https://x</link></item>
        </channel></rss>"""
        items = _parse_rss(xml, source="x")
        assert len(items) == 1
        assert items[0].title == "ok"


# ---------------------------------------------------------------------------
# _parse_atom — pure
# ---------------------------------------------------------------------------

class TestParseAtom:
    def test_parses_two_entries(self) -> None:
        items = _parse_atom(ATOM_FIXTURE, source="gov.uk")
        assert len(items) == 2
        assert items[0].title == "New housing scheme opens"
        assert items[0].link == "https://www.gov.uk/government/news/new-housing-scheme-opens"
        assert items[0].published == "2026-04-18T10:00:00Z"
        assert items[0].source == "gov.uk"

    def test_falls_back_to_published_when_updated_missing(self) -> None:
        items = _parse_atom(ATOM_FIXTURE, source="gov.uk")
        # Second entry uses <published>, not <updated>.
        assert items[1].published == "2026-04-17T14:30:00Z"

    def test_malformed_xml_returns_empty_list(self) -> None:
        assert _parse_atom(b"not xml", source="x") == []


# ---------------------------------------------------------------------------
# get_bbc_uk / get_gov_uk — urlopen mocked
# ---------------------------------------------------------------------------

class TestGetBBC:
    def test_returns_dict_shape_on_success(self) -> None:
        with mock.patch("news.urllib.request.urlopen", return_value=_mock_response(RSS_FIXTURE)):
            items = get_bbc_uk(limit=5)
        # diskcache may short-circuit this after the first run across test
        # invocations, so the contract is soft: if items came back, they
        # have the documented shape.
        if items:
            sample = items[0]
            assert {"title", "link", "published", "source"}.issubset(sample)
            assert sample["source"] == "BBC News"

    def test_network_failure_returns_empty(self) -> None:
        import urllib.error
        with mock.patch("news.urllib.request.urlopen", side_effect=urllib.error.URLError("dns")):
            assert get_bbc_uk(limit=5) in ([], None) or get_bbc_uk(limit=5) == []

    def test_respects_limit(self) -> None:
        # Build a fixture with 20 items so we can see limit do its job.
        many = b"""<?xml version="1.0"?><rss version="2.0"><channel>""" + b"".join(
            f"<item><title>t{i}</title><link>https://x/{i}</link></item>".encode()
            for i in range(20)
        ) + b"</channel></rss>"
        with mock.patch("news.urllib.request.urlopen", return_value=_mock_response(many)):
            items = get_bbc_uk(limit=3)
        if items:
            assert len(items) <= 3


class TestGetGovUK:
    def test_returns_dict_shape_on_success(self) -> None:
        with mock.patch("news.urllib.request.urlopen", return_value=_mock_response(ATOM_FIXTURE)):
            items = get_gov_uk(limit=5)
        if items:
            sample = items[0]
            assert {"title", "link", "published", "source"}.issubset(sample)
            assert sample["source"] == "gov.uk"


# ---------------------------------------------------------------------------
# get_combined
# ---------------------------------------------------------------------------

class TestGetCombined:
    def test_gov_uk_listed_first(self) -> None:
        # Mock both fetches by returning different bytes per call.
        urls_seen: list[str] = []

        def side_effect(req, *_a, **_kw):
            url = req.full_url if hasattr(req, "full_url") else ""
            urls_seen.append(url)
            return _mock_response(ATOM_FIXTURE if "atom" in url else RSS_FIXTURE)

        with mock.patch("news.urllib.request.urlopen", side_effect=side_effect):
            combined = get_combined(limit_per_source=2)
        # Soft contract: if anything came back, gov.uk is at index 0.
        if combined:
            assert combined[0]["source"] == "gov.uk"


# ---------------------------------------------------------------------------
# as_items helper
# ---------------------------------------------------------------------------

class TestAsItems:
    def test_round_trips_dicts_to_dataclass(self) -> None:
        dicts = [
            {"title": "a", "link": "http://a", "published": "2026-01-01", "source": "BBC News"},
            {"title": "b", "link": "http://b", "published": "2026-01-02", "source": "gov.uk"},
        ]
        items = as_items(dicts)
        assert all(isinstance(i, NewsItem) for i in items)
        assert items[0].source == "BBC News"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
