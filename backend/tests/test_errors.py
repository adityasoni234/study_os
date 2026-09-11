"""Contract tests for the error envelope, 404s, and rate limiting."""

import uuid

import pytest

_APP_ERROR_PATH = "/api/_test/app-error"


def _ensure_app_error_route():
    """Register a tiny hidden route that raises AppError (idempotent)."""
    import app.main as main
    from app.utils.errors import AppError

    already = any(
        getattr(route, "path", None) == _APP_ERROR_PATH
        for route in main.app.router.routes
    )
    if not already:

        @main.app.get(_APP_ERROR_PATH, include_in_schema=False)
        def _boom():
            raise AppError("NOT_FOUND", "Test resource was not found.", 404)


def test_unknown_route_under_api_returns_404(client):
    response = client.get(f"/api/no-such-route-{uuid.uuid4().hex}")
    assert response.status_code == 404


def test_app_error_returns_error_envelope(client):
    _ensure_app_error_route()
    response = client.get(_APP_ERROR_PATH)

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    assert isinstance(body["meta"], dict)


def test_validation_error_envelope_on_chat(client):
    """POST /api/chat without required fields → 422 VALIDATION_ERROR envelope.

    Tolerant: skipped while the chat router (another agent's lane) isn't mounted.
    """
    response = client.post("/api/chat", json={})
    if response.status_code == 404:
        pytest.skip("chat router not mounted yet (built by another agent)")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_rate_limit_returns_429_envelope():
    """Unit-level: a tiny app with limit=2 — third request is RATE_LIMITED."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.utils.ratelimit import RateLimitMiddleware

    mini = FastAPI()

    @mini.get("/api/ping")
    def ping():
        return {"pong": True}

    mini.add_middleware(RateLimitMiddleware, limit=2)

    with TestClient(mini) as mini_client:
        headers = {"X-User-ID": "rate-limit-test-user"}
        assert mini_client.get("/api/ping", headers=headers).status_code == 200
        assert mini_client.get("/api/ping", headers=headers).status_code == 200

        response = mini_client.get("/api/ping", headers=headers)
        assert response.status_code == 429
        assert response.headers.get("retry-after")
        body = response.json()
        assert body["success"] is False
        assert body["data"] is None
        assert body["error"]["code"] == "RATE_LIMITED"


def test_rate_limit_exempts_health():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.utils.ratelimit import RateLimitMiddleware

    mini = FastAPI()

    @mini.get("/api/health")
    def health():
        return {"ok": True}

    mini.add_middleware(RateLimitMiddleware, limit=1)

    with TestClient(mini) as mini_client:
        for _ in range(5):
            assert mini_client.get("/api/health").status_code == 200
