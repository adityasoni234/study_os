"""Contract tests for wellbeing sessions, journal, and wisdom (Agent-Well)."""

from sqlalchemy import select

DISCLAIMER = "StudyOS offers study support, not medical or mental-health care."

WISDOM_FIELDS = {
    "id",
    "original",
    "transliteration",
    "translation",
    "source",
    "sourceNote",
    "aiReflection",
    "question",
    "verified",
    "saved",
}


def _headers(user_id: str) -> dict:
    return {"X-User-ID": user_id}


def _data(response, status_code: int = 200):
    assert response.status_code == status_code
    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    assert isinstance(body["meta"], dict)
    return body["data"]


# --- wellbeing sessions -------------------------------------------------------


def test_wellbeing_session_reset(client):
    response = client.post(
        "/api/wellbeing/session",
        json={"kind": "reset"},
        headers=_headers("well-reset-user"),
    )
    data = _data(response)
    assert isinstance(data["reply"], str) and data["reply"].strip()
    assert data["suggestions"] == ["2-minute breath", "5-minute breath"]
    assert data["disclaimer"] == DISCLAIMER


def test_wellbeing_session_plan(client):
    response = client.post(
        "/api/wellbeing/session",
        json={"kind": "plan", "message": "This week is way too heavy."},
        headers=_headers("well-plan-user"),
    )
    data = _data(response)
    assert isinstance(data["reply"], str) and data["reply"].strip()
    # Three concrete lighter-week adjustments.
    assert isinstance(data["suggestions"], list) and len(data["suggestions"]) == 3
    assert all(isinstance(s, str) and s.strip() for s in data["suggestions"])
    assert data["disclaimer"] == DISCLAIMER


def test_wellbeing_session_talk(client):
    response = client.post(
        "/api/wellbeing/session",
        json={"kind": "talk", "message": "I feel behind on everything."},
        headers=_headers("well-talk-user"),
    )
    data = _data(response)
    assert isinstance(data["reply"], str) and data["reply"].strip()
    assert isinstance(data["suggestions"], list) and data["suggestions"]
    assert data["disclaimer"] == DISCLAIMER


def test_wellbeing_session_invalid_kind(client):
    response = client.post(
        "/api/wellbeing/session",
        json={"kind": "diagnose-me"},
        headers=_headers("well-bad-kind"),
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_talk_sessions_never_store_message_content(client, db):
    from app.models.wellbeing import WellbeingLog

    user_id = "well-privacy-user"
    secret = "very-private-feeling-xyz-123"
    for _ in range(2):
        response = client.post(
            "/api/wellbeing/session",
            json={"kind": "talk", "message": secret},
            headers=_headers(user_id),
        )
        assert response.status_code == 200

    db.expire_all()
    rows = (
        db.execute(select(WellbeingLog).where(WellbeingLog.user_id == user_id))
        .scalars()
        .all()
    )
    assert len(rows) == 2
    for row in rows:
        assert row.kind == "talk"
        assert row.note is None  # only the kind is persisted, never the message


# --- journal ------------------------------------------------------------------


def test_journal_post_then_get_returns_entry(client):
    user_id = "journal-user-one"
    created = _data(
        client.post(
            "/api/journal",
            json={"mood": "😊", "moodLabel": "Great", "note": "Finished my ML review."},
            headers=_headers(user_id),
        )
    )
    assert created["id"]
    assert created["mood"] == "😊"
    assert created["moodLabel"] == "Great"
    assert created["note"] == "Finished my ML review."
    assert created["createdAt"]

    listed = _data(client.get("/api/journal", headers=_headers(user_id)))
    assert [e["id"] for e in listed["entries"]] == [created["id"]]
    assert listed["pattern"] is None  # fewer than 3 entries — no pattern yet


def test_journal_pattern_appears_with_three_entries(client):
    user_id = "journal-user-pattern"
    for mood, label, note in [
        ("😊", "Great", "first"),
        ("😐", "Okay", "second"),
        ("😔", "Low", "third"),
    ]:
        response = client.post(
            "/api/journal",
            json={"mood": mood, "moodLabel": label, "note": note},
            headers=_headers(user_id),
        )
        assert response.status_code == 200

    listed = _data(client.get("/api/journal", headers=_headers(user_id)))
    assert len(listed["entries"]) == 3
    # Newest first.
    assert listed["entries"][0]["note"] == "third"
    assert listed["entries"][-1]["note"] == "first"
    # Gentle, non-judgmental pattern string once ≥3 entries exist.
    assert isinstance(listed["pattern"], str) and listed["pattern"].strip()
    assert listed["pattern"].startswith("Noticed gently:")


# --- wisdom -------------------------------------------------------------------


def test_wisdom_today_returns_verified_item_with_all_fields(client):
    data = _data(client.get("/api/wisdom/today", headers=_headers("wisdom-today-user")))
    assert WISDOM_FIELDS <= set(data.keys())
    assert data["verified"] is True
    assert data["saved"] is False  # fresh user has saved nothing
    for field in ("original", "transliteration", "translation", "source", "sourceNote",
                  "aiReflection", "question"):
        assert isinstance(data[field], str) and data[field].strip()


def test_wisdom_list_returns_all_seeded_items(client):
    data = _data(client.get("/api/wisdom", headers=_headers("wisdom-list-user")))
    items = data["items"]
    assert len(items) >= 3
    ids = {item["id"] for item in items}
    assert {"gita-2-47", "vidya", "gita-6-5"} <= ids
    for item in items:
        assert WISDOM_FIELDS <= set(item.keys())
        assert item["verified"] is True


def test_wisdom_save_toggles(client):
    user = _headers("wisdom-save-user")
    items = _data(client.get("/api/wisdom", headers=user))["items"]
    wisdom_id = items[0]["id"]

    saved = _data(client.post(f"/api/wisdom/{wisdom_id}/save", headers=user))
    assert saved == {"saved": True}

    listed = _data(client.get("/api/wisdom", headers=user))["items"]
    assert next(i for i in listed if i["id"] == wisdom_id)["saved"] is True

    unsaved = _data(client.post(f"/api/wisdom/{wisdom_id}/save", headers=user))
    assert unsaved == {"saved": False}


def test_wisdom_save_unknown_id_404(client):
    response = client.post(
        "/api/wisdom/not-a-real-id/save", headers=_headers("wisdom-404-user")
    )
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
