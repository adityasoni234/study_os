"""Mastery — the single source of learner state per (user, topic).

Gentle-by-design update rules (this is a tutor, not a leaderboard):
- correct answer: +5, capped at 95 through the tutor path (a mastery check,
  not day-to-day tutoring, is what earns the last few points),
- wrong answer: -2, floored at 5 (one bad day never zeroes a topic),
- trend reflects the latest movement: up / down / flat.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.common import utcnow
from app.models.learning import Mastery, Topic
from app.schemas.learning import MasteryTopicOut
from app.utils.errors import NotFound

TUTOR_CAP = 95  # correct answers via tutoring never push past this
FLOOR = 5  # wrong answers never drop below this
CORRECT_DELTA = 5
WRONG_DELTA = -2


def humanize_slug(slug: str) -> str:
    """"precision-recall" -> "Precision Recall" (fallback title for unknown slugs)."""
    return slug.replace("-", " ").replace("_", " ").strip().title() or slug


def resolve_topic(db: Session, topic_id: str) -> Topic | None:
    """Find a Topic by primary key or slug (seeded topic ids ARE their slugs)."""
    topic = db.get(Topic, topic_id)
    if topic is not None:
        return topic
    return db.execute(select(Topic).where(Topic.slug == topic_id)).scalar_one_or_none()


def ensure_topic(db: Session, topic_id: str, title: str | None = None) -> Topic:
    """Return the Topic for this id/slug, creating a minimal row if unknown."""
    topic = resolve_topic(db, topic_id)
    if topic is not None:
        return topic
    slug = topic_id.strip()[:120]
    topic = Topic(id=slug[:32], slug=slug, title=(title or humanize_slug(slug))[:200])
    db.add(topic)
    db.flush()
    return topic


def get_or_create(db: Session, user_id: str, topic_id: str) -> Mastery:
    """Return the Mastery row for (user, topic), creating topic and row if needed."""
    topic = ensure_topic(db, topic_id)
    row = db.execute(
        select(Mastery).where(Mastery.user_id == user_id, Mastery.topic_id == topic.id)
    ).scalar_one_or_none()
    if row is None:
        row = Mastery(user_id=user_id, topic_id=topic.id, value=0, trend="flat")
        db.add(row)
        db.flush()
    return row


def apply_result(
    db: Session,
    user_id: str,
    topic_id: str,
    correct: bool | None,
    quality: float | None = None,
) -> tuple[Mastery, int]:
    """Apply one learning signal; returns (row, delta actually applied).

    ``correct`` drives the gentle +5/-2 rules. When ``correct`` is None a
    ``quality`` score in [0, 1] may nudge mastery instead (0.5 is neutral).
    """
    row = get_or_create(db, user_id, topic_id)
    old = int(row.value or 0)

    if correct is True:
        new = min(max(old, TUTOR_CAP), old + CORRECT_DELTA)
    elif correct is False:
        new = max(min(old, FLOOR), old + WRONG_DELTA)
    elif quality is not None:
        nudge = round((max(0.0, min(1.0, quality)) - 0.5) * 8)  # -4 .. +4
        if nudge > 0:
            new = min(max(old, TUTOR_CAP), old + nudge)
        else:
            new = max(min(old, FLOOR), old + nudge)
    else:
        new = old

    delta = new - old
    row.value = new
    row.trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
    row.updated_at = utcnow()
    db.flush()
    return row, delta


def _summary(row: Mastery, topic: Topic) -> MasteryTopicOut:
    return MasteryTopicOut(
        topic_id=topic.slug or topic.id,
        title=topic.title,
        mastery=int(row.value or 0),
        trend=row.trend or "flat",
        updated_at=row.updated_at,
    )


def list_summary(db: Session, user_id: str) -> list[MasteryTopicOut]:
    """All mastery rows for the user, joined with topic titles, stable order."""
    rows = db.execute(
        select(Mastery, Topic)
        .join(Topic, Topic.id == Mastery.topic_id)
        .where(Mastery.user_id == user_id)
        .order_by(Topic.title.asc())
    ).all()
    return [_summary(row, topic) for row, topic in rows]


def topic_summary(db: Session, user_id: str, topic_id: str) -> MasteryTopicOut:
    """One topic's mastery for the user; NotFound if the topic was never seen."""
    topic = resolve_topic(db, topic_id)
    if topic is None:
        raise NotFound("Mastery for this topic")
    row = db.execute(
        select(Mastery).where(Mastery.user_id == user_id, Mastery.topic_id == topic.id)
    ).scalar_one_or_none()
    if row is None:
        raise NotFound("Mastery for this topic")
    return _summary(row, topic)


def weak_topics(db: Session, user_id: str, below: int = 60, limit: int = 3) -> list[MasteryTopicOut]:
    """The user's weakest topics under ``below``, weakest first (tutor context)."""
    rows = db.execute(
        select(Mastery, Topic)
        .join(Topic, Topic.id == Mastery.topic_id)
        .where(Mastery.user_id == user_id, Mastery.value < below)
        .order_by(Mastery.value.asc(), Topic.title.asc())
        .limit(limit)
    ).all()
    return [_summary(row, topic) for row, topic in rows]
