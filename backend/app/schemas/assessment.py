"""Request schemas for quiz + flashcards endpoints."""

from pydantic import Field

from app.schemas.common import CamelModel


class QuizGenerateRequest(CamelModel):
    topic_id: str | None = None
    notebook_id: str | None = None
    difficulty: str = "medium"  # easy|medium|hard
    length: int = Field(default=5, ge=1, le=20)  # service clamps to 3-8
    focus: str = "mixed"  # mixed|definitions|concepts|applications


class QuizAnswer(CamelModel):
    question_id: str
    selected_index: int | None = None


class QuizSubmitRequest(CamelModel):
    answers: list[QuizAnswer] = Field(default_factory=list)


class FlashcardsGenerateRequest(CamelModel):
    topic_id: str | None = None
    notebook_id: str | None = None
    count: int = Field(default=8, ge=1, le=50)  # service clamps to <=12
