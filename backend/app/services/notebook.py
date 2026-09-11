"""Notebook business logic: notebooks, source ingestion, grounded ask.

Retrieval goes through app.retrieval.store.search_chunks; generation through
app.ai.router (SOURCE_QA). API responses never contain chunk or embedding ids.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai import router as ai_router
from app.ai.base import TaskType
from app.models.notebook import Notebook, Source
from app.models.user import User
from app.retrieval.citations import build_citations
from app.retrieval.ingest import ingest_pdf, ingest_text, ingest_url
from app.retrieval.store import grounded_floor, search_chunks, top_score
from app.schemas.notebook import NotebookOut, SourceCreate
from app.utils.errors import AppError, NotFound
from app.utils.ids import new_id

DEFAULT_NOTEBOOK_TITLE = "My Notebook"

UNGROUNDED_ANSWER = (
    "I couldn't find this in your sources, so I won't guess. Try adding a "
    "source that covers it, or ask the tutor for a general explanation."
)


# ---------------------------------------------------------------- notebooks


def ensure_default_notebook(db: Session, user: User) -> None:
    """Guarantee the user has at least one notebook (contract: a default
    notebook always exists). Idempotent; creates lazily on first list."""
    has_any = db.execute(
        select(Notebook.id).where(Notebook.user_id == user.id).limit(1)
    ).scalar_one_or_none()
    if has_any is None:
        db.add(Notebook(id=new_id(), user_id=user.id, title=DEFAULT_NOTEBOOK_TITLE))
        db.flush()


def create_notebook(db: Session, user: User, title: str) -> NotebookOut:
    notebook = Notebook(id=new_id(), user_id=user.id, title=title.strip())
    db.add(notebook)
    db.flush()
    return NotebookOut(
        id=notebook.id, title=notebook.title, created_at=notebook.created_at, source_count=0
    )


def list_notebooks(db: Session, user: User) -> list[NotebookOut]:
    ensure_default_notebook(db, user)
    counts = dict(
        db.execute(
            select(Source.notebook_id, func.count(Source.id))
            .join(Notebook, Notebook.id == Source.notebook_id)
            .where(Notebook.user_id == user.id)
            .group_by(Source.notebook_id)
        ).all()
    )
    notebooks = db.execute(
        select(Notebook).where(Notebook.user_id == user.id).order_by(Notebook.created_at)
    ).scalars()
    return [
        NotebookOut(
            id=nb.id,
            title=nb.title,
            created_at=nb.created_at,
            source_count=int(counts.get(nb.id, 0)),
        )
        for nb in notebooks
    ]


def get_notebook(db: Session, user: User, notebook_id: str) -> Notebook:
    """The user's notebook, or 404 — foreign notebooks are indistinguishable
    from missing ones on purpose."""
    notebook = db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise NotFound("Notebook")
    return notebook


# ---------------------------------------------------------------- sources


def list_sources(db: Session, notebook: Notebook) -> list[Source]:
    return list(
        db.execute(
            select(Source).where(Source.notebook_id == notebook.id).order_by(Source.added_at)
        ).scalars()
    )


def add_source_from_json(db: Session, notebook: Notebook, payload: SourceCreate) -> Source:
    """JSON variant: pasted text/notes, or a url/youtube stub (optionally with
    pasted text, e.g. a transcript)."""
    title = payload.title.strip()
    if payload.kind in ("text", "notes"):
        if not (payload.text or "").strip():
            raise AppError("VALIDATION_ERROR", "Provide 'text' for a text or notes source.", 422)
        return ingest_text(db, notebook, title, payload.text, kind=payload.kind)
    # kind is "url" | "youtube"
    if not (payload.url or "").strip():
        raise AppError("VALIDATION_ERROR", "Provide 'url' for a url or youtube source.", 422)
    kind = "youtube" if payload.kind == "youtube" else "web"
    return ingest_url(db, notebook, title, payload.url.strip(), kind=kind, text=payload.text)


def add_source_from_file(
    db: Session,
    notebook: Notebook,
    *,
    filename: str,
    content_type: str,
    data: bytes,
    title: str | None = None,
) -> Source:
    """Multipart variant: PDF or plain-text file, ingested synchronously."""
    name = (filename or "").lower()
    resolved_title = (title or "").strip() or filename or "Uploaded document"
    if name.endswith(".pdf") or content_type == "application/pdf":
        return ingest_pdf(db, notebook, resolved_title, data)
    if name.endswith((".txt", ".md")) or content_type.startswith("text/"):
        return ingest_text(
            db, notebook, resolved_title, data.decode("utf-8", errors="replace"), kind="text"
        )
    raise AppError(
        "UNSUPPORTED_FILE", "Only PDF and plain-text (.txt, .md) uploads are supported.", 415
    )


# ---------------------------------------------------------------- ask


def ask(db: Session, user: User, notebook_id: str, question: str) -> dict:
    """Grounded Q&A over one notebook's sources.

    Below the grounding floor we answer honestly WITHOUT calling the model
    about content — no retrieved support means nothing to ground on.
    """
    notebook = get_notebook(db, user, notebook_id)
    hits = search_chunks(db, user.id, question, k=4, notebook_id=notebook.id)

    if not hits or top_score(hits) < grounded_floor():
        return {"answer": UNGROUNDED_ANSWER, "citations": [], "grounded": False}

    labeled = [(f"S{i}", hit.source_title, hit.text) for i, hit in enumerate(hits, start=1)]
    prompt = prompts.source_qa_prompt(question, labeled)
    result = ai_router.generate(
        TaskType.SOURCE_QA,
        [{"role": "user", "content": prompt}],
        system=prompts.TUTOR_SYSTEM,
    )
    citations = build_citations(hits, db)
    return {
        "answer": result.text,
        "citations": [citation.to_dict() for citation in citations],
        "grounded": True,
    }
