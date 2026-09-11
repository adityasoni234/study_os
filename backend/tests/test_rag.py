"""RAG lane tests: mock embeddings, seeded retrieval, notebook endpoints.

Runs fully offline (conftest pins AI_MODE=mock, in-memory SQLite + seeds)."""

from __future__ import annotations

import io
import math

from app.db.seeds.passages import PASSAGES

DEMO_USER = "demo-user"
DEMO_NOTEBOOK = "default-notebook"
SEEDED_CHUNK_IDS = set(PASSAGES)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _data(response, expected_status: int = 200) -> dict:
    assert response.status_code == expected_status, response.text
    body = response.json()
    assert body["success"] is True and body["error"] is None
    return body["data"]


def _tiny_pdf(text: str) -> bytes:
    """Minimal one-page PDF with real extractable text (Helvetica, one Tj op)."""
    stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_at = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF".encode()
    )
    return out.getvalue()


# ---------------------------------------------------------------- embeddings


def test_mock_embedding_is_deterministic_and_ranks_p14_first():
    from app.retrieval.embeddings import MockEmbedding

    provider = MockEmbedding()
    assert provider.name == "mock" and provider.dim == 1536

    keys = list(PASSAGES)
    vectors = provider.embed([PASSAGES[key] for key in keys])
    assert all(len(vec) == 1536 for vec in vectors)

    query_vec = provider.embed(["precision recall"])[0]
    ranked = sorted(
        zip(keys, vectors), key=lambda kv: _cosine(query_vec, kv[1]), reverse=True
    )
    # Pinned behaviour: 'precision recall' ranks the p.14 passage first.
    assert ranked[0][0] == "unit3-p14"

    # Deterministic across calls (and across processes: salted blake2b, not hash()).
    assert provider.embed(["precision recall"])[0] == query_vec
    # Related texts share features; unrelated ones score near zero.
    unrelated = provider.embed(["medieval castle drawbridge maintenance"])[0]
    assert _cosine(query_vec, unrelated) < 0.1


# ---------------------------------------------------------------- store


def test_search_chunks_ranks_seeded_passages_and_persists_embeddings(db):
    from app.retrieval.store import search_chunks, top_score

    hits = search_chunks(db, DEMO_USER, "precision and recall formulas")

    assert hits, "expected hits from the seeded notebook"
    assert hits[0].chunk_id in {"unit3-p14", "unit3-p15"}
    assert len(hits) <= 4
    assert all(a.score >= b.score for a, b in zip(hits, hits[1:]))
    assert top_score(hits) == hits[0].score > 0.3
    assert hits[0].source_title  # joined from Source, not an id

    # The lazy backfill persisted embeddings — visible from a brand-new session.
    from sqlalchemy import select

    from app.db.base import SessionLocal
    from app.models.notebook import SourceChunk

    fresh = SessionLocal()
    try:
        seeded = list(
            fresh.execute(
                select(SourceChunk).where(SourceChunk.id.in_(SEEDED_CHUNK_IDS))
            ).scalars()
        )
        assert len(seeded) == len(SEEDED_CHUNK_IDS)
        assert all(
            chunk.embedding is not None and len(chunk.embedding) == 1536 for chunk in seeded
        )
    finally:
        fresh.close()


def test_search_chunks_scopes_to_the_users_notebooks(db):
    from app.retrieval.store import search_chunks

    assert search_chunks(db, "user-with-no-notebooks", "precision recall") == []
    assert search_chunks(db, DEMO_USER, "precision recall", notebook_id="not-a-notebook") == []


# ---------------------------------------------------------------- ask


def test_ask_grounded_answer_with_citations(client):
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/ask",
        json={"question": "What is the formula for precision and recall?"},
    )
    data = _data(response)

    assert data["grounded"] is True
    assert data["answer"].strip()
    assert len(data["citations"]) >= 1
    for citation in data["citations"]:
        # Contract shape only — chunk/embedding ids must never leak.
        assert set(citation) == {"sourceId", "title", "page", "snippet", "url"}
        assert citation["sourceId"] not in SEEDED_CHUNK_IDS
        assert citation["snippet"]
    assert any(c["title"] and c["page"] is not None for c in data["citations"])


def test_ask_unrelated_question_is_honestly_ungrounded(client):
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/ask",
        json={"question": "What is the capital of France?"},
    )
    data = _data(response)

    assert data["grounded"] is False
    assert data["citations"] == []
    assert "couldn't find" in data["answer"].lower()


def test_ask_foreign_notebook_is_404(client):
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/ask",
        json={"question": "What is precision?"},
        headers={"X-User-ID": "intruder-user"},
    )
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False and body["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------- notebooks


def test_default_notebook_always_exists_for_a_new_user(client):
    data = _data(client.get("/api/notebooks", headers={"X-User-ID": "rag-fresh-user"}))
    notebooks = data["notebooks"]
    assert len(notebooks) >= 1
    first = notebooks[0]
    assert set(first) == {"id", "title", "createdAt", "sourceCount"}
    assert first["sourceCount"] == 0


def test_demo_user_sees_seeded_notebook_with_source_count(client):
    data = _data(client.get("/api/notebooks"))
    by_id = {nb["id"]: nb for nb in data["notebooks"]}
    assert DEMO_NOTEBOOK in by_id
    assert by_id[DEMO_NOTEBOOK]["sourceCount"] >= 4  # seeded sources


# ---------------------------------------------------------------- ingestion


def test_text_source_ingestion_then_ask_finds_it(client):
    created = _data(client.post("/api/notebooks", json={"title": "Reactor notes"}))
    notebook_id = created["id"]

    source = _data(
        client.post(
            f"/api/notebooks/{notebook_id}/sources",
            json={
                "kind": "text",
                "title": "Zorbax primer",
                "text": (
                    "The zorbax coefficient measures how quickly a fictional zorbax "
                    "reactor stabilises after a cold start. A higher zorbax "
                    "coefficient means the reactor settles faster and wastes less fuel."
                ),
            },
        )
    )
    assert source["kind"] == "text" and source["status"] == "ready"
    assert set(source) == {"id", "title", "kind", "status", "meta", "addedAt"}

    listing = _data(client.get(f"/api/notebooks/{notebook_id}/sources"))
    assert [s["title"] for s in listing["sources"]] == ["Zorbax primer"]

    answer = _data(
        client.post(
            f"/api/notebooks/{notebook_id}/ask",
            json={"question": "What does the zorbax coefficient measure?"},
        )
    )
    assert answer["grounded"] is True
    assert answer["citations"][0]["title"] == "Zorbax primer"


def test_pdf_upload_ingests_pages_and_is_searchable(client, db):
    created = _data(client.post("/api/notebooks", json={"title": "Marsh studies"}))
    notebook_id = created["id"]

    pdf_bytes = _tiny_pdf("Kelvindale marsh drainage relies on tidal sluice gates.")
    source = _data(
        client.post(
            f"/api/notebooks/{notebook_id}/sources",
            files={"file": ("marsh.pdf", pdf_bytes, "application/pdf")},
        )
    )
    assert source["kind"] == "pdf" and source["status"] == "ready"
    assert source["meta"] == "PDF · 1 page"

    from app.retrieval.store import search_chunks

    hits = search_chunks(
        db, DEMO_USER, "kelvindale marsh drainage", notebook_id=notebook_id
    )
    assert hits and hits[0].page == 1
    assert "sluice" in hits[0].text


def test_pdf_with_wrong_magic_bytes_is_rejected(client):
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/sources",
        files={"file": ("junk.pdf", b"this is definitely not a pdf", "application/pdf")},
    )
    assert response.status_code == 415
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "UNSUPPORTED_FILE"


def test_oversized_upload_is_rejected(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "max_upload_mb", 0)
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/sources",
        files={"file": ("big.pdf", _tiny_pdf("x"), "application/pdf")},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_url_source_stub_never_breaks_retrieval(client):
    created = _data(client.post("/api/notebooks", json={"title": "Link shelf"}))
    notebook_id = created["id"]

    source = _data(
        client.post(
            f"/api/notebooks/{notebook_id}/sources",
            json={
                "kind": "youtube",
                "title": "StatQuest — ROC curves",
                "url": "https://www.youtube.com/watch?v=abc123",
            },
        )
    )
    assert source["kind"] == "youtube" and source["status"] == "ready"

    # No pasted text → a single title+url chunk exists, so ask never crashes.
    answer = _data(
        client.post(
            f"/api/notebooks/{notebook_id}/ask",
            json={"question": "Explain gradient boosting."},
        )
    )
    assert answer["grounded"] is False


def test_json_source_missing_text_is_validation_error(client):
    response = client.post(
        f"/api/notebooks/{DEMO_NOTEBOOK}/sources",
        json={"kind": "text", "title": "Empty"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
