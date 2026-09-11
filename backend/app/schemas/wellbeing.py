"""Wellbeing + journal schemas (camelCase JSON via CamelModel)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class WellbeingSessionRequest(CamelModel):
    kind: str = Field(min_length=1, max_length=16)  # reset | plan | talk
    message: str | None = Field(default=None, max_length=4000)


class WellbeingSessionResponse(CamelModel):
    reply: str
    suggestions: list[str]
    disclaimer: str


class JournalCreateRequest(CamelModel):
    mood: str = Field(min_length=1, max_length=16)  # emoji
    mood_label: str = Field(min_length=1, max_length=32)
    note: str = Field(default="", max_length=4000)


class JournalEntryOut(CamelModel):
    id: str
    mood: str
    mood_label: str
    note: str
    created_at: datetime


class JournalListResponse(CamelModel):
    entries: list[JournalEntryOut]
    pattern: str | None
