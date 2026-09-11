"""Tests for the AI layer: routing, JSON generation, intent, fallback.

Runs fully offline — AI_MODE is forced to mock before any app import.
"""

import os

os.environ["AI_MODE"] = "mock"

import pytest

from app.ai import intent, prompts, router
from app.ai.base import AIMessage, AIProviderError, AIResult, TaskType
from app.ai.providers import MockProvider
from app.utils.errors import AppError


def _messages(text: str) -> list[AIMessage]:
    return [{"role": "user", "content": text}]


class FailingProvider:
    """Fake provider that always raises, to exercise the fallback chain."""

    name = "failing"

    def generate(self, messages, *, system=None, max_tokens=1024, temperature=0.7, json_mode=False):
        raise AIProviderError("The failing provider is down.")

    def available(self) -> bool:
        return True


class BadJSONProvider:
    """Fake provider that returns non-JSON text even in json_mode."""

    name = "badjson"

    def generate(self, messages, *, system=None, max_tokens=1024, temperature=0.7, json_mode=False):
        return AIResult(text="sorry, no json here", provider=self.name, model="bad-1", latency_ms=1)

    def available(self) -> bool:
        return True


def test_mock_mode_routes_to_mock_provider():
    result = router.generate(TaskType.CHAT, _messages("Explain precision vs recall"))
    assert isinstance(result, AIResult)
    assert result.provider == "mock"
    assert result.model
    assert result.text.strip()
    # tutor-style mock reply references the student's message
    assert "precision" in result.text.lower()


def test_provider_chain_ends_with_mock_and_has_no_dead_providers():
    chain = router.get_provider_chain(TaskType.CHAT)
    assert [p.name for p in chain] == ["mock"]  # AI_MODE=mock: only mock is available
    deep = router.get_provider_chain(TaskType.DEEP_EXPLAIN)
    assert deep[-1].name == "mock"


def test_generate_json_quiz_shape():
    prompt = prompts.quiz_prompt("Precision & Recall", "medium", 5, "mixed", None)
    data, result = router.generate_json(TaskType.QUIZ_GEN, _messages(prompt))
    assert result.provider == "mock"
    assert isinstance(data, dict)
    questions = data["questions"]
    assert len(questions) == 5
    for question in questions:
        assert isinstance(question["prompt"], str) and question["prompt"]
        assert isinstance(question["options"], list) and len(question["options"]) == 4
        assert all(isinstance(option, str) for option in question["options"])
        assert isinstance(question["correctIndex"], int)
        assert 0 <= question["correctIndex"] <= 3
        assert question["explanation"]
        assert question["tag"] in {"Definitions", "Concepts", "Applications"}


def test_intent_rules():
    assert intent.classify("test me") == "quiz"
    assert intent.classify("explain simpler") == "explain_differently"
    assert intent.classify("hello") == "teach"


def test_intent_more_phrases_offline():
    assert intent.classify("can you quiz me on recall?") == "quiz"
    assert intent.classify("give me an analogy") == "explain_differently"
    assert intent.classify("let's review that again") == "review"
    assert intent.classify("I want to practice problems") == "practice"
    assert intent.classify("") == "teach"


def test_router_falls_back_when_first_provider_errors(monkeypatch):
    chain = [FailingProvider(), MockProvider()]
    monkeypatch.setattr(router, "get_provider_chain", lambda task: list(chain))
    result = router.generate(TaskType.CHAT, _messages("What is recall?"))
    assert result.provider == "mock"
    assert result.text.strip()


def test_router_raises_ai_unavailable_when_every_provider_fails(monkeypatch):
    monkeypatch.setattr(router, "get_provider_chain", lambda task: [FailingProvider()])
    with pytest.raises(AppError) as excinfo:
        router.generate(TaskType.CHAT, _messages("hi"))
    assert excinfo.value.code == "AI_UNAVAILABLE"
    assert excinfo.value.status == 503


def test_generate_json_falls_back_to_mock_json_on_unparseable_output(monkeypatch):
    monkeypatch.setattr(router, "get_provider_chain", lambda task: [BadJSONProvider()])
    data, result = router.generate_json(
        TaskType.QUIZ_GEN, _messages("Make a quiz about recall"), schema_hint='{"questions": [...]}'
    )
    assert isinstance(data, dict)
    assert result.provider == "mock"  # deterministic fallback so callers always get a dict
    assert "questions" in data
