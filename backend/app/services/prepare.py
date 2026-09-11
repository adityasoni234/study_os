"""Preparation plans ("Prepare me"): get-or-create per (user, opportunity).

The flagship demo plan for 'hackathon-ai-ed' is hand-authored to mirror the
frontend exactly (6 days, Day 2 tutors 'what-is-rag'). Every other opportunity
gets a 4-6 day plan generated through the AI router (ROADMAP_GEN) and coerced
defensively — weird shapes fall back to a sensible generic plan. Plans persist
as PrepPlan (day metadata JSON) + PrepTask rows, so a second prepare call
returns the SAME plan with done flags preserved.

Readiness = 72 + 25 * done/total, rounded, capped at 97.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai import router as ai_router
from app.ai.base import TaskType
from app.models.opportunity import Opportunity, PrepPlan, PrepTask
from app.models.user import Profile, User
from app.opportunities.matching import match_for_user
from app.schemas.opportunity import PrepDayOut, PrepPlanOut, PrepTaskOut, PrepToggleOut
from app.utils.errors import NotFound

READINESS_BASE = 72
READINESS_SPREAD = 25
READINESS_CAP = 97

MIN_DAYS, MAX_DAYS = 4, 6
_MIN_MINUTES, _MAX_MINUTES = 15, 180
_MAX_TASKS_PER_DAY = 4

# Hand-authored plans keyed by opportunity id. Day dicts: title, minutes,
# tasks (labels), tutor_topic_id, note. Mirrors src/data/opportunities.ts.
HAND_AUTHORED: dict[str, dict] = {
    "hackathon-ai-ed": {
        "gap_note": (
            "RAG is new to you — Day 2 is lighter everywhere else so you can "
            "take your time here."
        ),
        "days": [
            {
                "title": "Understand the problem space",
                "minutes": 45,
                "tasks": [
                    "Read the hackathon brief and judging criteria",
                    "Pick a learning problem you personally understand",
                    "Sketch your one-line pitch",
                ],
                "tutor_topic_id": None,
                "note": None,
            },
            {
                "title": "Learn RAG fundamentals",
                "minutes": 60,
                "tasks": [
                    'Complete "What is RAG?" with your tutor',
                    "Understand embeddings at an intuition level",
                    "Skim one real RAG example project",
                ],
                "tutor_topic_id": "what-is-rag",
                "note": (
                    "RAG is new to you, so this day is lighter everywhere else "
                    "— take your time here."
                ),
            },
            {
                "title": "Build the prototype core",
                "minutes": 90,
                "tasks": [
                    "Set up the project skeleton in Python",
                    "Wire a minimal retrieval + answer loop",
                    "Hard-code one happy-path demo",
                ],
                "tutor_topic_id": None,
                "note": None,
            },
            {
                "title": "Make it real",
                "minutes": 90,
                "tasks": [
                    "Add your own study materials as sources",
                    "Handle two edge cases gracefully",
                    "Draft the demo script",
                ],
                "tutor_topic_id": None,
                "note": None,
            },
            {
                "title": "Polish & practice",
                "minutes": 60,
                "tasks": [
                    "Tighten the UI for the demo path",
                    "Rehearse the 3-minute pitch twice",
                    "Prepare answers for likely judge questions",
                ],
                "tutor_topic_id": None,
                "note": None,
            },
            {
                "title": "Submit with margin",
                "minutes": 30,
                "tasks": [
                    "Record the demo video",
                    "Write the submission description",
                    "Submit before 6pm — never at the deadline",
                ],
                "tutor_topic_id": None,
                "note": None,
            },
        ],
    },
}


def prepare_plan(db: Session, user: User, opportunity_id: str) -> PrepPlanOut:
    """Get-or-create the preparation plan (idempotent; preserves done flags)."""
    opp = db.get(Opportunity, opportunity_id)
    if opp is None:
        raise NotFound("Opportunity")

    plan = _existing_plan(db, user, opportunity_id)
    if plan is None:
        spec = HAND_AUTHORED.get(opp.id) or _generated_spec(db, user, opp)
        plan = _persist(db, user, opp, spec)
    return _serialize(db, plan)


def toggle_task(db: Session, user: User, task_id: str) -> PrepToggleOut:
    """Flip one task's done flag and recompute readiness. Foreign/unknown → 404."""
    task = db.get(PrepTask, task_id)
    plan = db.get(PrepPlan, task.plan_id) if task is not None else None
    if task is None or plan is None or plan.user_id != user.id:
        raise NotFound("Preparation task")
    task.done = not task.done
    tasks = _plan_tasks(db, plan.id)
    readiness = _readiness(tasks)
    plan.readiness = readiness
    plan.started = any(t.done for t in tasks)
    db.flush()
    return PrepToggleOut(done=task.done, readiness=readiness)


# --- internals ---------------------------------------------------------------


def _existing_plan(db: Session, user: User, opportunity_id: str) -> PrepPlan | None:
    return db.execute(
        select(PrepPlan)
        .where(PrepPlan.user_id == user.id, PrepPlan.opportunity_id == opportunity_id)
        .order_by(PrepPlan.created_at)
    ).scalars().first()


def _plan_tasks(db: Session, plan_id: str) -> list[PrepTask]:
    return db.execute(
        select(PrepTask)
        .where(PrepTask.plan_id == plan_id)
        .order_by(PrepTask.day, PrepTask.position)
    ).scalars().all()


def _readiness(tasks: list[PrepTask]) -> int:
    if not tasks:
        return READINESS_BASE
    done = sum(1 for t in tasks if t.done)
    value = READINESS_BASE + READINESS_SPREAD * done / len(tasks)
    return min(READINESS_CAP, int(round(value)))


def _persist(db: Session, user: User, opp: Opportunity, spec: dict) -> PrepPlan:
    days_meta = [
        {
            "day": i,
            "title": day["title"],
            "minutes": day["minutes"],
            "tutor_topic_id": day.get("tutor_topic_id"),
            "note": day.get("note"),
        }
        for i, day in enumerate(spec["days"], start=1)
    ]
    plan = PrepPlan(
        user_id=user.id,
        opportunity_id=opp.id,
        readiness=READINESS_BASE,
        gap_note=spec.get("gap_note") or "",
        days=days_meta,
        started=False,
    )
    db.add(plan)
    db.flush()  # assigns plan.id for the task FKs
    for i, day in enumerate(spec["days"], start=1):
        for position, label in enumerate(day["tasks"]):
            db.add(PrepTask(plan_id=plan.id, day=i, position=position, label=label, done=False))
    db.flush()
    return plan


def _serialize(db: Session, plan: PrepPlan) -> PrepPlanOut:
    tasks = _plan_tasks(db, plan.id)
    by_day: dict[int, list[PrepTaskOut]] = {}
    for task in tasks:
        by_day.setdefault(task.day, []).append(
            PrepTaskOut(id=task.id, label=task.label, done=task.done)
        )
    days = [
        PrepDayOut(
            day=int(meta.get("day", i)),
            title=str(meta.get("title") or f"Day {i}"),
            minutes=int(meta.get("minutes") or 45),
            tasks=by_day.get(int(meta.get("day", i)), []),
            tutor_topic_id=meta.get("tutor_topic_id"),
            note=meta.get("note"),
        )
        for i, meta in enumerate(sorted(plan.days or [], key=lambda m: m.get("day", 0)), start=1)
    ]
    readiness = _readiness(tasks)
    if plan.readiness != readiness:  # keep the stored value honest
        plan.readiness = readiness
        db.flush()
    return PrepPlanOut(
        opportunity_id=plan.opportunity_id,
        days_remaining=len(days),
        readiness=readiness,
        gap_note=plan.gap_note or "",
        days=days,
    )


def _generated_spec(db: Session, user: User, opp: Opportunity) -> dict:
    """AI-generated 4-6 day plan; falls back to a generic plan on weird shapes."""
    match = match_for_user(db, user, opp)
    profile = db.get(Profile, user.id)
    prompt = prompts.roadmap_prompt(
        goal=f"Prepare for {opp.title}",
        level=profile.level if profile else "Beginner",
        hours_per_week=5,
        deadline=opp.deadline_text or None,
    )
    data, _ = ai_router.generate_json(TaskType.ROADMAP_GEN, [{"role": "user", "content": prompt}])
    days = _days_from_roadmap(data)
    if not days:
        days = _generic_days(opp)
    days = days[:MAX_DAYS]
    if len(days) < MIN_DAYS:
        for filler in _generic_days(opp):
            if len(days) >= MIN_DAYS:
                break
            days.append(filler)
    return {"gap_note": _gap_note(match), "days": days}


def _days_from_roadmap(data: dict) -> list[dict]:
    """Map ROADMAP_GEN output (milestones→topics) into day dicts; [] on junk."""
    days: list[dict] = []
    try:
        for milestone in data.get("milestones") or []:
            if not isinstance(milestone, dict):
                continue
            for topic in milestone.get("topics") or []:
                if not isinstance(topic, dict):
                    continue
                title = str(topic.get("title") or "").strip()
                if not title:
                    continue
                tasks = [
                    str(sub).strip()
                    for sub in (topic.get("subtopics") or [])
                    if str(sub).strip()
                ][:_MAX_TASKS_PER_DAY]
                if not tasks:
                    tasks = [f"Study {title}", "Apply it in one small exercise"]
                days.append(
                    {
                        "title": title,
                        "minutes": _coerce_minutes(topic.get("minutes")),
                        "tasks": tasks,
                        "tutor_topic_id": None,
                        "note": None,
                    }
                )
    except Exception:
        return []
    return days


def _coerce_minutes(value) -> int:
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        minutes = 45
    return max(_MIN_MINUTES, min(_MAX_MINUTES, minutes))


def _gap_note(match: dict) -> str:
    gaps = match.get("gaps") or []
    if not gaps:
        return ""
    label = str(gaps[0]).split(" — ")[0].strip()
    return f"{label} is your main gap — the first days shore it up before the deliverable."


def _generic_days(opp: Opportunity) -> list[dict]:
    """Deterministic fallback plan when generation returns nothing usable."""
    return [
        {
            "title": "Understand the brief",
            "minutes": 45,
            "tasks": [
                f"Read the {opp.type.lower()} requirements and eligibility",
                "Note how submissions are judged or selected",
                "List exactly what you must deliver",
            ],
            "tutor_topic_id": None,
            "note": None,
        },
        {
            "title": "Close your biggest gap",
            "minutes": 60,
            "tasks": [
                "Pick the weakest skill this opportunity needs",
                "Do one focused study session on it",
                "Summarise what you learned in five bullet points",
            ],
            "tutor_topic_id": None,
            "note": None,
        },
        {
            "title": "Build the core deliverable",
            "minutes": 90,
            "tasks": [
                "Draft the main artifact end to end",
                "Keep scope small enough to finish",
                "Get one honest outside opinion",
            ],
            "tutor_topic_id": None,
            "note": None,
        },
        {
            "title": "Polish and strengthen",
            "minutes": 60,
            "tasks": [
                "Revise the weakest part of your draft",
                "Check every requirement is addressed",
                "Prepare answers for likely questions",
            ],
            "tutor_topic_id": None,
            "note": None,
        },
        {
            "title": "Submit with margin",
            "minutes": 30,
            "tasks": [
                "Do a final read-through",
                "Submit at least a day early",
                "Confirm the submission was received",
            ],
            "tutor_topic_id": None,
            "note": None,
        },
    ]
