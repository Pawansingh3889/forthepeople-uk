"""Pytest fixtures shared across the test suite.

Provides a ``_clear_cache`` autouse fixture that empties ``cache._cache``
before every test. The ``@cached`` decorator persists results to a
diskcache directory across tests, which caused silent false positives:

- test A runs, its urlopen mock returns payload P, result cached
- test B runs with the same args but a *different* mock (e.g. URLError);
  the cache hit short-circuits the function, the mock never fires, and
  the assertion fails with a confusing "cached payload from test A"
  error.

Clearing between tests makes each test self-contained, which is what
the test file authors clearly expected.
"""
from __future__ import annotations

import pytest

try:
    import cache as _cache_mod
except ImportError:
    _cache_mod = None  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def _clear_cache():
    """Empty the module-level diskcache before and after every test."""
    if _cache_mod is not None and _cache_mod._cache is not None:
        _cache_mod._cache.clear()
    yield
    if _cache_mod is not None and _cache_mod._cache is not None:
        _cache_mod._cache.clear()
