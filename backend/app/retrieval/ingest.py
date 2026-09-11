"""Source ingestion: extract → normalise → chunk → persist Source + chunks.

Chunks are stored with ``embedding=None``; ``app.retrieval.store.search_chunks``
backfills embeddings lazily in one batch on first search, so ingestion never
needs the network and uploads stay fast.
"""

from __future__ import annotations

import io
import re
from typing import Protocol
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.config import settings
from app.models.notebook import Notebook, Source, SourceChunk
from app.utils.errors import AppError
from app.utils.ids import new_id

TARGET_CHARS = 1100
OVERLAP_CHARS = 150

_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


# ---------------------------------------------------------------- chunking


def chunk_text(
    text: str, target_chars: int = TARGET_CHARS, overlap: int = OVERLAP_CHARS
) -> list[str]:
    """Split normalised text into ~target_chars chunks on paragraph/sentence
    boundaries, each chunk (after the first) prefixed with ~overlap chars of
    the previous one so ideas straddling a boundary stay retrievable."""
    units = _units(text, target_chars)
    if not units:
        return []

    chunks: list[str] = []
    buffer = ""
    for unit in units:
        candidate = f"{buffer} {unit}".strip() if buffer else unit
        if buffer and len(candidate) > target_chars:
            chunks.append(buffer)
            buffer = f"{_tail(buffer, overlap)} {unit}".strip()
        else:
            buffer = candidate
    if buffer:
        chunks.append(buffer)
    return chunks


def _units(text: str, target_chars: int) -> list[str]:
    """Whitespace-normalised paragraphs; oversized ones split into sentences,
    monster sentences hard-split so no unit exceeds target_chars."""
    units: list[str] = []
    for raw_paragraph in _PARAGRAPH_SPLIT_RE.split(text or ""):
        paragraph = " ".join(raw_paragraph.split())
        if not paragraph:
            continue
        if len(paragraph) <= target_chars:
            units.append(paragraph)
            continue
        for sentence in _SENTENCE_SPLIT_RE.split(paragraph):
            sentence = sentence.strip()
            if not sentence:
                continue
            while len(sentence) > target_chars:
                cut = sentence.rfind(" ", 0, target_chars)
                cut = cut if cut > 0 else target_chars
                units.append(sentence[:cut].strip())
                sentence = sentence[cut:].strip()
            if sentence:
                units.append(sentence)
    return units


def _tail(text: str, overlap: int) -> str:
    """Last ~overlap chars of a chunk, cut at a word boundary."""
    if overlap <= 0 or len(text) <= overlap:
        return text if overlap > 0 else ""
    tail = text[-overlap:]
    space = tail.find(" ")
    return tail[space + 1 :] if space != -1 else tail


# ---------------------------------------------------------------- ingestion


def ingest_pdf(db: Session, notebook: Notebook, title: str, file_bytes: bytes) -> Source:
    """Validate, extract per page (pypdf), chunk per page with page numbers."""
    _enforce_upload_limit(len(file_bytes))
    if not file_bytes.startswith(b"%PDF"):
        raise AppError("UNSUPPORTED_FILE", "That file doesn't look like a valid PDF.", 415)

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(reader.pages)
    except AppError:
        raise
    except Exception as exc:  # corrupt/encrypted beyond repair — never leak details
        raise AppError("UNSUPPORTED_FILE", "That PDF could not be read.", 415) from exc

    source = _make_source(
        notebook,
        title=title,
        kind="pdf",
        meta=f"PDF · {page_count} page{'s' if page_count != 1 else ''}",
    )
    db.add(source)

    position = 0
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:  # a single bad page must not sink the document
            page_text = ""
        for chunk in chunk_text(page_text):
            db.add(_make_chunk(source, notebook, position, chunk, page=page_number))
            position += 1
    if position == 0:  # e.g. a scanned/imageonly PDF — keep the source findable
        db.add(_make_chunk(source, notebook, 0, title, page=None))
    db.flush()
    return source


def ingest_text(
    db: Session, notebook: Notebook, title: str, text: str, kind: str = "text"
) -> Source:
    """Pasted text / notes / uploaded .txt. kind: 'text' | 'notes'."""
    _enforce_upload_limit(len((text or "").encode("utf-8")))
    chunks = chunk_text(text or "")
    label = "Notes" if kind == "notes" else "Text"
    words = len((text or "").split())
    source = _make_source(notebook, title=title, kind=kind, meta=f"{label} · {words} words")
    db.add(source)
    for position, chunk in enumerate(chunks or [title]):
        db.add(_make_chunk(source, notebook, position, chunk, page=None))
    db.flush()
    return source


def ingest_url(
    db: Session,
    notebook: Notebook,
    title: str,
    url: str,
    kind: str = "web",
    text: str | None = None,
) -> Source:
    """URL stub (kind 'web' | 'youtube'): store the url, status 'ready'.

    No network fetching in the MVP — if the caller pasted the page/transcript
    text we chunk that; otherwise a single title+url chunk keeps retrieval
    from ever crashing on an empty source.
    """
    label = "YouTube" if kind == "youtube" else "Web"
    domain = urlparse(url).netloc or "link"
    source = _make_source(
        notebook, title=title, kind=kind, meta=f"{label} · {domain}", url=url
    )
    db.add(source)
    chunks = chunk_text(text) if text else [f"{title} — {url}"]
    for position, chunk in enumerate(chunks or [f"{title} — {url}"]):
        db.add(_make_chunk(source, notebook, position, chunk, page=None))
    db.flush()
    return source


class UrlFetcher(Protocol):
    """Extension point: post-MVP, a fetcher turns a URL into real text before
    ``ingest_url`` chunks it (HTML page extraction, YouTube transcripts, ...).
    Implement this protocol, fetch inside a worker/background task, and pass
    the result as ``text=`` — ``ingest_url`` itself stays network-free."""

    def fetch(self, url: str) -> str: ...


# ---------------------------------------------------------------- helpers


def _enforce_upload_limit(size_bytes: int) -> None:
    limit_mb = settings.max_upload_mb
    if size_bytes > limit_mb * 1024 * 1024:
        raise AppError("FILE_TOO_LARGE", f"Uploads are limited to {limit_mb} MB.", 413)


def _make_source(
    notebook: Notebook, *, title: str, kind: str, meta: str, url: str | None = None
) -> Source:
    return Source(
        id=new_id(),
        notebook_id=notebook.id,
        title=(title or "Untitled source").strip()[:300],
        kind=kind,
        status="ready",
        meta=meta[:200],
        url=url,
    )


def _make_chunk(
    source: Source, notebook: Notebook, position: int, text: str, page: int | None
) -> SourceChunk:
    return SourceChunk(
        id=new_id(),
        source_id=source.id,
        notebook_id=notebook.id,
        position=position,
        page=page,
        text=text,
        embedding=None,  # backfilled lazily by app.retrieval.store.search_chunks
    )
