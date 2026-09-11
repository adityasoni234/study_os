"""Request-ID + access logging (pure ASGI).

One single-line JSON log per request via logging.getLogger("studyos"):
    {"ts", "requestId", "method", "path", "status", "ms"}
Never logs request/response bodies, headers, or query values.

The request id is taken from an incoming ``X-Request-ID`` header when it looks
sane, otherwise generated (uuid4 hex). It is exposed on the response as
``X-Request-ID`` and on ``request.state.request_id`` for handlers.
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from uuid import uuid4

log = logging.getLogger("studyos")

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_HEADER_NAME = b"x-request-id"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the 'studyos' logger: INFO, single-line output, no duplication.

    Idempotent — safe to call from main and from tests.
    """
    logger = logging.getLogger("studyos")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    # We emit our own structured access line; quiet uvicorn's duplicate one.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def _incoming_request_id(scope: dict) -> str | None:
    for name, value in scope.get("headers") or []:
        if name == _HEADER_NAME:
            candidate = value.decode("latin-1").strip()
            if _REQUEST_ID_RE.match(candidate):
                return candidate
            return None
    return None


class RequestLoggingMiddleware:
    """Pure-ASGI middleware: assigns a request id, times the request, logs one JSON line."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _incoming_request_id(scope) or uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        method = scope.get("method", "-")
        path = scope.get("path", "-")
        start = time.perf_counter()
        status_seen = {"status": 500}

        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                status_seen["status"] = message["status"]
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != _HEADER_NAME
                ]
                headers.append((_HEADER_NAME, request_id.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            status_seen["status"] = 500
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            log.info(
                json.dumps(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                        "requestId": request_id,
                        "method": method,
                        "path": path,
                        "status": status_seen["status"],
                        "ms": elapsed_ms,
                    },
                    separators=(",", ":"),
                )
            )
