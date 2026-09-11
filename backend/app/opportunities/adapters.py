"""Opportunity search adapters (provider-neutral, swappable via settings).

LAWFUL-USE POLICY for every current and future adapter in this module:
any adapter that touches the live web MUST respect robots.txt, the target
site's Terms of Service, and polite rate limits (identify the client, back
off on 429/503, cache results). Prefer official/partner APIs over scraping.
The mock adapter serves the bundled demo corpus and never touches the network.

Selection: `get_adapter()` reads `settings.search_provider` ("mock" default).
"""

from __future__ import annotations

import copy
from typing import Protocol

from app.config import settings


class SearchAdapter(Protocol):
    """A source of opportunity dicts shaped like the seeded rows
    (see app.db.seeds.opportunities.OPPORTUNITIES)."""

    def search(self, query: str, kinds: list[str] | None) -> list[dict]: ...


class MockSearchAdapter:
    """Deterministic, offline adapter over the seeded demo corpus.

    `query` is matched case-insensitively against title, org, description and
    skills; `kinds` filters on the opportunity `type` (case-insensitive).
    Returns deep copies so callers can never mutate the seed data.
    """

    name = "mock"

    def search(self, query: str, kinds: list[str] | None = None) -> list[dict]:
        # Imported lazily so a partially-built seeds tree never breaks import.
        from app.db.seeds.opportunities import OPPORTUNITIES

        needle = (query or "").strip().lower()
        wanted = {k.strip().lower() for k in kinds or [] if k and k.strip()}
        results: list[dict] = []
        for spec in OPPORTUNITIES:
            if wanted and spec["type"].lower() not in wanted:
                continue
            if needle:
                haystack = " ".join(
                    [spec["title"], spec["org"], spec["description"], *spec["skills"]]
                ).lower()
                if needle not in haystack:
                    continue
            results.append(copy.deepcopy(spec))
        return results


class WebSearchAdapter:
    """Documented stub for a future live web-search adapter. NOT implemented.

    A real implementation MUST, before fetching anything:
    - check and obey robots.txt for every host it touches;
    - comply with each source site's Terms of Service (many opportunity
      boards forbid scraping — use their official APIs or licensed feeds);
    - rate-limit itself (per-host delays, exponential backoff on 429/5xx)
      and send an honest User-Agent;
    - store only what the source permits, with attribution via source_url,
      and mark unverified listings verified=False.
    """

    name = "web"

    def search(self, query: str, kinds: list[str] | None = None) -> list[dict]:
        raise NotImplementedError(
            "WebSearchAdapter is a stub: live opportunity search is not implemented. "
            "Set SEARCH_PROVIDER=mock, or implement this adapter against an official "
            "API while respecting robots.txt, the source's Terms of Service, and "
            "polite rate limits."
        )


def get_adapter() -> SearchAdapter:
    """Return the adapter selected by settings.search_provider (unknown → mock)."""
    if settings.search_provider.strip().lower() == "web":
        return WebSearchAdapter()
    return MockSearchAdapter()
