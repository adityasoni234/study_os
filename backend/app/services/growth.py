"""Growth dashboard + knowledge map.

The learning dimension and every insight derive from Mastery (the source of
truth); the remaining dimensions are sensible static MVP values. Week minutes
come from LearningSession durations, falling back to a seeded-looking static
week when no sessions exist yet.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LearningSession, Mastery, Profile, Subject, Topic, User
from app.schemas.growth import (
    GrowthDimension,
    GrowthInsight,
    KnowledgeArea,
    KnowledgeTopic,
    NextStep,
    WeekDay,
)

_FALLBACK_WEEK_MINUTES = [45, 30, 60, 25, 50, 20, 40]

# Heuristic buckets for the knowledge map when no Subject rows exist.
_HEURISTIC_AREAS = [
    ("python", "Python", "code", "sky", ("python", "decorator", "generator", "async")),
    ("career-skills", "Career Skills", "rocket", "violet",
     ("career", "interview", "portfolio", "communication", "structured", "resume")),
    ("machine-learning", "Machine Learning", "brain", "indigo", ()),  # catch-all
]


def _mastery_rows(db: Session, user_id: str) -> list[tuple[Topic, int, str]]:
    """[(topic, value, trend)] for every Mastery row of the user."""
    rows = db.execute(
        select(Topic, Mastery.value, Mastery.trend)
        .join(Mastery, Mastery.topic_id == Topic.id)
        .where(Mastery.user_id == user_id)
    ).all()
    return [(topic, int(value), str(trend)) for topic, value, trend in rows]


def _week(db: Session, user_id: str) -> list[WeekDay]:
    today = dt.datetime.now(dt.timezone.utc).date()
    days = [today - dt.timedelta(days=offset) for offset in range(6, -1, -1)]
    minutes = {day: 0 for day in days}

    # Date filtering happens in Python: naive-vs-aware datetime comparisons in
    # SQL differ between SQLite and Postgres, and the row count is small (MVP).
    sessions = (
        db.execute(select(LearningSession).where(LearningSession.user_id == user_id))
        .scalars()
        .all()
    )
    for session in sessions:
        started, ended = session.started_at, session.ended_at
        if started is None or ended is None:
            continue
        if started.tzinfo is None:
            started = started.replace(tzinfo=dt.timezone.utc)
        if ended.tzinfo is None:
            ended = ended.replace(tzinfo=dt.timezone.utc)
        day = started.date()
        if day in minutes and ended > started:
            minutes[day] += int((ended - started).total_seconds() // 60)

    if not any(minutes.values()):  # no sessions yet → seeded-looking static week
        return [
            WeekDay(day=day.strftime("%a"), minutes=_FALLBACK_WEEK_MINUTES[i])
            for i, day in enumerate(days)
        ]
    return [WeekDay(day=day.strftime("%a"), minutes=minutes[day]) for day in days]


def get_growth(db: Session, user: User) -> dict:
    rows = _mastery_rows(db, user.id)
    values = [value for _, value, _ in rows]
    avg_mastery = round(sum(values) / len(values)) if values else 0
    ups = sum(1 for _, _, trend in rows if trend == "up")
    downs = sum(1 for _, _, trend in rows if trend == "down")

    dimensions = [
        GrowthDimension(
            id="learning", label="Learning", value=avg_mastery,
            delta=max(-9, min(9, ups - downs)), tone="indigo",
        ),
        GrowthDimension(id="skills", label="Skills", value=71, delta=3, tone="sky"),
        GrowthDimension(id="goals", label="Goals", value=64, delta=2, tone="amber"),
        GrowthDimension(id="wellbeing", label="Wellbeing", value=76, delta=1, tone="mint"),
        GrowthDimension(id="inner", label="Inner Growth", value=58, delta=2, tone="violet"),
    ]

    profile = db.get(Profile, user.id)
    streak_days = int(profile.streak_days) if profile is not None else 0

    insights: list[GrowthInsight] = []
    next_step = NextStep(
        title="Start your first topic",
        reason="Pick any roadmap topic and the tutor will meet you there.",
        route="/",
    )
    if rows:
        strongest = max(rows, key=lambda r: r[1])
        insights.append(
            GrowthInsight(
                kind="strongest",
                title=strongest[0].title,
                detail=f"Mastery {strongest[1]} — your strongest topic right now.",
                route=f"/tutor/{strongest[0].id}",
            )
        )
        improving = [r for r in rows if r[2] == "up"]
        if improving:
            best = max(improving, key=lambda r: r[1])
            insights.append(
                GrowthInsight(
                    kind="improving",
                    title=best[0].title,
                    detail=f"Trending up at mastery {best[1]} — momentum is on your side.",
                    route=f"/tutor/{best[0].id}",
                )
            )
        weakest = min(rows, key=lambda r: r[1])
        insights.append(
            GrowthInsight(
                kind="attention",
                title=weakest[0].title,
                detail=f"Mastery {weakest[1]} — a short session here pays off most.",
                route=f"/tutor/{weakest[0].id}",
            )
        )
        next_step = NextStep(
            title=f"Review {weakest[0].title}",
            reason=f"Your mastery here is {weakest[1]} — a focused session lifts it fastest.",
            route=f"/tutor/{weakest[0].id}",
        )

    return {
        "dimensions": dimensions,
        "week": _week(db, user.id),
        "streakDays": streak_days,
        "insights": insights,
        "nextStep": next_step,
    }


# --------------------------------------------------------------- knowledge map


def _area(subject_id: str, title: str, icon: str, tone: str,
          topics: list[tuple[Topic, int]]) -> KnowledgeArea:
    return KnowledgeArea(
        id=subject_id,
        title=title,
        icon=icon,
        tone=tone,
        topics=[
            KnowledgeTopic(
                topic_id=topic.id, title=topic.title, mastery=mastery,
                route=f"/tutor/{topic.id}",
            )
            for topic, mastery in topics
        ],
    )


def get_knowledge_map(db: Session, user: User) -> dict:
    mastery_by_topic = {
        topic.id: value for topic, value, _ in _mastery_rows(db, user.id)
    }
    subjects = db.execute(select(Subject)).scalars().all()
    areas: list[KnowledgeArea] = []

    if subjects:
        for subject in subjects:
            topics = (
                db.execute(select(Topic).where(Topic.subject_id == subject.id))
                .scalars()
                .all()
            )
            if not topics:
                continue
            areas.append(
                _area(
                    subject.id, subject.title, subject.icon, subject.tone,
                    [(t, mastery_by_topic.get(t.id, 0)) for t in topics],
                )
            )
        return {"areas": areas}

    # No taxonomy seeded — bucket topics heuristically by their slugs.
    topics = db.execute(select(Topic)).scalars().all()
    buckets: dict[str, list[tuple[Topic, int]]] = {aid: [] for aid, *_ in _HEURISTIC_AREAS}
    for topic in topics:
        slug = topic.slug.lower()
        target = _HEURISTIC_AREAS[-1][0]  # Machine Learning catch-all
        for area_id, _title, _icon, _tone, keywords in _HEURISTIC_AREAS[:-1]:
            if any(keyword in slug for keyword in keywords):
                target = area_id
                break
        buckets[target].append((topic, mastery_by_topic.get(topic.id, 0)))
    for area_id, title, icon, tone, _keywords in _HEURISTIC_AREAS:
        if buckets[area_id]:
            areas.append(_area(area_id, title, icon, tone, buckets[area_id]))
    return {"areas": areas}
