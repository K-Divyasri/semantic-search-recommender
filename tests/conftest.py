"""Shared fixtures. Everything runs offline -- no key, no downloads (just numpy)."""

from __future__ import annotations

import pytest

from recsys.index import SearchIndex


@pytest.fixture(scope="session")
def index() -> SearchIndex:
    """One built index for the whole test session (the catalog is deterministic)."""
    return SearchIndex.from_catalog()
