"""Contract tests for POST /api/chat — the flat competition endpoint."""


def test_chat_returns_flat_response_shape(client):
    response = client.post("/api/chat", json={"message": "Explain precision vs recall"})
    assert response.status_code == 200

    body = response.json()
    assert set(body.keys()) == {"response"}  # flat shape, no envelope
    assert isinstance(body["response"], str)
    assert body["response"].strip()


def test_chat_missing_message_is_422(client):
    response = client.post("/api/chat", json={})
    assert response.status_code == 422

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_chat_empty_message_is_422(client):
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_conversation_persists_in_rolling_session(client):
    client.post("/api/chat", json={"message": "What is a confusion matrix?"})
    client.post("/api/chat", json={"message": "And what are its four cells?"})

    # The flat endpoint runs on the fixed per-user session "chat-<user id>".
    response = client.get("/api/tutor/session/chat-demo-user")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["id"] == "chat-demo-user"
    messages = data["messages"]
    assert len(messages) >= 4  # two exchanges, student + tutor each
    roles = {m["role"] for m in messages}
    assert roles == {"student", "tutor"}
    assert all(m["text"] for m in messages)
    assert all(m["createdAt"] for m in messages)
