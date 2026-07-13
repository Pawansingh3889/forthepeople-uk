"""Shared result envelope for live data sources.

Every fetcher in this package returns a SourceResult. ``data`` carries the
payload in whatever shape the UI tab expects; the other fields say where it
came from and how fresh it is, so provenance captions render the same way
for every source.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceResult:
    data: Any            # payload, or None when the source is unavailable
    live: bool           # True = fetched from the upstream API this call (or cache of it)
    asof: str | None     # month/date the data describes, if the API says
    source: str          # human-readable source name, e.g. "Police UK"
    url: str             # official link for users to verify against

    def caption(self) -> str:
        """One-line provenance text for the UI."""
        if self.live:
            return f"Live from {self.source}" + (f" · {self.asof}" if self.asof else "")
        return "Indicative sample data"
