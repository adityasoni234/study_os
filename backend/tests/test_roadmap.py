"""Contract tests for Roadmaps, plus content + growth smoke checks (this lane).

Seed-dependent numbers (mastery values) are read from the live DB rather than
hard-coded, so these tests stay correct even when earlier test files in the
shared session have already moved mastery around.
"""

from sqlalchemy import select

from app.models import Mastery

DEMO_USER = "demo-user"

ROADMAP_BASE_KEYS = {
    "id", "title", "type", "tone", "icon", "goal", "targetDate", "progress",
    "focus", "nextAction", "nextTopicId", "adaptedNote", "isNew",
}
TOPIC_KEYS = {"id", "title", "status", "mastery", "minutes", "summary", "subtopics", "note"}


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
    return body["error"]


def _mastery_value(db, topic_id: str) -> int:
    db.expire_all()
    value = db.execute(
        select(Mastery.value).where(
            Mastery.user_id == DEMO_USER, Mastery.topic_id == topic_id
        )
    ).scalar_one_or_none()
    return int(value) if value is not None else 0


def _create_roadmap(client, goal="Learn machine learning from scratch"):
    response = client.post(
        "/api/roadmaps",
        json={
            "goal": goal,
            "type": "Subject",
            "level": "Beginner",
            "hoursPerWeek": 5,
            "deadline": "Dec 20",
            "knownTopics": ["python"],
        },
    )
    return _data(response)


# ------------------------------------------------------------------- roadmaps


def test_list_roadmaps_includes_seeds(client):
    data = _data(client.get("/api/roadmaps"))
    roadmaps = data["roadmaps"]
    ids = {r["id"] for r in roadmaps}
    assert "ml" in ids
    assert len(roadmaps) >= 4
    for roadmap in roadmaps:
        assert "milestones" not in roadmap  # list view is milestone-free
        assert ROADMAP_BASE_KEYS <= set(roadmap)
        assert isinstance(roadmap["progress"], int)
        assert 0 <= roadmap["progress"] <= 100


def test_ml_detail_matches_contract(client, db):
    data = _data(client.get("/api/roadmaps/ml"))
    assert ROADMAP_BASE_KEYS <= set(data)
    assert data["title"] == "Machine Learning"
    assert data["nextTopicId"] == "precision-recall"

    milestones = data["milestones"]
    assert [m["id"] for m in milestones] == ["ml-m1", "ml-m2", "ml-m3", "ml-m4"]
    for milestone in milestones:
        assert {"id", "title", "status", "topics"} <= set(milestone)
        assert milestone["status"] in ("done", "current", "locked")
        for topic in milestone["topics"]:
            assert TOPIC_KEYS <= set(topic)

    m2 = milestones[1]
    assert m2["status"] == "current"
    metrics = next(t for t in m2["topics"] if t["id"] == "classification-metrics")
    assert metrics["status"] == "current"
    # Mastery is the source of truth: the node links topic_id 'precision-recall'.
    assert metrics["mastery"] == _mastery_value(db, "precision-recall")

    subtopics = metrics["subtopics"]
    assert {s["title"] for s in subtopics} == {
        "Confusion Matrix", "Precision & Recall", "ROC Curves",
    }
    by_title = {s["title"]: s["state"] for s in subtopics}
    assert by_title["Confusion Matrix"] == "done"
    assert by_title["Precision & Recall"] == "current"
    assert by_title["ROC Curves"] == "next"


def test_ml_progress_endpoint(client, db):
    data = _data(client.get("/api/roadmaps/ml/progress"))
    assert set(data) == {"progress", "topicsDone", "topicsTotal", "mastery"}
    assert data["topicsDone"] == 4
    assert data["topicsTotal"] == 11

    # Weighted rule: (done-or-review topics + current mastery/100) over the 8
    # topics in the unlocked milestones (m1: 3, m2: 5). Fresh seeds → 71.
    pr = _mastery_value(db, "precision-recall")
    assert data["progress"] == round(100 * (5 + pr / 100) / 8)
    assert data["mastery"]["precision-recall"] == pr
    assert "linear-regression" in data["mastery"]


def test_create_roadmap_persists_full_tree(client):
    data = _create_roadmap(client)
    roadmap_id = data["id"]
    assert roadmap_id
    assert data["isNew"] is True
    assert data["goal"] == "Learn machine learning from scratch"
    assert data["targetDate"] == "Dec 20"
    assert data["type"] == "Subject"

    milestones = data["milestones"]
    assert len(milestones) >= 2
    assert milestones[0]["status"] == "current"
    assert all(m["status"] == "locked" for m in milestones[1:])

    topics = [t for m in milestones for t in m["topics"]]
    assert topics
    assert milestones[0]["topics"][0]["status"] == "current"
    assert all(t["status"] in ("current", "locked") for t in topics)
    assert sum(1 for t in topics if t["status"] == "current") == 1
    for topic in topics:
        assert TOPIC_KEYS <= set(topic)
        assert isinstance(topic["minutes"], int)
        for sub in topic["subtopics"]:
            assert set(sub) == {"title", "state"}
            assert sub["state"] in ("done", "current", "next")

    # Round-trips: detail and list both see the persisted roadmap.
    detail = _data(client.get(f"/api/roadmaps/{roadmap_id}"))
    assert detail["id"] == roadmap_id
    assert len(detail["milestones"]) == len(milestones)
    listed = _data(client.get("/api/roadmaps"))
    assert roadmap_id in {r["id"] for r in listed["roadmaps"]}


def test_patch_roadmap_and_archive(client):
    roadmap_id = _create_roadmap(client, goal="Ace the statistics exam")["id"]

    patched = _data(
        client.patch(f"/api/roadmaps/{roadmap_id}", json={"targetDate": "Jan 5"})
    )
    assert patched["targetDate"] == "Jan 5"
    assert _data(client.get(f"/api/roadmaps/{roadmap_id}"))["targetDate"] == "Jan 5"

    goal_patch = _data(
        client.patch(f"/api/roadmaps/{roadmap_id}", json={"goal": "New goal"})
    )
    assert goal_patch["goal"] == "New goal"

    archived = _data(
        client.patch(f"/api/roadmaps/{roadmap_id}", json={"archived": True})
    )
    assert archived["id"] == roadmap_id
    listed = _data(client.get("/api/roadmaps"))
    assert roadmap_id not in {r["id"] for r in listed["roadmaps"]}
    # Detail remains reachable for archived roadmaps.
    assert _data(client.get(f"/api/roadmaps/{roadmap_id}"))["id"] == roadmap_id


def test_unknown_roadmap_is_404_envelope(client):
    _error(client.get("/api/roadmaps/definitely-not-here"), 404, "NOT_FOUND")
    _error(client.get("/api/roadmaps/definitely-not-here/progress"), 404, "NOT_FOUND")
    _error(
        client.patch("/api/roadmaps/definitely-not-here", json={"goal": "x"}),
        404,
        "NOT_FOUND",
    )


# ------------------------------------------------------- content smoke checks


def test_study_guide_requires_a_source(client):
    _error(client.post("/api/study-guide/generate", json={}), 422, "VALIDATION_ERROR")


def test_study_guide_generates_sections(client):
    data = _data(
        client.post("/api/study-guide/generate", json={"topicId": "precision-recall"})
    )
    assert isinstance(data["title"], str) and data["title"]
    assert data["sections"]
    kinds = {
        "overview", "concepts", "definitions", "formulas", "examples",
        "mistakes", "tips", "practice", "revision",
    }
    for section in data["sections"]:
        assert set(section) == {"id", "title", "kind", "markdown", "citations"}
        assert section["kind"] in kinds
        assert isinstance(section["citations"], list)


def test_mindmap_generates_with_mastery_links(client, db):
    data = _data(client.post("/api/mindmap/generate", json={"topicId": "precision-recall"}))
    assert data["center"]
    assert data["nodes"]
    for node in data["nodes"]:
        assert set(node) == {"id", "label", "parentId", "mastery", "topicId"}
    # The mock map contains a "Precision & Recall" node whose slug matches the
    # seeded topic — it must resolve topicId + mastery through the Mastery table.
    linked = next(n for n in data["nodes"] if n["label"] == "Precision & Recall")
    assert linked["topicId"] == "precision-recall"
    assert linked["mastery"] == _mastery_value(db, "precision-recall")
    unlinked = next(n for n in data["nodes"] if n["topicId"] is None)
    assert unlinked["mastery"] is None


def test_studycast_generates_dialogue(client):
    data = _data(
        client.post(
            "/api/studycast/generate", json={"topicId": "what-is-rag", "minutes": 5}
        )
    )
    assert set(data) == {"id", "title", "minutes", "lines", "audioUrl"}
    assert data["minutes"] == 5
    assert data["audioUrl"] is None
    assert data["lines"]
    assert {line["speaker"] for line in data["lines"]} <= {"A", "B"}


# -------------------------------------------------------- growth smoke checks


def test_growth_shape(client):
    data = _data(client.get("/api/growth"))
    assert set(data) == {"dimensions", "week", "streakDays", "insights", "nextStep"}
    ids = [d["id"] for d in data["dimensions"]]
    assert ids == ["learning", "skills", "goals", "wellbeing", "inner"]
    for dim in data["dimensions"]:
        assert set(dim) == {"id", "label", "value", "delta", "tone"}
        assert 0 <= dim["value"] <= 100
        assert dim["tone"] in ("indigo", "sky", "amber", "mint", "violet")
    assert len(data["week"]) == 7
    for day in data["week"]:
        assert set(day) == {"day", "minutes"}
    assert isinstance(data["streakDays"], int)
    kinds = {i["kind"] for i in data["insights"]}
    assert kinds <= {"strongest", "improving", "attention"}
    assert {"title", "reason", "route"} == set(data["nextStep"])
    assert data["nextStep"]["route"].startswith("/")


def test_knowledge_map_groups_topics(client, db):
    data = _data(client.get("/api/knowledge-map"))
    areas = data["areas"]
    assert areas
    for area in areas:
        assert set(area) == {"id", "title", "icon", "tone", "topics"}
        for topic in area["topics"]:
            assert set(topic) == {"topicId", "title", "mastery", "route"}
            assert topic["route"] == f"/tutor/{topic['topicId']}"
    all_topic_ids = {t["topicId"] for a in areas for t in a["topics"]}
    assert "precision-recall" in all_topic_ids
    db.expire_all()
    ml_area = next(a for a in areas if a["id"] == "machine-learning")
    pr = next(t for t in ml_area["topics"] if t["topicId"] == "precision-recall")
    assert pr["mastery"] == _mastery_value(db, "precision-recall")
    # Topics without a Mastery row fall back to 0, never null.
    topic_ids_with_rows = {
        row for (row,) in db.execute(
            select(Mastery.topic_id).where(Mastery.user_id == DEMO_USER)
        )
    }
    for area in areas:
        for topic in area["topics"]:
            if topic["topicId"] not in topic_ids_with_rows:
                assert topic["mastery"] == 0
