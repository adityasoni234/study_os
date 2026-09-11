"""AI provider implementations: OpenAI, Anthropic, and an always-on Mock.

Services must NEVER import this module directly — go through `app.ai.router`.
Providers raise `AIProviderError` with SAFE messages (no keys, no payloads,
no response bodies); the router catches them and walks the fallback chain.
"""

from __future__ import annotations

import json
import time

try:  # httpx is only needed by the live providers; mock mode works without it.
    import httpx
except ImportError:  # pragma: no cover - exercised only on minimal installs
    httpx = None  # type: ignore[assignment]

from app.ai import mock_data
from app.ai.base import AIMessage, AIProviderError, AIResult
from app.config import settings

_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"
_JSON_ONLY_INSTRUCTION = "Respond with ONLY valid JSON, no prose, no code fences."

# Up to 2 extra attempts after the first, sleeping 0.5s then 1.5s in between.
_RETRY_BACKOFF_S: tuple[float, ...] = (0.5, 1.5)


def _retryable_status(status: int) -> bool:
    return status == 429 or status >= 500


class _HttpProvider:
    """Shared httpx POST with retry/backoff and safe error reporting."""

    name = "http"

    def __init__(self) -> None:
        self._client: "httpx.Client | None" = None

    def _post(self, url: str, headers: dict[str, str], payload: dict) -> dict:
        if httpx is None:
            raise AIProviderError(
                f"The {self.name} provider is unavailable (HTTP client not installed)."
            )
        if self._client is None:
            self._client = httpx.Client(timeout=settings.request_timeout_s)
        reason = "request failed"
        attempts = len(_RETRY_BACKOFF_S) + 1
        for attempt in range(attempts):
            try:
                response = self._client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException:
                reason = "timed out"
            except httpx.HTTPError:
                reason = "network error"
            else:
                if response.status_code < 400:
                    try:
                        body = response.json()
                    except ValueError as exc:
                        raise AIProviderError(
                            f"The {self.name} provider returned an unreadable response."
                        ) from exc
                    if not isinstance(body, dict):
                        raise AIProviderError(
                            f"The {self.name} provider returned an unexpected response shape."
                        )
                    return body
                reason = f"HTTP {response.status_code}"
                if not _retryable_status(response.status_code):
                    raise AIProviderError(
                        f"The {self.name} provider rejected the request ({reason})."
                    )
            if attempt < attempts - 1:
                time.sleep(_RETRY_BACKOFF_S[attempt])
        raise AIProviderError(f"The {self.name} provider is unreachable ({reason}).")


class OpenAIProvider(_HttpProvider):
    """Chat Completions over HTTPS. json_mode uses response_format json_object."""

    name = "openai"

    def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> AIResult:
        chat: list[dict[str, str]] = []
        if system:
            chat.append({"role": "system", "content": system})
        chat.extend({"role": m["role"], "content": m["content"]} for m in messages)
        payload: dict = {
            "model": settings.openai_model,
            "messages": chat,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        started = time.perf_counter()
        data = self._post(_OPENAI_URL, headers, payload)
        latency_ms = int((time.perf_counter() - started) * 1000)
        try:
            text = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(
                "The openai provider returned an unexpected response shape."
            ) from exc
        return AIResult(
            text=text,
            provider=self.name,
            model=str(data.get("model") or settings.openai_model),
            latency_ms=latency_ms,
            usage=dict(data.get("usage") or {}),
        )

    def available(self) -> bool:
        return settings.openai_live


class AnthropicProvider(_HttpProvider):
    """Messages API over HTTPS. json_mode appends a firm JSON-only instruction."""

    name = "anthropic"

    def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> AIResult:
        system_text = (system or "").strip()
        if json_mode:
            system_text = (
                f"{system_text}\n\n{_JSON_ONLY_INSTRUCTION}" if system_text else _JSON_ONLY_INSTRUCTION
            )
        convo = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("user", "assistant")
        ]
        if not convo:
            convo = [{"role": "user", "content": "Begin."}]
        payload: dict = {
            "model": settings.anthropic_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": convo,
        }
        if system_text:
            payload["system"] = system_text
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
        }
        # Org-level keys (not scoped to a workspace) must name the workspace.
        if settings.anthropic_workspace_id:
            headers["anthropic-workspace-id"] = settings.anthropic_workspace_id
        started = time.perf_counter()
        data = self._post(_ANTHROPIC_URL, headers, payload)
        latency_ms = int((time.perf_counter() - started) * 1000)
        blocks = data.get("content")
        if not isinstance(blocks, list):
            raise AIProviderError(
                "The anthropic provider returned an unexpected response shape."
            )
        text = "".join(
            str(block.get("text", ""))
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        )
        return AIResult(
            text=text,
            provider=self.name,
            model=str(data.get("model") or settings.anthropic_model),
            latency_ms=latency_ms,
            usage=dict(data.get("usage") or {}),
        )

    def available(self) -> bool:
        return settings.anthropic_live


class MockProvider:
    """Deterministic offline provider. Always available; never fails."""

    name = "mock"
    model = "studyos-mock-1"

    def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> AIResult:
        started = time.perf_counter()
        if json_mode:
            text = json.dumps(mock_data.json_payload(system, messages), ensure_ascii=False)
        else:
            text = mock_data.tutor_reply(messages)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return AIResult(
            text=text,
            provider=self.name,
            model=self.model,
            latency_ms=latency_ms,
            usage={},
        )

    def available(self) -> bool:
        return True
