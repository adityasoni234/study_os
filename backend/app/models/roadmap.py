"""Roadmaps and their milestone/topic/subtopic node tree."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import created_at_column, pk_column


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[str] = pk_column()
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="Topic")
    tone: Mapped[str] = mapped_column(String(32), nullable=False, default="indigo")
    icon: Mapped[str] = mapped_column(String(32), nullable=False, default="sparkles")
    goal_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column(String(64), nullable=True)  # display string, e.g. "Nov 30"
    focus: Mapped[str | None] = mapped_column(String(200), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Plain string on purpose (no FK): AI-generated roadmaps may reference topics
    # that get created in the same request; services resolve it against topics.id.
    next_topic_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    adapted_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = created_at_column()

    nodes: Mapped[list["RoadmapNode"]] = relationship(
        cascade="all, delete-orphan", order_by="RoadmapNode.position"
    )


class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id: Mapped[str] = pk_column()
    roadmap_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # milestone|topic|subtopic
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="locked")  # done|current|locked|review
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    depends_on: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    parent: Mapped["RoadmapNode | None"] = relationship(
        back_populates="children", remote_side="RoadmapNode.id"
    )
    children: Mapped[list["RoadmapNode"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", order_by="RoadmapNode.position"
    )
