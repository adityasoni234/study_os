"""Contract tests for GET /api/health."""


def test_health_returns_success_envelope(client):
    response = client.get("/api/health")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    assert isinstance(body["meta"], dict)

    data = body["data"]
    assert data["status"] == "ok"
    assert data["db"] is True
    assert data["aiMode"] == "mock"  # conftest pins AI_MODE=mock
    assert data["version"] == "1.0.0"


def test_health_sets_request_id_header(client):
    response = client.get("/api/health")
    request_id = response.headers.get("x-request-id")
    assert request_id
    assert len(request_id) <= 64


def test_health_honors_incoming_request_id(client):
    response = client.get("/api/health", headers={"X-Request-ID": "smoke-abc-123"})
    assert response.headers.get("x-request-id") == "smoke-abc-123"


def test_health_rejects_malformed_request_id(client):
    response = client.get(
        "/api/health", headers={"X-Request-ID": "bad value\twith spaces"}
    )
    request_id = response.headers.get("x-request-id")
    assert request_id
    assert request_id != "bad value\twith spaces"
