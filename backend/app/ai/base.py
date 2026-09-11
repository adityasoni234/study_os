"""Provider-neutral AI interface. Spine file — all providers implement this."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, TypedDict


class TaskType(StrEnum):
    # fast / structured → openai primary
    CHAT = "chat"
    TUTOR_FAST = "tutor_fast"
    QUIZ_GEN = "quiz_gen"
    FLASHCARDS = "flashcards"
    ROADMAP_GEN = "roadmap_gen"
    SOURCE_QA = "source_qa"
    STUDYCAST = "studycast"
    INTENT = "intent"
    # deep reasoning → anthropic primary
    DEEP_EXPLAIN = "deep_explain"
    MISCONCEPTION = "misconception"
    EVALUATE_ANSWER = "evaluate_answer"
    SYNTHESIS = "synthesis"
    STUDY_GUIDE = "study_guide"


OPENAI_PRIMARY: frozenset[TaskType] = frozenset(
    {
        TaskType.CHAT,
        TaskType.TUTOR_FAST,
        TaskType.QUIZ_GEN,
        TaskType.FLASHCARDS,
        TaskType.ROADMAP_GEN,
        TaskType.SOURCE_QA,
        TaskType.STUDYCAST,
        TaskType.INTENT,
    }
)


class AIMessage(TypedDict):
    role: str  # "user" | "assistant"
    content: str


@dataclass
class AIResult:
    text: str
    provider: str
    model: str
    latency_ms: int
    usage: dict = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised by providers on failure; router catches and falls back."""


class AIProvider(Protocol):
    name: str

    def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> AIResult: ...

    def available(self) -> bool: ...
