"""Task-based routing over AI providers — the ONLY entry point services use.

    from app.ai import router
    result = router.generate(TaskType.CHAT, messages, system=prompts.TUTOR_SYSTEM)
    data, result = router.generate_json(TaskType.QUIZ_GEN, messages, schema_hint=...)

Routing: primary provider per task (see docs/ARCHITECTURE.md), then the other
live provider, then the mock — so generation practically never fails. One JSON
log line per attempt on logger "studyos.ai": {task, provider, ok, ms}. Never
log content, keys, or payloads.
"""

from __future__ import annotations

import json
import logging
import re
import time
from functools import lru_cache

from app.ai import prompts
from app.ai.base import (
    OPENAI_PRIMARY,
    AIMessage,
    AIProvider,
    AIProviderError,
    AIResult,
    TaskType,
)
from app.ai.providers import AnthropicProvider, MockProvider, OpenAIProvider
from app.config import settings
from app.utils.errors import AppError

_log = logging.getLogger("studyos.ai")

CROSS_CHECK_TASKS: frozenset[TaskType] = frozenset(
    {TaskType.EVALUATE_ANSWER, TaskType.DEEP_EXPLAIN}
)

_REPAIR_INSTRUCTION = "Your previous output was not valid JSON. Return ONLY the JSON object."


@lru_cache(maxsize=1)
def _openai() -> OpenAIProvider:
    return OpenAIProvider()


@lru_cache(maxsize=1)
def _anthropic() -> AnthropicProvider:
    return AnthropicProvider()


@lru_cache(maxsize=1)
def _mock() -> MockProvider:
    return MockProvider()


def get_provider_chain(task: TaskType) -> list[AIProvider]:
    """Ordered fallback chain for a task: primary, other live provider, mock."""
    if task in OPENAI_PRIMARY:
        primary, secondary = _openai(), _anthropic()
    else:
        primary, secondary = _anthropic(), _openai()
    chain: list[AIProvider] = [p for p in (primary, secondary) if p.available()]
    chain.append(_mock())
    return chain


def _log_attempt(task: TaskType, provider: str, ok: bool, ms: int) -> None:
    _log.info(json.dumps({"task": str(task), "provider": provider, "ok": ok, "ms": ms}))


def generate(
    task: TaskType,
    messages: list[AIMessage],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> AIResult:
    """Generate text for a task, walking the fallback chain.

    Raises AppError("AI_UNAVAILABLE", ..., 503) only if every provider —
    including the mock — fails, which is practically never.
    """
    for provider in get_provider_chain(task):
        started = time.perf_counter()
        try:
            result = provider.generate(
                messages,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
                json_mode=json_mode,
            )
        except AIProviderError:
            _log_attempt(task, provider.name, False, int((time.perf_counter() - started) * 1000))
            continue
        except Exception:  # defensive: a provider bug must not become a 500
            _log_attempt(task, provider.name, False, int((time.perf_counter() - started) * 1000))
            continue
        _log_attempt(task, provider.name, True, result.latency_ms)
        if not json_mode and settings.cross_check and task in CROSS_CHECK_TASKS:
            result = _cross_checked(task, result, messages)
        return result
    raise AppError("AI_UNAVAILABLE", "The tutor is briefly unavailable — please retry.", 503)


def generate_json(
    task: TaskType,
    messages: list[AIMessage],
    *,
    system: str | None = None,
    max_tokens: int = 2048,
    schema_hint: str | None = None,
) -> tuple[dict, AIResult]:
    """Generate and parse a JSON object; callers ALWAYS get a dict back.

    One repair retry on invalid JSON, then a deterministic mock fallback.
    """
    full_system = _with_schema_hint(system, schema_hint)
    result = generate(
        task, messages, system=full_system, max_tokens=max_tokens, temperature=0.3, json_mode=True
    )
    data = _try_parse_json(result.text)
    if data is not None:
        return data, result

    repair_messages: list[AIMessage] = [
        *messages,
        {"role": "assistant", "content": result.text},
        {"role": "user", "content": _REPAIR_INSTRUCTION},
    ]
    retry = generate(
        task,
        repair_messages,
        system=full_system,
        max_tokens=max_tokens,
        temperature=0.2,
        json_mode=True,
    )
    data = _try_parse_json(retry.text)
    if data is not None:
        return data, retry

    mock = _mock()
    fallback = mock.generate(messages, system=full_system, max_tokens=max_tokens, json_mode=True)
    _log_attempt(task, mock.name, True, fallback.latency_ms)
    data = _try_parse_json(fallback.text) or {"result": "ok"}
    return data, fallback


def cross_check(
    task: TaskType,
    draft_text: str,
    messages: list[AIMessage],
    *,
    draft_provider: str | None = None,
) -> str:
    """Send a draft answer to the other live provider for a review pass.

    Active only when settings.cross_check is on and task is EVALUATE_ANSWER or
    DEEP_EXPLAIN. Returns the improved text, or the draft unchanged on any
    failure — the main answer path must never break because of a review.
    """
    if not settings.cross_check or task not in CROSS_CHECK_TASKS or not draft_text.strip():
        return draft_text
    producer = draft_provider or (
        _openai().name if task in OPENAI_PRIMARY else _anthropic().name
    )
    if producer == _mock().name:
        return draft_text
    reviewer: AIProvider = _anthropic() if producer == _openai().name else _openai()
    if reviewer.name == producer or not reviewer.available():
        return draft_text
    student_ask = messages[-1]["content"] if messages else ""
    review_messages: list[AIMessage] = [
        {
            "role": "user",
            "content": (
                "Another tutor drafted the reply below for this student. Review it for "
                "factual accuracy, clarity, and a warm, non-shaming tone. Fix anything "
                "wrong or confusing and tighten the wording. Return ONLY the final "
                "improved reply, with no notes about your review.\n\n"
                f"STUDENT'S MESSAGE:\n{student_ask}\n\n"
                f"DRAFT REPLY:\n{draft_text}"
            ),
        }
    ]
    started = time.perf_counter()
    try:
        reviewed = reviewer.generate(
            review_messages, system=prompts.TUTOR_SYSTEM, max_tokens=1024, temperature=0.3
        )
    except Exception:
        _log_attempt(task, reviewer.name, False, int((time.perf_counter() - started) * 1000))
        return draft_text
    _log_attempt(task, reviewer.name, True, reviewed.latency_ms)
    improved = reviewed.text.strip()
    return improved or draft_text


def _cross_checked(task: TaskType, result: AIResult, messages: list[AIMessage]) -> AIResult:
    improved = cross_check(task, result.text, messages, draft_provider=result.provider)
    if improved:
        result.text = improved
    return result


def _with_schema_hint(system: str | None, schema_hint: str | None) -> str | None:
    if not schema_hint:
        return system
    return f"{system}\n\n{schema_hint}" if system else schema_hint


_FENCE_OPEN_RE = re.compile(r"^```[a-zA-Z]*\s*")


def _try_parse_json(text: str) -> dict | None:
    """Best-effort parse to a dict: raw, fence-stripped, then braced substring."""
    candidate = _strip_code_fences(text)
    for attempt in (candidate, _braced_substring(candidate)):
        if not attempt:
            continue
        try:
            parsed = json.loads(attempt)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = _FENCE_OPEN_RE.sub("", stripped, count=1)
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def _braced_substring(text: str) -> str | None:
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return None
