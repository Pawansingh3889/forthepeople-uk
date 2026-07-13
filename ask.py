"""Plain-English questions over the dashboard's own data, answered by Claude.

The Ask tab works in three modes, checked in this order:

1. Operator key: ``ANTHROPIC_API_KEY`` set in the environment (a Hugging
   Face Space secret or Render env var). Session and hourly rate limits
   apply because the operator pays per question.
2. Visitor key: pasted into the tab, held in Streamlit session state only,
   never stored server-side.
3. No key: a keyword search over the schemes and services tables, so the
   tab still helps without any AI and the app keeps working with no keys.

Answers are grounded: the model receives this dashboard's data for the
selected council with each block labelled live or indicative, and is
instructed to say which kind backs every figure, to signpost rather than
advise, and to stay on UK public services.
"""
from __future__ import annotations

import json
import os

import requests

import cache
from data import (
    get_council_data,
    get_crime_stats,
    get_essential_services,
    get_housing,
    get_mp_data,
    get_population,
    get_schemes,
    get_schools,
)

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

MAX_QUESTION_CHARS = 400
MAX_ANSWER_TOKENS = 600
SESSION_LIMIT = 10   # questions per browser session (operator-key mode)
HOURLY_LIMIT = 60    # questions per hour across all visitors (operator-key mode)

SYSTEM_PROMPT = """You answer questions from UK residents about public services, using the dashboard data provided in the user message.

Rules:
- Ground every figure in the provided data. Each block is labelled live (fetched from an official API) or indicative (sample data for demonstration). Say which kind backs each figure, for example "(live Police UK figure for 2026-05)" or "(indicative sample figure - check the linked official source)".
- If the data does not cover the question, say so plainly and point to the right official source: gov.uk, ONS, NHS, Police UK, or the council's own site.
- General information only. Never assess an individual's eligibility for benefits, their immigration status, or their legal position. Point to the gov.uk benefits checker, Citizens Advice, or a regulated adviser instead.
- Plain English, UK context, short: a brief paragraph or a few bullet points.
- Only answer questions about UK public services, government, and this dashboard. For anything else, reply in one sentence that this tab only covers UK public services."""

# Common words that would otherwise match almost every scheme description.
_STOPWORDS = {
    "with", "this", "that", "what", "when", "where", "which", "help",
    "much", "have", "does", "need", "there", "about", "from", "will",
}


def build_context(council: str) -> str:
    """Compact JSON snapshot of the dashboard's data for one council.

    Provenance labels ride along so the model can caption figures honestly.
    """
    schemes = {
        category: [f"{s['name']} - {s.get('who', '')} ({s.get('amount', '')})" for s in entries]
        for category, entries in get_schemes().items()
    }
    snapshot = {
        "council": council,
        "provenance": {
            "always_live": ["weather", "news", "postcode lookup"],
            "flagged_blocks": "crime, mps, population and housing each carry their own "
                              "live flag; live=false means indicative sample data",
            "indicative_sample": ["finance", "education", "health", "transport",
                                  "environment", "overview details"],
        },
        "overview_indicative": get_council_data(council),
        "population": get_population(council),
        "crime": get_crime_stats(council),
        "mps": get_mp_data(council),
        "housing": get_housing(council),
        "schools_indicative": get_schools(council),
        "schemes": schemes,
        "essential_services": get_essential_services(),
    }
    return json.dumps(snapshot, separators=(",", ":"), default=str)


def ask_claude(question: str, council: str, api_key: str) -> dict:
    """One grounded question to the Claude API. Returns {"answer"} or {"error"}."""
    question = (question or "").strip()[:MAX_QUESTION_CHARS]
    if not question:
        return {"error": "Type a question first."}
    if not api_key:
        return {"error": "No API key configured."}
    body = {
        "model": DEFAULT_MODEL,
        "max_tokens": MAX_ANSWER_TOKENS,
        "system": SYSTEM_PROMPT,
        "messages": [{
            "role": "user",
            "content": (
                f"Selected council: {council}\n"
                f"Dashboard data (JSON, with provenance labels):\n{build_context(council)}\n\n"
                f"Question: {question}"
            ),
        }],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": API_VERSION,
        "content-type": "application/json",
    }
    try:
        r = requests.post(API_URL, headers=headers, json=body, timeout=30)
    except Exception as e:
        return {"error": f"Could not reach the Claude API: {e}"}
    if r.status_code in (401, 403):
        return {"error": "The API key was rejected. Check it in the Anthropic console."}
    if r.status_code == 429:
        return {"error": "The API rate limit was hit. Wait a minute and try again."}
    if r.status_code >= 500:
        return {"error": "The Claude API is overloaded right now. Try again shortly."}
    if r.status_code != 200:
        return {"error": f"Unexpected API response (HTTP {r.status_code})."}
    try:
        blocks = r.json().get("content", [])
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    except Exception:
        text = ""
    if not text:
        return {"error": "The API returned no answer text."}
    return {"answer": text}


def keyword_fallback(question: str) -> list[dict]:
    """No-key mode: rank schemes and services by keyword overlap."""
    words = {w.lower().strip(".,?!'\"") for w in (question or "").split()}
    words = {w for w in words if len(w) > 3 and w not in _STOPWORDS}
    if not words:
        return []
    hits: list[tuple[int, dict]] = []
    for category, schemes in get_schemes().items():
        for s in schemes:
            hay = f"{s.get('name', '')} {s.get('who', '')} {s.get('category', '')} {category}".lower()
            score = sum(1 for w in words if w in hay)
            if score:
                hits.append((score, {"name": s["name"], "detail": s.get("who", ""),
                                     "link": s.get("link", "")}))
    for group, services in get_essential_services().items():
        for s in services:
            hay = f"{s.get('name', '')} {s.get('for', '')} {group}".lower()
            score = sum(1 for w in words if w in hay)
            if score:
                hits.append((score, {"name": s["name"], "detail": s.get("for", ""),
                                     "link": s.get("url", "")}))
    hits.sort(key=lambda t: -t[0])
    return [h for _, h in hits[:6]]


def hourly_used() -> int:
    """Questions asked on the operator key in the current hour window."""
    if cache._cache is None:
        return 0
    return int(cache._cache.get("ask_hourly", 0))


def record_use() -> None:
    if cache._cache is None:
        return
    cache._cache.set("ask_hourly", hourly_used() + 1, expire=3600)
