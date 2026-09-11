"""User account, profile and goals."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import created_at_column, pk_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = pk_column()
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = created_at_column()

    profile: Mapped["Profile | None"] = relationship(cascade="all, delete-orphan", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    level: Mapped[str] = mapped_column(String(32), nullable=False, default="Beginner")
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    explanation_style: Mapped[str] = mapped_column(String(32), nullable=False, default="visual")
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="learning")
    target_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
