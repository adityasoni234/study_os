"""Quizzes, flashcards, study guides and mind maps."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import created_at_column, pk_column


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    notebook_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    focus: Mapped[str] = mapped_column(String(32), nullable=False, default="mixed")
    created_at: Mapped[datetime] = created_at_column()

    questions: Mapped[list["QuizQuestion"]] = relationship(
        cascade="all, delete-orphan", order_by="QuizQuestion.position"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[str] = pk_column()
    quiz_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tag: Mapped[str] = mapped_column(String(64), nullable=False, default="")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = pk_column()
    quiz_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    answers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    strengths: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = created_at_column()


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    weak: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = created_at_column()


class StudyGuide(Base):
    __tablename__ = "study_guides"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    notebook_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    sections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = created_at_column()


class MindMap(Base):
    __tablename__ = "mind_maps"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    notebook_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    center: Mapped[str] = mapped_column(String(200), nullable=False)
    nodes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = created_at_column()
