"""Pydantic schemas for the Notebook feature (camelCase JSON via CamelModel)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel


class NotebookCreate(CamelModel):
    title: str = Field(min_length=1, max_length=200)


class NotebookOut(CamelModel):
    id: str
    title: str
    created_at: datetime
    source_count: int = 0


class SourceCreate(CamelModel):
    """JSON body for POST /notebooks/{id}/sources (the non-file variant)."""

    kind: Literal["text", "url", "youtube", "notes"]
    title: str = Field(min_length=1, max_length=300)
    text: str | None = None
    url: str | None = None


class SourceOut(CamelModel):
    id: str
    title: str
    kind: str  # pdf|web|youtube|notes|text
    status: str  # ready|processing|failed
    meta: str
    added_at: datetime


class AskRequest(CamelModel):
    question: str = Field(min_length=1, max_length=2000)
