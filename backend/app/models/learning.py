"""Taxonomy (subjects/topics), tutoring sessions, mastery, recommendations, daily mission."""

# `import datetime as dt` (not `from datetime import date`): DailyMission.date would
# shadow the type name inside the class body otherwise.
import datetime as dt

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import created_at_column, pk_column, utcnow


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = pk_column()
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    icon: Mapped[str] = mapped_column(String(32), nullable=False, default="book")
    tone: Mapped[str] = mapped_column(String(32), nullable=False, default="indigo")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[str] = pk_column()
    subject_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class Subtopic(Base):
    __tablename__ = "subtopics"

    id: Mapped[str] = pk_column()
    topic_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="teach")
    started_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    ended_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = pk_column()
    session_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("learning_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = created_at_column()


class Mastery(Base):
    """Single source of truth for learner state per (user, topic)."""

    __tablename__ = "masteries"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_mastery_user_topic"),)

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0-100
    trend: Mapped[str] = mapped_column(String(8), nullable=False, default="flat")  # up|flat|down
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # review|learn|practice|opportunity
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    route: Mapped[str] = mapped_column(String(300), nullable=False)
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[dt.datetime] = created_at_column()
    dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class DailyMission(Base):
    __tablename__ = "daily_missions"
    __table_args__ = (Index("ix_daily_missions_user_date", "user_id", "date"),)

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    topic_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    context: Mapped[str] = mapped_column(String(300), nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    steps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    adapted_note: Mapped[str | None] = mapped_column(Text, nullable=True)
