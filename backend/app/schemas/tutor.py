"""Request schemas for the tutor endpoints. Bodies accept camelCase keys."""

from pydantic import Field

from app.schemas.common import CamelModel


class TutorMessageIn(CamelModel):
    """Body of POST /api/tutor/message.

    ``message`` may be blank only when submitting a quiz answer
    (``mode="feedback"`` with ``questionId`` + ``answerIndex``); the service
    validates that combination.
    """

    session_id: str | None = None
    topic_id: str | None = None
    message: str = Field(default="", max_length=8000)
    mode: str | None = None  # teach|practice|review|quiz|feedback|mastery|explain_differently
    style: str | None = None  # explain_differently: simpler|analogy|real_world|visual|...
    question_id: str | None = None
    answer_index: int | None = Field(default=None, ge=0)
