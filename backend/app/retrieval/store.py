"""Vector search over SourceChunk rows — the single retrieval entry point.

Other services depend on EXACTLY this import and signature (do not change):

    from app.retrieval.store import search_chunks
    hits = search_chunks(db, user_id, query, k=4, notebook_id=None)

Behaviour: resolves the user's notebook(s) (default: all of them), lazily
embeds-and-persists any chunks with NULL embeddings in one batch, embeds the
query, then ranks by cosine similarity — native pgvector SQL on Postgres
(python fallback on any failure), pure-python cosine on SQLite (no numpy).
"""

from __future__ import annotations

import logging
import math

from sqlalchemy import select
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.models.notebook import Notebook, Source, SourceChunk
from app.retrieval.embeddings import get_embedding_provider
from app.retrieval.types import ChunkHit

_log = logging.getLogger("studyos.retrieval")

# Sanity floor applied inside search_chunks: obviously-irrelevant hits are
# dropped. Mock scores are kept as-is (top-k always returned, scores exposed)
# so callers can gate "grounded" themselves via top_score()/grounded_floor().
_SCORE_FLOOR: dict[str, float] = {"mock": -1.0, "openai": 0.05}

# Minimum top score for an answer to count as grounded in the user's sources.
# Mock (hashed bag-of-words): related questions score ~0.3-0.9, unrelated ones
# ~0.0-0.08 on the seeded corpus — 0.18 splits them with wide margins.
# OpenAI text-embedding-3: related Q↔passage cosine is typically ≥0.35,
# unrelated ~0.0-0.2 — 0.25 is a conservative split.
_GROUNDED_MIN_SCORE: dict[str, float] = {"mock": 0.18, "openai": 0.25}


def search_chunks(
    db: Session,
    user_id: str,
    query: str,
    k: int = 4,
    notebook_id: str | None = None,
) -> list[ChunkHit]:
    """Top-k chunks from the user's notebooks for a query, best first."""
    if k <= 0 or not (query or "").strip():
        return []

    stmt = select(Notebook.id).where(Notebook.user_id == user_id)
    if notebook_id is not None:
        stmt = stmt.where(Notebook.id == notebook_id)
    notebook_ids = list(db.execute(stmt).scalars())
    if not notebook_ids:
        return []

    provider = get_embedding_provider()
    _backfill_embeddings(db, notebook_ids, provider)
    query_vec = provider.embed([query])[0]

    hits: list[ChunkHit] | None = None
    if db.get_bind().dialect.name == "postgresql":
        try:
            hits = _pg_search(db, notebook_ids, query_vec, k)
        except Exception:  # pgvector missing/odd plan — never fail a search
            _log.warning("pgvector search failed; falling back to python cosine")
            db.rollback()
            hits = None
    if hits is None:
        hits = _python_search(db, notebook_ids, query_vec, k)

    floor = _SCORE_FLOOR.get(provider.name, 0.0)
    hits = [h for h in hits if h.score > floor]
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:k]


def top_score(hits: list[ChunkHit]) -> float:
    """Best score in a hit list (0.0 when empty). Use with grounded_floor()."""
    return max((h.score for h in hits), default=0.0)


def grounded_floor() -> float:
    """Minimum top_score for an answer to claim grounding, per active provider."""
    return _GROUNDED_MIN_SCORE.get(get_embedding_provider().name, 0.25)


# ---------------------------------------------------------------- internals


def _backfill_embeddings(db: Session, notebook_ids: list[str], provider) -> None:
    """Embed every NULL-embedding chunk in these notebooks in ONE batch and
    persist. Chunks are written with embedding=None at ingest/seed time, so
    the first search pays the (mock: trivial) embedding cost, and only once."""
    missing = list(
        db.execute(
            select(SourceChunk)
            .where(SourceChunk.notebook_id.in_(notebook_ids))
            .where(SourceChunk.embedding.is_(None))
            .order_by(SourceChunk.source_id, SourceChunk.position)
        ).scalars()
    )
    if not missing:
        return
    vectors = provider.embed([chunk.text for chunk in missing])
    for chunk, vector in zip(missing, vectors):
        chunk.embedding = vector
    try:
        db.commit()  # persist the backfill so later requests skip it
    except Exception:  # pragma: no cover - keep serving from memory on failure
        _log.warning("embedding backfill commit failed; continuing unpersisted")
        db.rollback()


def _pg_search(
    db: Session, notebook_ids: list[str], query_vec: list[float], k: int
) -> list[ChunkHit]:
    """Native pgvector cosine search: score = 1 - (embedding <=> query)."""
    params: dict = {f"nb{i}": nb_id for i, nb_id in enumerate(notebook_ids)}
    in_clause = ", ".join(f":nb{i}" for i in range(len(notebook_ids)))
    params["qvec"] = "[" + ",".join(f"{x:.8f}" for x in query_vec) + "]"
    params["k"] = k
    stmt = sql_text(
        f"""
        SELECT sc.id, sc.source_id, s.title, sc.text, sc.page,
               1 - (sc.embedding <=> CAST(:qvec AS vector)) AS score
        FROM source_chunks sc
        JOIN sources s ON s.id = sc.source_id
        WHERE sc.notebook_id IN ({in_clause}) AND sc.embedding IS NOT NULL
        ORDER BY sc.embedding <=> CAST(:qvec AS vector)
        LIMIT :k
        """
    )
    return [
        ChunkHit(
            chunk_id=row[0],
            source_id=row[1],
            source_title=row[2],
            text=row[3],
            page=row[4],
            score=float(row[5]),
        )
        for row in db.execute(stmt, params)
    ]


def _python_search(
    db: Session, notebook_ids: list[str], query_vec: list[float], k: int
) -> list[ChunkHit]:
    """Pure-python cosine ranking (SQLite path and Postgres fallback)."""
    rows = db.execute(
        select(SourceChunk, Source.title)
        .join(Source, Source.id == SourceChunk.source_id)
        .where(SourceChunk.notebook_id.in_(notebook_ids))
        .where(SourceChunk.embedding.is_not(None))
    ).all()
    scored = [
        ChunkHit(
            chunk_id=chunk.id,
            source_id=chunk.source_id,
            source_title=title,
            text=chunk.text,
            page=chunk.page,
            score=_cosine(query_vec, chunk.embedding),
        )
        for chunk, title in rows
    ]
    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[:k]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / math.sqrt(na * nb)
