"""In-memory sliding-window rate limiter (pure ASGI).

Keyed by ``X-User-ID`` header when present, else client IP. Limit defaults to
``settings.rate_limit_per_minute`` over a 60s window. Over the limit → HTTP 429
with the standard error envelope, code ``RATE_LIMITED``.

Per-process only — good enough for the MVP's single instance. Swap for a
Redis-backed limiter behind the same middleware interface when scaling out.
"""

from __future__ import annotations

import threading
import time
from collections import deque

from starlette.responses import JSONResponse

from app.config import settings
from app.utils.envelope import err_body

DEFAULT_EXEMPT_PATHS: frozenset[str] = frozenset(
    {"/api/health", "/api/docs", "/api/openapi.json"}
)

_MAX_TRACKED_KEYS = 10_000


class RateLimitMiddleware:
    """Sliding-window limiter. Thread-safe via a single lock (operations are O(window))."""

    def __init__(
        self,
        app,
        limit: int | None = None,
        window_s: float = 60.0,
        exempt_paths: frozenset[str] | set[str] | None = None,
    ) -> None:
        self.app = app
        self._limit_override = limit
        self.window_s = window_s
        self.exempt_paths = (
            DEFAULT_EXEMPT_PATHS if exempt_paths is None else frozenset(exempt_paths)
        )
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    @property
    def limit(self) -> int:
        if self._limit_override is not None:
            return self._limit_override
        return settings.rate_limit_per_minute

    @staticmethod
    def _key(scope: dict) -> str:
        for name, value in scope.get("headers") or []:
            if name == b"x-user-id":
                user_id = value.decode("latin-1").strip()
                if user_id:
                    return f"u:{user_id[:64]}"
                break
        client = scope.get("client")
        return f"ip:{client[0]}" if client else "ip:anonymous"

    def _check(self, key: str) -> tuple[bool, int]:
        """Record a hit for key. Returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        cutoff = now - self.window_s
        with self._lock:
            if len(self._hits) > _MAX_TRACKED_KEYS:
                self._hits = {
                    k: dq for k, dq in self._hits.items() if dq and dq[-1] > cutoff
                }
            window = self._hits.setdefault(key, deque())
            while window and window[0] <= cutoff:
                window.popleft()
            if len(window) >= self.limit:
                retry_after = max(1, int(window[0] + self.window_s - now) + 1)
                return False, retry_after
            window.append(now)
            return True, 0

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope.get("path") in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        allowed, retry_after = self._check(self._key(scope))
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content=err_body(
                    "RATE_LIMITED",
                    "Too many requests. Please slow down and try again shortly.",
                ),
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
