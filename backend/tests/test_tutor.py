"""Contract tests for POST /api/tutor/message and GET /api/tutor/session/{id}.

conftest pins AI_MODE=mock, so replies come from the deterministic MockProvider.
Mutating flows (quiz feedback → mastery) run as a dedicated user so the seeded
demo-user mastery numbers stay untouched for tests/test_mastery.py.
"""

TOPIC = "precision-recall"
FEEDBACK_USER = {"X-User-ID": "tutor-fb-user"}


def _post(client, payload, headers=None):
    response = client.post("/api/tutor/message", json=payload, headers=headers or {})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    return body["data"]


def test_teach_message_matches_contract(client):
    data = _post(
        client, {"topicId": TOPIC, "message": "Teach me about precision and recall"}
    )

    assert data["sessionId"]

    reply = data["reply"]
    assert reply["role"] == "tutor"
    assert isinstance(reply["text"], str) and reply["text"].strip()
    assert isinstance(reply["citations"], list)
    assert 3 <= len(reply["suggestions"]) <= 4
    assert all(isinstance(chip, str) and chip for chip in reply["suggestions"])
    assert reply["quiz"] is None

    state = data["state"]
    assert state["topicId"] == TOPIC
    assert isinstance(state["mastery"], int)
    assert state["masteryDelta"] == 0
    assert state["mode"] == "teach"
    assert state["misconception"] is None


def test_session_persists_history_across_messages(client):
    first = _post(client, {"topicId": TOPIC, "message": "Give me the core idea first"})
    session_id = first["sessionId"]

    second = _post(
        client,
        {"sessionId": session_id, "message": "Now go one level deeper on that idea"},
    )
    assert second["sessionId"] == session_id
    assert second["state"]["topicId"] == TOPIC  # topic remembered by the session

    response = client.get(f"/api/tutor/session/{session_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == session_id
    assert data["topicId"] == TOPIC
    assert len(data["messages"]) == 4  # 2 exchanges, student + tutor each
    assert [m["role"] for m in data["messages"]] == ["student", "tutor", "student", "tutor"]
    assert isinstance(data["state"], dict)


def test_message_required_without_answer(client):
    response = client.post("/api/tutor/message", json={"topicId": TOPIC})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_session_is_404(client):
    response = client.post(
        "/api/tutor/message", json={"sessionId": "does-not-exist", "message": "hi"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

    response = client.get("/api/tutor/session/does-not-exist")
    assert response.status_code == 404


def test_foreign_session_is_404(client):
    data = _post(client, {"topicId": TOPIC, "message": "Start a session for me"})
    session_id = data["sessionId"]

    response = client.get(
        f"/api/tutor/session/{session_id}", headers={"X-User-ID": "someone-else"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_quiz_mode_returns_question_with_answer_withheld(client):
    data = _post(
        client, {"topicId": TOPIC, "message": "Quiz me on this", "mode": "quiz"}
    )

    quiz = data["reply"]["quiz"]
    assert quiz is not None
    assert quiz["questionId"]
    assert isinstance(quiz["question"], str) and quiz["question"]
    assert isinstance(quiz["options"], list) and len(quiz["options"]) >= 2
    assert quiz["correctIndex"] is None  # never leaked to the client
    assert data["state"]["mode"] == "quiz"


def test_feedback_on_correct_answer_moves_mastery(client):
    quiz_data = _post(
        client,
        {"topicId": TOPIC, "message": "Quiz me please", "mode": "quiz"},
        headers=FEEDBACK_USER,
    )
    session_id = quiz_data["sessionId"]
    quiz = quiz_data["reply"]["quiz"]
    assert quiz is not None
    mastery_before = quiz_data["state"]["mastery"]

    # Mock quiz data: the first generated question's correct index is 0.
    feedback = _post(
        client,
        {
            "sessionId": session_id,
            "topicId": TOPIC,
            "mode": "feedback",
            "questionId": quiz["questionId"],
            "answerIndex": 0,
            "message": "I pick the first option",
        },
        headers=FEEDBACK_USER,
    )

    assert feedback["reply"]["text"].strip()
    assert feedback["reply"]["quiz"] is None
    state = feedback["state"]
    assert state["mode"] == "feedback"
    assert state["masteryDelta"] != 0
    assert state["mastery"] == mastery_before + state["masteryDelta"]


def test_feedback_on_wrong_answer_is_supportive_and_names_misconception(client):
    quiz_data = _post(
        client,
        {"topicId": TOPIC, "message": "Another quiz question", "mode": "quiz"},
        headers=FEEDBACK_USER,
    )
    quiz = quiz_data["reply"]["quiz"]
    assert quiz is not None

    feedback = _post(
        client,
        {
            "sessionId": quiz_data["sessionId"],
            "topicId": TOPIC,
            "mode": "feedback",
            "questionId": quiz["questionId"],
            "answerIndex": 1,  # mock's correct index is 0 → this is wrong
            "message": "I pick the second option",
        },
        headers=FEEDBACK_USER,
    )

    assert feedback["reply"]["text"].strip()
    assert feedback["state"]["misconception"]
    assert feedback["state"]["masteryDelta"] <= 0


def test_feedback_with_unknown_question_is_404(client):
    response = client.post(
        "/api/tutor/message",
        json={
            "topicId": TOPIC,
            "mode": "feedback",
            "questionId": "no-such-question",
            "answerIndex": 0,
            "message": "answering",
        },
        headers=FEEDBACK_USER,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_explain_differently_mode(client):
    data = _post(
        client,
        {
            "topicId": TOPIC,
            "message": "Explain it simpler please",
            "mode": "explain_differently",
            "style": "analogy",
        },
    )
    assert data["reply"]["text"].strip()
    assert data["state"]["mode"] == "explain_differently"
    assert 3 <= len(data["reply"]["suggestions"]) <= 4
