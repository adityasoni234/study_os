"""Request schemas for content generation (study guide, mind map, studycast)."""

from pydantic import Field

from app.schemas.common import CamelModel


class ContentSourceRequest(CamelModel):
    """topicId or notebookId — the service enforces that at least one is given."""

    topic_id: str | None = None
    notebook_id: str | None = None


class StudycastGenerateRequest(ContentSourceRequest):
    minutes: int = Field(default=5, ge=1, le=30)
