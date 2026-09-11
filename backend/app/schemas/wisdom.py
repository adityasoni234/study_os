"""Inner-growth (wisdom) schemas (camelCase JSON via CamelModel)."""

from __future__ import annotations

from app.schemas.common import CamelModel


class WisdomItemOut(CamelModel):
    id: str
    original: str
    transliteration: str
    translation: str
    source: str  # e.g. "Bhagavad Gita 2.47" (model column: source_ref)
    source_note: str
    ai_reflection: str
    question: str
    verified: bool
    saved: bool


class WisdomListResponse(CamelModel):
    items: list[WisdomItemOut]


class WisdomSaveResponse(CamelModel):
    saved: bool
