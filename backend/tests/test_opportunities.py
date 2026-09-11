"""Contract tests for opportunities: tabs + explainable match, save, prepare."""

HACKATHON_ID = "hackathon-ai-ed"

ALL_IDS = {
    "hackathon-ai-ed",
    "kaggle-classification",
    "research-internship",
    "gsoc-prep",
    "ai-scholarship",
    "campus-fellowship",
}

ITEM_KEYS = {
    "id", "title", "org", "type", "tone", "deadline", "daysLeft", "mode",
    "blurb", "eligibility", "source", "sourceUrl", "verified", "match", "saved",
}


def _data(response, status=200):
    assert response.status_code == status, response.text
    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    return body["data"]


def _find(items, opp_id):
    return next(item for item in items if item["id"] == opp_id)


# --- listing + matching ------------------------------------------------------


def test_list_returns_six_opportunities_per_contract(client):
    items = _data(client.get("/api/opportunities"))["opportunities"]
    assert len(items) == 6
    assert {item["id"] for item in items} == ALL_IDS
    for item in items:
        assert ITEM_KEYS <= set(item.keys())
        assert isinstance(item["verified"], bool) and item["verified"] is True
        assert item["sourceUrl"] == "https://" + item["source"]
        assert isinstance(item["saved"], bool)
        match = item["match"]
        assert isinstance(match["score"], int)
        assert 0 <= match["score"] <= 100
        assert isinstance(match["reasons"], list)
        assert isinstance(match["gaps"], list)


def test_hackathon_match_is_high_and_explainable(client):
    items = _data(client.get("/api/opportunities?tab=best"))["opportunities"]
    hackathon = _find(items, HACKATHON_ID)
    match = hackathon["match"]
    assert match["score"] >= 90
    assert match["score"] == 94  # tuned constant for the seeded demo-user
    assert match["reasons"], "reasons must be non-empty"
    assert match["gaps"], "gaps must be non-empty"
    assert any("RAG" in gap for gap in match["gaps"])
    # best tab leads with the strongest match
    assert items[0]["id"] == HACKATHON_ID
    scores = [item["match"]["score"] for item in items]
    assert scores == sorted(scores, reverse=True)


def test_match_is_stable_across_calls(client):
    first = _data(client.get(f"/api/opportunities/{HACKATHON_ID}"))["match"]
    second = _data(client.get(f"/api/opportunities/{HACKATHON_ID}"))["match"]
    assert first == second


def test_closing_tab_sorts_days_left_asc_nulls_last(client):
    items = _data(client.get("/api/opportunities?tab=closing"))["opportunities"]
    assert [item["daysLeft"] for item in items] == [7, 19, 21, 29, None, None]


def test_new_tab_returns_three(client):
    items = _data(client.get("/api/opportunities?tab=new"))["opportunities"]
    assert len(items) == 3


def test_invalid_tab_is_validation_error(client):
    response = client.get("/api/opportunities?tab=bogus")
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_opportunity_404(client):
    response = client.get("/api/opportunities/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# --- save toggle -------------------------------------------------------------


def test_save_toggles_and_appears_in_saved_tab(client):
    headers = {"X-User-ID": "save-tester"}

    assert _data(client.post(f"/api/opportunities/{HACKATHON_ID}/save", headers=headers)) == {
        "saved": True
    }
    saved_items = _data(client.get("/api/opportunities?tab=saved", headers=headers))[
        "opportunities"
    ]
    assert [item["id"] for item in saved_items] == [HACKATHON_ID]
    assert saved_items[0]["saved"] is True

    # toggles off again
    assert _data(client.post(f"/api/opportunities/{HACKATHON_ID}/save", headers=headers)) == {
        "saved": False
    }
    assert (
        _data(client.get("/api/opportunities?tab=saved", headers=headers))["opportunities"] == []
    )


def test_save_unknown_opportunity_404(client):
    response = client.post("/api/opportunities/nope/save")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# --- prepare -----------------------------------------------------------------


def test_prepare_hackathon_creates_hand_authored_six_day_plan(client):
    plan = _data(client.post(f"/api/opportunities/{HACKATHON_ID}/prepare"))
    assert plan["opportunityId"] == HACKATHON_ID
    assert plan["daysRemaining"] == 6
    assert plan["readiness"] == 72
    assert "RAG" in plan["gapNote"]

    days = plan["days"]
    assert [day["day"] for day in days] == [1, 2, 3, 4, 5, 6]
    assert days[0]["title"] == "Understand the problem space"
    assert days[5]["title"] == "Submit with margin"

    day2 = days[1]
    assert day2["title"] == "Learn RAG fundamentals"
    assert day2["tutorTopicId"] == "what-is-rag"
    assert day2["note"] and "RAG is new to you" in day2["note"]

    for day in days:
        assert isinstance(day["minutes"], int) and day["minutes"] > 0
        assert len(day["tasks"]) == 3
        for task in day["tasks"]:
            assert task["id"]
            assert task["label"]
            assert task["done"] is False


def test_task_toggle_raises_and_lowers_readiness(client):
    plan = _data(client.post(f"/api/opportunities/{HACKATHON_ID}/prepare"))
    task_id = plan["days"][0]["tasks"][0]["id"]

    toggled = _data(client.post(f"/api/prepare/tasks/{task_id}/toggle"))
    assert toggled["done"] is True
    assert toggled["readiness"] == 73  # 72 + 25 * 1/18 rounded

    reverted = _data(client.post(f"/api/prepare/tasks/{task_id}/toggle"))
    assert reverted["done"] is False
    assert reverted["readiness"] == 72


def test_second_prepare_returns_same_plan_and_preserves_done(client):
    first = _data(client.post(f"/api/opportunities/{HACKATHON_ID}/prepare"))
    task_id = first["days"][0]["tasks"][0]["id"]
    _data(client.post(f"/api/prepare/tasks/{task_id}/toggle"))

    second = _data(client.post(f"/api/opportunities/{HACKATHON_ID}/prepare"))
    first_ids = [t["id"] for day in first["days"] for t in day["tasks"]]
    second_ids = [t["id"] for day in second["days"] for t in day["tasks"]]
    assert first_ids == second_ids  # same persisted plan, same order
    assert [d["title"] for d in first["days"]] == [d["title"] for d in second["days"]]

    done_flags = {t["id"]: t["done"] for day in second["days"] for t in day["tasks"]}
    assert done_flags[task_id] is True
    assert second["readiness"] == 73


def test_toggle_foreign_task_is_404(client):
    plan = _data(client.post(f"/api/opportunities/{HACKATHON_ID}/prepare"))
    task_id = plan["days"][0]["tasks"][1]["id"]
    response = client.post(
        f"/api/prepare/tasks/{task_id}/toggle", headers={"X-User-ID": "intruder"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_toggle_unknown_task_is_404(client):
    response = client.post("/api/prepare/tasks/does-not-exist/toggle")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_prepare_generates_plan_for_other_opportunities(client):
    plan = _data(client.post("/api/opportunities/kaggle-classification/prepare"))
    assert plan["opportunityId"] == "kaggle-classification"
    assert plan["readiness"] == 72
    assert 4 <= len(plan["days"]) <= 6
    assert plan["daysRemaining"] == len(plan["days"])
    for day in plan["days"]:
        assert day["title"]
        assert isinstance(day["minutes"], int) and day["minutes"] > 0
        assert day["tasks"], "every generated day needs at least one task"

    # idempotent for generated plans too
    again = _data(client.post("/api/opportunities/kaggle-classification/prepare"))
    assert [d["title"] for d in again["days"]] == [d["title"] for d in plan["days"]]
    assert [t["id"] for d in again["days"] for t in d["tasks"]] == [
        t["id"] for d in plan["days"] for t in d["tasks"]
    ]
