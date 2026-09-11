"""Notebooks, ingested sources and their retrieval chunks."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.vector_type import EmbeddingVector
from app.models.common import created_at_column, pk_column, utcnow


class Notebook(Base):
    __tablename__ = "notebooks"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = created_at_column()

    sources: Mapped[list["Source"]] = relationship(
        cascade="all, delete-orphan", order_by="Source.added_at"
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = pk_column()
    notebook_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # pdf|web|youtube|notes|text
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ready")  # ready|processing|failed
    meta: Mapped[str] = mapped_column(String(200), nullable=False, default="")  # display string, e.g. "PDF · 42 pages"
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    chunks: Mapped[list["SourceChunk"]] = relationship(
        cascade="all, delete-orphan", order_by="SourceChunk.position"
    )


class SourceChunk(Base):
    __tablename__ = "source_chunks"

    id: Mapped[str] = pk_column()
    source_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notebook_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(EmbeddingVector, nullable=True)
    created_at: Mapped[datetime] = created_at_column()
