"""Daily mission + live recommendations.

The mission is derived from the user's primary roadmap (its next current
topic), created once per UTC day and then mutated in place as steps complete.
Recommendations are computed live from mastery + the mission — no rows stored.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning import DailyMission, Topic
from app.models.roadmap import Roadmap, RoadmapNode
from app.models.user import User
from app.schemas.learning import MissionOut, MissionStepOut, RecommendationOut
from app.services import mastery as mastery_service
from app.utils.errors import NotFound

# Deterministic fallback (matches the seeded demo roadmap "ml").
FALLBACK_TOPIC_ID = "precision-recall"
FALLBACK_TITLE = "Precision & Recall"
FALLBACK_CONTEXT = "Machine Learning · Classification Metrics"
DEFAULT_MINUTES = 25

_DEFAULT_STEPS: list[dict] = [
    {"id": "learn", "label": "Learn the concept with your tutor", "done": False},
    {"id": "practice", "label": "Practice 5 questions", "done": False},
    {"id": "check", "label": "Complete the mastery check", "done": False},
]


def _today() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


def _pick_roadmap(db: Session, user_id: str) -> Roadmap | None:
    """The user's primary roadmap: prefer a Subject roadmap with a next topic."""
    rows = (
        db.execute(
            select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.archived.is_(False))
        )
        .scalars()
        .all()
    )
    candidates = [r for r in rows if r.next_topic_id] or rows
    if not candidates:
        return None
    # Deterministic preference: the main Subject roadmap first, established
    # (not just-created) roadmaps before new ones, id as the final tiebreak.
    candidates.sort(key=lambda r: (r.type != "Subject", bool(r.is_new), r.id))
    return candidates[0]


def _mission_minutes(db: Session, roadmap: Roadmap, topic: Topic) -> int:
    """Minutes from the roadmap's current subtopic node for this topic, else 25."""
    node = db.execute(
        select(RoadmapNode)
        .where(
            RoadmapNode.roadmap_id == roadmap.id,
            RoadmapNode.topic_id == topic.id,
            RoadmapNode.status == "current",
            RoadmapNode.kind == "subtopic",
        )
        .order_by(RoadmapNode.position.asc())
    ).scalars().first()
    if node is not None and node.minutes:
        return int(node.minutes)
    return DEFAULT_MINUTES


def get_or_create(db: Session, user: User) -> DailyMission:
    """Today's mission for the user, derived from their roadmap on first call."""
    today = _today()
    mission = db.execute(
        select(DailyMission)
        .where(DailyMission.user_id == user.id, DailyMission.date == today)
        .order_by(DailyMission.id.asc())
    ).scalars().first()
    if mission is not None:
        return mission

    roadmap = _pick_roadmap(db, user.id)
    topic: Topic | None = None
    if roadmap is not None and roadmap.next_topic_id:
        topic = mastery_service.resolve_topic(db, roadmap.next_topic_id)

    if topic is None:
        topic = mastery_service.ensure_topic(db, FALLBACK_TOPIC_ID, FALLBACK_TITLE)
        context = FALLBACK_CONTEXT
        minutes = DEFAULT_MINUTES
        adapted_note = (
            f"Today is a focused {DEFAULT_MINUTES}-minute session on {topic.title} — "
            "small, steady steps beat marathon cramming."
        )
    else:
        context_parts = [roadmap.title]
        if roadmap.focus:
            context_parts.append(roadmap.focus)
        context = " · ".join(context_parts)
        minutes = _mission_minutes(db, roadmap, topic)
        adapted_note = roadmap.adapted_note or (
            f"Today's {minutes}-minute mission moves {roadmap.title} forward: "
            f"{topic.title} is your current step."
        )

    mission = DailyMission(
        user_id=user.id,
        date=today,
        topic_id=topic.id,
        title=topic.title,
        context=context,
        minutes=minutes,
        steps=[dict(step) for step in _DEFAULT_STEPS],
        adapted_note=adapted_note,
    )
    db.add(mission)
    db.flush()
    return mission


def complete_step(db: Session, user: User, step_id: str) -> MissionOut:
    """Mark one mission step done (idempotent); returns the updated mission."""
    mission = get_or_create(db, user)
    steps = [dict(step) for step in (mission.steps or [])]
    if not any(step.get("id") == step_id for step in steps):
        raise NotFound("Mission step")
    for step in steps:
        if step.get("id") == step_id:
            step["done"] = True
    mission.steps = steps  # reassign so the JSON column change is tracked
    db.flush()
    return to_out(db, mission)


def to_out(db: Session, mission: DailyMission) -> MissionOut:
    topic = db.get(Topic, mission.topic_id)
    topic_id = (topic.slug or topic.id) if topic is not None else mission.topic_id
    return MissionOut(
        topic_id=topic_id,
        title=mission.title,
        context=mission.context,
        minutes=int(mission.minutes or DEFAULT_MINUTES),
        steps=[
            MissionStepOut(
                id=str(step.get("id", "")),
                label=str(step.get("label", "")),
                done=bool(step.get("done", False)),
            )
            for step in (mission.steps or [])
        ],
        adapted_note=mission.adapted_note or "",
    )


def recommendations(db: Session, user: User) -> list[RecommendationOut]:
    """Live recommendations: review the weakest topic, continue the mission,
    and check matching opportunities."""
    mission = get_or_create(db, user)
    mission_out = to_out(db, mission)
    recs: list[RecommendationOut] = []

    weak = mastery_service.weak_topics(db, user.id, below=60, limit=3)
    weakest = next((w for w in weak if w.topic_id != mission_out.topic_id), None)
    if weakest is not None:
        trend_note = " and slipping" if weakest.trend == "down" else ""
        recs.append(
            RecommendationOut(
                id=f"rec-review-{weakest.topic_id}",
                kind="review",
                title=f"Review {weakest.title}",
                reason=f"Mastery is at {weakest.mastery}%{trend_note} — a short review will lift it.",
                topic_id=weakest.topic_id,
                route=f"/tutor/{weakest.topic_id}",
            )
        )

    recs.append(
        RecommendationOut(
            id=f"rec-learn-{mission_out.topic_id}",
            kind="learn",
            title=f"Continue {mission_out.title}",
            reason=f"It's today's mission focus ({mission_out.context}).",
            topic_id=mission_out.topic_id,
            route=f"/tutor/{mission_out.topic_id}",
        )
    )

    recs.append(
        RecommendationOut(
            id="rec-opportunity",
            kind="opportunity",
            title="Explore opportunities that match your skills",
            reason="Hackathons and internships matched to your progress have deadlines coming up.",
            topic_id=None,
            route="/opportunities",
        )
    )
    return recs
