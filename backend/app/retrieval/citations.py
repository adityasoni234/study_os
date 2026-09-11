"""Turn retrieval hits into user-facing citations.

Other services depend on EXACTLY this import and signature (do not change):

    from app.retrieval.citations import build_citations
    citations = build_citations(hits, db=db)

One Citation per distinct source — the source's best (highest-scoring) hit
supplies page and snippet. Chunk ids and embeddings never leave this layer.
"""

from __future__ import annotations

from app.retrieval.types import ChunkHit, Citation

SNIPPET_CHARS = 220


def build_citations(hits: list[ChunkHit], db=None) -> list[Citation]:
    """Citations for a hit list, best sources first. ``db`` (optional
    SQLAlchemy session) resolves each Source's url; without it url is None."""
    best_per_source: dict[str, ChunkHit] = {}
    for hit in sorted(hits, key=lambda h: h.score, reverse=True):
        best_per_source.setdefault(hit.source_id, hit)

    citations: list[Citation] = []
    for source_id, hit in best_per_source.items():
        citations.append(
            Citation(
                source_id=source_id,
                title=hit.source_title,
                page=hit.page,
                snippet=_snippet(hit.text),
                url=_source_url(db, source_id),
            )
        )
    return citations


def _snippet(text: str, limit: int = SNIPPET_CHARS) -> str:
    """First ~limit chars of the hit text, whitespace-collapsed, cut at a word."""
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    cut = clean.rfind(" ", 0, limit)
    return clean[: cut if cut > 0 else limit].rstrip(",;:") + "…"


def _source_url(db, source_id: str) -> str | None:
    if db is None:
        return None
    from app.models.notebook import Source  # local import keeps layering light

    source = db.get(Source, source_id)
    return source.url if source is not None else None
