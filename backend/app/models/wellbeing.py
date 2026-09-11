"""Wellbeing logs, journal entries and wisdom items."""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import created_at_column, pk_column


class WellbeingLog(Base):
    __tablename__ = "wellbeing_logs"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # reset|plan|talk
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = created_at_column()


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mood: Mapped[str] = mapped_column(String(16), nullable=False)  # emoji
    mood_label: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = created_at_column()


class WisdomItem(Base):
    __tablename__ = "wisdom_items"

    id: Mapped[str] = pk_column()
    original: Mapped[str] = mapped_column(Text, nullable=False)
    transliteration: Mapped[str] = mapped_column(Text, nullable=False)
    translation: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g. "Bhagavad Gita 2.47"
    source_note: Mapped[str] = mapped_column(String(300), nullable=False)
    ai_reflection: Mapped[str] = mapped_column(Text, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    tradition: Mapped[str] = mapped_column(String(64), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class SavedWisdom(Base):
    __tablename__ = "saved_wisdom"

    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    wisdom_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("wisdom_items.id", ondelete="CASCADE"), primary_key=True
    )
