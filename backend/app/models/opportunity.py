"""Opportunities, saves, and preparation plans."""

# `import datetime as dt`: Opportunity.deadline_date is a date column; avoid name clashes.
import datetime as dt

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import created_at_column, pk_column


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = pk_column()
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    org: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # Hackathon|Internship|Scholarship|...
    tone: Mapped[str] = mapped_column(String(32), nullable=False, default="indigo")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    deadline_text: Mapped[str] = mapped_column(String(64), nullable=False)  # display string, e.g. "Sep 18"
    deadline_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    days_left: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="Online")
    eligibility: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = created_at_column()


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"
    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uq_saved_opportunity_user_opp"),
    )

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[dt.datetime] = created_at_column()


class PrepPlan(Base):
    """Preparation plan for an opportunity (the OpportunityApplication in DATABASE.md)."""

    __tablename__ = "prep_plans"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    readiness: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gap_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    days: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    started: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = created_at_column()

    tasks: Mapped[list["PrepTask"]] = relationship(
        cascade="all, delete-orphan", order_by="(PrepTask.day, PrepTask.position)"
    )


class PrepTask(Base):
    __tablename__ = "prep_tasks"

    id: Mapped[str] = pk_column()
    plan_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("prep_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
