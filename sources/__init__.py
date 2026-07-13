"""Live open-data sources for ForThePeople UK.

One module per upstream API. Every fetcher returns a
:class:`sources.base.SourceResult` so callers get the payload and its
provenance (live or not, as-of date, source name and link) in one shape.
"""
