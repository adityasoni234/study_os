"""Request schemas for the Roadmaps endpoints (responses are built as dicts in
app.services.roadmap so the tree serialisation stays in one place)."""

from pydantic import Field

from app.schemas.common import CamelModel


class RoadmapCreate(CamelModel):
    goal: str = Field(min_length=1, max_length=500)
    type: str | None = None  # Subject|Topic|Exam|Skill|Career|Personal
    level: str = "Beginner"
    hours_per_week: int = Field(default=5, ge=1, le=80)
    deadline: str | None = Field(default=None, max_length=64)
    known_topics: list[str] = Field(default_factory=list)


class RoadmapPatch(CamelModel):
    """PATCH body — only the provided fields are applied (exclude_unset)."""

    target_date: str | None = Field(default=None, max_length=64)
    goal: str | None = Field(default=None, max_length=500)
    archived: bool | None = None
