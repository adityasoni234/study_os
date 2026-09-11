"""StudyOS smoke test — run against a live server, no app imports.

Usage:
    BASE_URL=http://localhost:8000 python -m scripts.smoke_test

Prints PASS/WARN/FAIL per check with latency. Exit code 1 on any FAIL.
A 404 is a WARN, not a failure — the feature may not be mounted yet.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Callable

import httpx

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_results: list[tuple[str, str]] = []


def _report(status: str, name: str, detail: str, ms: float | None = None) -> None:
    latency = f"{ms:7.1f} ms" if ms is not None else "     -   "
    print(f"[{status}] {latency}  {name}  {detail}")
    _results.append((status, name))


def _envelope_ok(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "body is not a JSON object"
    if payload.get("success") is not True:
        return f"success != true (error={payload.get('error')})"
    if not isinstance(payload.get("data"), (dict, list)):
        return "data missing from envelope"
    return None


def check(
    name: str,
    method: str,
    path: str,
    json_body: dict | None = None,
    validate: Callable[[httpx.Response, Any], str | None] = lambda r, p: None,
) -> None:
    url = BASE_URL + path
    start = time.perf_counter()
    try:
        response = httpx.request(method, url, json=json_body, timeout=60.0)
    except Exception as exc:
        _report(FAIL, name, f"request failed: {exc!r}")
        return
    ms = (time.perf_counter() - start) * 1000

    if response.status_code == 404:
        _report(WARN, name, "404 — feature not yet mounted", ms)
        return

    try:
        payload = response.json()
    except Exception:
        _report(FAIL, name, f"non-JSON body (status {response.status_code})", ms)
        return

    if response.status_code != 200:
        _report(FAIL, name, f"status {response.status_code}: {payload}", ms)
        return

    problem = validate(response, payload)
    if problem:
        _report(FAIL, name, problem, ms)
    else:
        _report(PASS, name, "ok", ms)


def main() -> int:
    print(f"StudyOS smoke test → {BASE_URL}\n")

    check(
        "GET  /api/health",
        "GET",
        "/api/health",
        validate=lambda r, p: _envelope_ok(p)
        or (None if p["data"].get("status") == "ok" else "data.status != 'ok'")
        or (None if p["data"].get("db") is True else "data.db is not true"),
    )
    check(
        "POST /api/chat",
        "POST",
        "/api/chat",
        json_body={"message": "hello"},
        validate=lambda r, p: (
            None
            if isinstance(p, dict) and isinstance(p.get("response"), str)
            else "expected flat {'response': str}"
        ),
    )
    check("GET  /api/roadmaps", "GET", "/api/roadmaps", validate=lambda r, p: _envelope_ok(p))
    check("GET  /api/notebooks", "GET", "/api/notebooks", validate=lambda r, p: _envelope_ok(p))
    check(
        "POST /api/quiz/generate",
        "POST",
        "/api/quiz/generate",
        json_body={"topicId": "precision-recall"},
        validate=lambda r, p: _envelope_ok(p),
    )
    check(
        "GET  /api/opportunities",
        "GET",
        "/api/opportunities",
        validate=lambda r, p: _envelope_ok(p),
    )

    passed = sum(1 for status, _ in _results if status == PASS)
    warned = sum(1 for status, _ in _results if status == WARN)
    failed = sum(1 for status, _ in _results if status == FAIL)
    print(f"\n{passed} passed, {warned} warnings, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
