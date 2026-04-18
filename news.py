"""UK news fetcher — BBC News UK feed + gov.uk announcements.

Two public, feed-based sources that don't require an API key:

- BBC News UK — ``http://feeds.bbci.co.uk/news/uk/rss.xml`` — RSS 2.0.
  BBC content is BBC's rights, not under OGL. We display only
  headlines + links + publication time, which is the normal pattern
  for RSS aggregation. Attribution is explicit in the UI and in
  ``NOTICE``.
- gov.uk announcements — ``https://www.gov.uk/government/announcements.atom`` —
  Atom 1.0. Released under Open Government Licence v3.0; the NOTICE
  already covers the gov.uk chain.

Both fetches go through the existing 24-hour ``cached`` decorator so
a re-render doesn't hit the upstreams on every session.

Uses stdlib ``urllib`` + ``xml.etree.ElementTree`` — no new dependency.
Graceful on every failure mode: returns an empty list rather than
raising, so the UI degrades to "no items" instead of a stack trace.
"""
from __future__ import annotations

import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable

from cache import cached

REQUEST_TIMEOUT_SECONDS = 5
CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours — headlines age, but not in a dashboard


BBC_UK_FEED = "http://feeds.bbci.co.uk/news/uk/rss.xml"
GOV_UK_ANNOUNCEMENTS_FEED = "https://www.gov.uk/government/announcements.atom"

# Atom uses a default namespace; this maps the usual prefix to it so the
# ElementTree XPath expressions read normally.
_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass(frozen=True)
class NewsItem:
    """One displayable headline."""

    title: str
    link: str
    published: str  # ISO-ish string; the UI renders it as-is
    source: str  # "BBC News" | "gov.uk"


def _fetch(url: str) -> bytes | None:
    """Stdlib GET returning raw bytes; ``None`` on any failure."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "forthepeople-uk"})
        with urllib.request.urlopen(req, context=ctx, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return resp.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def _parse_rss(xml_bytes: bytes, source: str) -> list[NewsItem]:
    """Parse an RSS 2.0 document into NewsItems."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    items: list[NewsItem] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if title and link:
            items.append(NewsItem(title=title, link=link, published=pub, source=source))
    return items


def _parse_atom(xml_bytes: bytes, source: str) -> list[NewsItem]:
    """Parse an Atom 1.0 document into NewsItems."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    items: list[NewsItem] = []
    for entry in root.findall("atom:entry", _ATOM_NS):
        title_el = entry.find("atom:title", _ATOM_NS)
        title = (title_el.text or "").strip() if title_el is not None else ""
        link = ""
        link_el = entry.find("atom:link", _ATOM_NS)
        if link_el is not None:
            link = (link_el.get("href") or "").strip()
        pub_el = entry.find("atom:updated", _ATOM_NS) or entry.find("atom:published", _ATOM_NS)
        pub = (pub_el.text or "").strip() if pub_el is not None else ""
        if title and link:
            items.append(NewsItem(title=title, link=link, published=pub, source=source))
    return items


@cached(ttl=CACHE_TTL_SECONDS)
def get_bbc_uk(limit: int = 10) -> list[dict]:
    """Return up to ``limit`` BBC News UK headlines as plain dicts.

    Returned as dicts rather than dataclass instances so the cache
    decorator's JSON key-hashing and diskcache's pickled storage both
    round-trip cleanly.
    """
    xml_bytes = _fetch(BBC_UK_FEED)
    if xml_bytes is None:
        return []
    items = _parse_rss(xml_bytes, source="BBC News")
    return [_to_dict(i) for i in items[:limit]]


@cached(ttl=CACHE_TTL_SECONDS)
def get_gov_uk(limit: int = 10) -> list[dict]:
    """Return up to ``limit`` gov.uk announcements as plain dicts."""
    xml_bytes = _fetch(GOV_UK_ANNOUNCEMENTS_FEED)
    if xml_bytes is None:
        return []
    items = _parse_atom(xml_bytes, source="gov.uk")
    return [_to_dict(i) for i in items[:limit]]


def get_combined(limit_per_source: int = 8) -> list[dict]:
    """Return BBC and gov.uk items interleaved, with gov.uk first.

    gov.uk first because its items are OGL v3.0 (the NOTICE already
    covers them) and they tend to be the longest-dated, so they're a
    useful backstop when the BBC feed is empty or failing.
    """
    return [*get_gov_uk(limit_per_source), *get_bbc_uk(limit_per_source)]


def _to_dict(item: NewsItem) -> dict:
    return {
        "title": item.title,
        "link": item.link,
        "published": item.published,
        "source": item.source,
    }


# Convenience for callers that want the dataclass form.
def as_items(dicts: Iterable[dict]) -> list[NewsItem]:
    return [NewsItem(**d) for d in dicts]
