"""Contract tests for quiz generate/submit + flashcards.

Quizzes here target the 'decorators' topic (python roadmap) so the mastery
updates on submit never disturb the ml-roadmap numbers asserted in
tests/test_roadmap.py. Expected mastery values are read from the live DB, not
hard-coded, so shared-session drift cannot break them.
"""

from collections import Counter

from sqlalchemy import select

from app.models import Mastery, QuizAttempt, QuizQuestion

DEMO_USER = "demo-user"
TAGS = {"Definitions", "Concepts", "Applications"}


def _data(response, status=200):
    assert response.status_code == status, response.text
    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    return body["data"]


def _error(response, status, code):
    assert response.status_code == status, response.text
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == code


def _mastery_row(db, topic_id):
    db.expire_all()
    return db.execute(
        select(Mastery).where(
            Mastery.user_id == DEMO_USER, Mastery.topic_id == topic_id
        )
    ).scalar_one_or_none()


def _generate(client, topic_id="decorators", length=5):
    return _data(
        client.post(
            "/api/quiz/generate",
            json={"topicId": topic_id, "length": length, "difficulty": "medium",
                  "focus": "mixed"},
        )
    )


# ------------------------------------------------------------------- generate


def test_generate_returns_questions_without_answers(client):
    data = _generate(client)
    assert data["quizId"]
    assert data["topicId"] == "decorators"
    questions = data["questions"]
    assert len(questions) == 5
    for question in questions:
        assert set(question) == {"id", "prompt", "options", "tag"}
        assert "correctIndex" not in question
        assert len(question["options"]) >= 2
        assert question["tag"] in TAGS


def test_generate_requires_topic_or_notebook(client):
    _error(client.post("/api/quiz/generate", json={}), 422, "VALIDATION_ERROR")


def test_generate_clamps_length(client):
    data = _generate(client, length=1)  # clamped up to 3
    assert 3 <= len(data["questions"]) <= 8


# --------------------------------------------------------------------- submit


def test_submit_grades_and_updates_mastery(client, db):
    data = _generate(client)
    quiz_id = data["quizId"]

    db.expire_all()
    questions = (
        db.execute(
            select(QuizQuestion)
            .where(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.position)
        )
        .scalars()
        .all()
    )
    assert len(questions) == 5

    # Answer everything right except one question with a UNIQUE tag, so the
    # expected weaknesses list is exactly that tag (mock tags make this exist).
    tag_counts = Counter(q.tag for q in questions)
    wrong_q = next(q for q in questions if tag_counts[q.tag] == 1)
    answers = [
        {
            "questionId": q.id,
            "selectedIndex": q.correct_index
            if q.id != wrong_q.id
            else (q.correct_index + 1) % len(q.options),
        }
        for q in questions
    ]

    before_row = _mastery_row(db, "decorators")
    before = int(before_row.value) if before_row is not None else 0
    expected_after = max(before, min(95, before + 8))  # 4/5 = 0.8 → +8

    result = _data(client.post(f"/api/quiz/{quiz_id}/submit", json={"answers": answers}))
    assert result["score"] == 4
    assert result["total"] == 5
    assert result["masteryBefore"] == before
    assert result["masteryAfter"] == expected_after
    assert result["masteryAfter"] > result["masteryBefore"]

    per_question = {p["questionId"]: p for p in result["perQuestion"]}
    assert set(per_question) == {q.id for q in questions}
    for q in questions:
        entry = per_question[q.id]
        assert set(entry) == {"questionId", "correct", "correctIndex", "explanation"}
        assert entry["correctIndex"] == q.correct_index
        assert entry["correct"] is (q.id != wrong_q.id)

    assert wrong_q.tag in result["weaknesses"]
    assert wrong_q.tag not in result["strengths"]
    fully_correct_tags = {q.tag for q in questions if q.tag != wrong_q.tag}
    assert fully_correct_tags <= set(result["strengths"])

    assert result["recommendation"] == {
        "title": "Practice weak areas",
        "route": "/quiz/decorators",
    }

    # Mastery row was written through (source of truth) and attempt persisted.
    row = _mastery_row(db, "decorators")
    assert row is not None
    assert int(row.value) == expected_after
    assert row.trend == "up"
    db.expire_all()
    attempt = db.execute(
        select(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id)
    ).scalar_one()
    assert attempt.score == 4
    assert attempt.total == 5
    assert wrong_q.tag in attempt.weaknesses


def test_submit_perfect_score_keeps_momentum(client, db):
    data = _generate(client, topic_id="structured-answers")
    quiz_id = data["quizId"]
    db.expire_all()
    questions = (
        db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id))
        .scalars()
        .all()
    )
    answers = [
        {"questionId": q.id, "selectedIndex": q.correct_index} for q in questions
    ]
    result = _data(client.post(f"/api/quiz/{quiz_id}/submit", json={"answers": answers}))
    assert result["score"] == result["total"] == len(questions)
    assert result["weaknesses"] == []
    assert result["recommendation"] == {"title": "Keep the momentum", "route": "/"}


def test_submit_unknown_quiz_is_404(client):
    _error(
        client.post("/api/quiz/not-a-quiz/submit", json={"answers": []}),
        404,
        "NOT_FOUND",
    )


def test_submit_unknown_question_is_validation_error(client):
    quiz_id = _generate(client)["quizId"]
    _error(
        client.post(
            f"/api/quiz/{quiz_id}/submit",
            json={"answers": [{"questionId": "bogus", "selectedIndex": 0}]},
        ),
        422,
        "VALIDATION_ERROR",
    )


# ----------------------------------------------------------------- flashcards


def test_flashcards_generate(client, db):
    data = _data(
        client.post(
            "/api/flashcards/generate", json={"topicId": "roc-curves", "count": 6}
        )
    )
    cards = data["cards"]
    assert len(cards) == 6
    for card in cards:
        assert set(card) == {"id", "front", "back", "weak"}
        assert card["front"] and card["back"]
    row = _mastery_row(db, "roc-curves")
    mastery = int(row.value) if row is not None else 0
    if mastery < 70:  # weak topic → first half of the deck flagged weak
        assert cards[0]["weak"] is True
        assert any(c["weak"] for c in cards)
    assert all(c["weak"] is False for c in cards[len(cards) // 2:] or [cards[-1]])


def test_flashcards_require_topic_or_notebook(client):
    _error(client.post("/api/flashcards/generate", json={}), 422, "VALIDATION_ERROR")
