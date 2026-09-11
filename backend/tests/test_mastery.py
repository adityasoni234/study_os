"""Contract tests for mastery, daily mission and recommendations endpoints.

Runs as the seeded demo-user (default X-User-ID) whose mastery rows are seeded
by app/db/seeds/core.py and left untouched by the other test files.
"""


def test_list_mastery_includes_seeded_rows(client):
    response = client.get("/api/mastery")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    topics = body["data"]["topics"]
    assert isinstance(topics, list) and topics
    by_id = {t["topicId"]: t for t in topics}

    assert by_id["precision-recall"]["mastery"] == 65
    assert by_id["precision-recall"]["trend"] == "up"
    assert by_id["precision-recall"]["title"] == "Precision & Recall"
    assert by_id["confusion-matrix"]["mastery"] == 88

    for topic in topics:
        assert set(topic.keys()) == {"topicId", "title", "mastery", "trend", "updatedAt"}
        assert topic["trend"] in ("up", "flat", "down")
        assert topic["updatedAt"]


def test_single_topic_mastery(client):
    response = client.get("/api/mastery/precision-recall")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["topicId"] == "precision-recall"
    assert data["mastery"] == 65
    assert data["title"] == "Precision & Recall"


def test_unseen_topic_mastery_is_404(client):
    response = client.get("/api/mastery/never-seen-topic")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_daily_mission_derives_from_roadmap(client):
    response = client.get("/api/daily-mission")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["topicId"] == "precision-recall"
    assert data["title"] == "Precision & Recall"
    assert data["context"] == "Machine Learning · Classification Metrics"
    assert data["minutes"] == 25
    assert isinstance(data["adaptedNote"], str) and data["adaptedNote"]

    steps = data["steps"]
    assert [s["id"] for s in steps] == ["learn", "practice", "check"]
    assert all(set(s.keys()) == {"id", "label", "done"} for s in steps)


def test_complete_mission_step_is_idempotent(client):
    response = client.post("/api/daily-mission/steps/learn/complete")
    assert response.status_code == 200
    steps = {s["id"]: s for s in response.json()["data"]["steps"]}
    assert steps["learn"]["done"] is True
    assert steps["practice"]["done"] is False

    # Completing the same step again stays done and stays 200.
    response = client.post("/api/daily-mission/steps/learn/complete")
    assert response.status_code == 200
    steps = {s["id"]: s for s in response.json()["data"]["steps"]}
    assert steps["learn"]["done"] is True


def test_complete_unknown_step_is_404(client):
    response = client.post("/api/daily-mission/steps/nope/complete")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_recommendations_are_computed_live(client):
    response = client.get("/api/recommendations")
    assert response.status_code == 200

    recs = response.json()["data"]["recommendations"]
    assert isinstance(recs, list) and len(recs) >= 3
    for rec in recs:
        assert set(rec.keys()) == {"id", "kind", "title", "reason", "topicId", "route"}
        assert rec["kind"] in ("review", "learn", "practice", "opportunity")

    kinds = [r["kind"] for r in recs]
    assert "review" in kinds and "learn" in kinds and "opportunity" in kinds

    review = next(r for r in recs if r["kind"] == "review")
    assert review["topicId"] == "roc-curves"  # seeded weakest topic (12%)
    assert review["route"].startswith("/tutor/")

    learn = next(r for r in recs if r["kind"] == "learn")
    assert learn["topicId"] == "precision-recall"  # today's mission focus

    opportunity = next(r for r in recs if r["kind"] == "opportunity")
    assert opportunity["route"] == "/opportunities"
    assert opportunity["topicId"] is None
