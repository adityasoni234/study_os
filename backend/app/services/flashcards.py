"""Flashcard generation: AI (FLASHCARDS task) → persisted Flashcard rows.

Cards on a topic whose mastery is below 70 mark the first half as weak=True so
the frontend can front-load the shaky material.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts, router as ai_router
from app.ai.base import TaskType
from app.models import Flashcard, Mastery, Notebook, User
from app.services.roadmap import get_or_create_topic
from app.utils.errors import AppError, NotFound
from app.utils.ids import new_id

_CARDS_SCHEMA_HINT = (
    'Return ONLY a JSON object shaped exactly like: {"cards": [{"front": "...", "back": "..."}]}'
)


def _clean_cards(raw, limit: int) -> list[dict]:
    cleaned: list[dict] = []
    if not isinstance(raw, list):
        return cleaned
    for item in raw:
        if len(cleaned) >= limit:
            break
        if not isinstance(item, dict):
            continue
        front = str(item.get("front") or "").strip()
        back = str(item.get("back") or "").strip()
        if front and back:
            cleaned.append({"front": front, "back": back})
    return cleaned


def generate_flashcards(db: Session, user: User, body) -> dict:
    if not body.topic_id and not body.notebook_id:
        raise AppError("VALIDATION_ERROR", "Provide topicId or notebookId.", 422)

    subject = "General Review"
    topic = None
    if body.notebook_id:
        notebook = db.get(Notebook, body.notebook_id)
        if notebook is None or notebook.user_id != user.id:
            raise NotFound("Notebook")
        subject = notebook.title
    if body.topic_id:
        topic = get_or_create_topic(db, body.topic_id)
        subject = topic.title

    count = max(1, min(12, int(body.count or 8)))
    data, _res = ai_router.generate_json(
        TaskType.FLASHCARDS,
        [{"role": "user", "content": prompts.flashcards_prompt(subject, count=count)}],
        schema_hint=_CARDS_SCHEMA_HINT,
    )
    specs = _clean_cards(data.get("cards") if isinstance(data, dict) else None, count)
    if not specs:
        raise AppError(
            "AI_UNAVAILABLE", "Could not build flashcards right now — please retry.", 503
        )

    mastery = 100
    if topic is not None:
        row = db.execute(
            select(Mastery.value).where(
                Mastery.user_id == user.id, Mastery.topic_id == topic.id
            )
        ).scalar_one_or_none()
        mastery = int(row) if row is not None else 0

    weak_first_half = mastery < 70
    weak_count = max(1, len(specs) // 2) if weak_first_half else 0

    rows: list[Flashcard] = []
    for i, spec in enumerate(specs):
        card = Flashcard(
            id=new_id(),
            user_id=user.id,
            topic_id=topic.id if topic else None,
            front=spec["front"],
            back=spec["back"],
            weak=i < weak_count,
        )
        db.add(card)
        rows.append(card)
    db.flush()

    return {
        "cards": [
            {"id": c.id, "front": c.front, "back": c.back, "weak": bool(c.weak)}
            for c in rows
        ]
    }
