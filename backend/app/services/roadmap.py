"""Roadmap business logic: serialization of the node tree, progress, CRUD and
AI-backed creation.

Conventions honoured here (docs/ARCHITECTURE.md):
- Mastery (app.models.learning.Mastery) is THE source of truth for a topic's
  mastery number; topic-kind nodes resolve it through node.topic_id (fallback 0).
- Progress is weighted: topics finished (status done or review) count 1 each,
  the current topic(s) earn partial credit mastery/100, over the topics in the
  UNLOCKED (done/current) milestones. Fresh seeds put the 'ml' roadmap at
  (4 + 1 + 0.65) / 8 = 71, drifting toward 74 as precision-recall mastery grows.
- AI dicts are validated and coerced defensively — a weird shape can never 500.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts, router as ai_router
from app.ai.base import TaskType
from app.models import Mastery, Roadmap, RoadmapNode, Topic, User
from app.utils.errors import NotFound
from app.utils.ids import new_id

# Sensible (tone, icon) per roadmap type — mirrors the seeded demo roadmaps.
_TYPE_STYLE: dict[str, tuple[str, str]] = {
    "Subject": ("indigo", "brain"),
    "Career": ("violet", "rocket"),
    "Skill": ("sky", "code"),
    "Personal": ("mint", "chat"),
    "Topic": ("amber", "layers"),
    "Exam": ("indigo", "target"),
}
_VALID_TYPES = set(_TYPE_STYLE)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 120) -> str:
    slug = _SLUG_RE.sub("-", str(text).lower()).strip("-")
    return slug[:max_len].strip("-") or "topic"


def get_or_create_topic(db: Session, title_or_id: str, *, summary: str | None = None) -> Topic:
    """Resolve a topic by id, then slug; create it (uuid id) when absent."""
    raw = str(title_or_id).strip()
    topic = db.get(Topic, raw[:32]) if raw else None
    if topic is not None:
        return topic
    slug = slugify(raw)
    topic = db.execute(select(Topic).where(Topic.slug == slug)).scalar_one_or_none()
    if topic is not None:
        return topic
    title = raw if any(c.isupper() for c in raw) or " " in raw else slug.replace("-", " ").title()
    topic = Topic(id=new_id(), slug=slug, title=title[:200], summary=summary)
    db.add(topic)
    db.flush()
    return topic


def mastery_values(db: Session, user_id: str, topic_ids: list[str]) -> dict[str, int]:
    """{topic_id: value} for the given topics; missing rows simply absent."""
    if not topic_ids:
        return {}
    rows = db.execute(
        select(Mastery.topic_id, Mastery.value).where(
            Mastery.user_id == user_id, Mastery.topic_id.in_(set(topic_ids))
        )
    ).all()
    return {topic_id: int(value) for topic_id, value in rows}


# ---------------------------------------------------------------- serialization


def _subtopic_state(status: str) -> str:
    if status == "done":
        return "done"
    if status == "current":
        return "current"
    return "next"


def _split_tree(nodes: list[RoadmapNode]):
    """(milestones, children_by_parent) from the flat node list, position-ordered."""
    milestones = sorted(
        (n for n in nodes if n.kind == "milestone"), key=lambda n: n.position
    )
    children: dict[str, list[RoadmapNode]] = {}
    for node in nodes:
        if node.parent_id:
            children.setdefault(node.parent_id, []).append(node)
    for group in children.values():
        group.sort(key=lambda n: n.position)
    return milestones, children


def compute_progress(
    nodes: list[RoadmapNode], mastery_map: dict[str, int]
) -> tuple[int, int, int]:
    """(progress_pct, topics_done, topics_total) — see module docstring for the rule."""
    milestones, children = _split_tree(nodes)
    all_topics = [n for n in nodes if n.kind == "topic"]
    topics_done = sum(1 for n in all_topics if n.status == "done")

    weighted = 0.0
    reachable = 0
    for milestone in milestones:
        if milestone.status == "locked":
            continue
        for topic in children.get(milestone.id, []):
            if topic.kind != "topic":
                continue
            reachable += 1
            if topic.status in ("done", "review"):
                weighted += 1.0
            elif topic.status == "current":
                weighted += (mastery_map.get(topic.topic_id or "", 0)) / 100.0
    progress = round(100.0 * weighted / reachable) if reachable else 0
    return max(0, min(100, progress)), topics_done, len(all_topics)


def serialize_roadmap(db: Session, roadmap: Roadmap, with_milestones: bool = True) -> dict:
    """Build the contract Roadmap JSON from the node tree + Mastery."""
    nodes = list(roadmap.nodes)
    topic_ids = [n.topic_id for n in nodes if n.topic_id]
    masteries = mastery_values(db, roadmap.user_id, topic_ids)
    progress, _, _ = compute_progress(nodes, masteries)

    data: dict = {
        "id": roadmap.id,
        "title": roadmap.title,
        "type": roadmap.type,
        "tone": roadmap.tone,
        "icon": roadmap.icon,
        "goal": roadmap.goal_text,
        "targetDate": roadmap.target_date,
        "progress": progress,
        "focus": roadmap.focus,
        "nextAction": roadmap.next_action,
        "nextTopicId": roadmap.next_topic_id,
        "adaptedNote": roadmap.adapted_note,
        "isNew": bool(roadmap.is_new),
    }
    if not with_milestones:
        return data

    milestones, children = _split_tree(nodes)
    data["milestones"] = [
        {
            "id": m.id,
            "title": m.title,
            "status": m.status,
            "topics": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "mastery": masteries.get(t.topic_id or "", 0),
                    "minutes": t.minutes,
                    "summary": t.summary,
                    "subtopics": [
                        {"title": s.title, "state": _subtopic_state(s.status)}
                        for s in children.get(t.id, [])
                        if s.kind == "subtopic"
                    ],
                    "note": t.note,
                }
                for t in children.get(m.id, [])
                if t.kind == "topic"
            ],
        }
        for m in milestones
    ]
    return data


# ------------------------------------------------------------------- endpoints


def _get_owned(db: Session, user: User, roadmap_id: str) -> Roadmap:
    roadmap = db.get(Roadmap, roadmap_id)
    if roadmap is None or roadmap.user_id != user.id:
        raise NotFound("Roadmap")
    return roadmap


def list_roadmaps(db: Session, user: User) -> dict:
    roadmaps = (
        db.execute(
            select(Roadmap)
            .where(Roadmap.user_id == user.id, Roadmap.archived.is_(False))
            .order_by(Roadmap.created_at)
        )
        .scalars()
        .all()
    )
    return {"roadmaps": [serialize_roadmap(db, r, with_milestones=False) for r in roadmaps]}


def get_roadmap(db: Session, user: User, roadmap_id: str) -> dict:
    return serialize_roadmap(db, _get_owned(db, user, roadmap_id), with_milestones=True)


def patch_roadmap(db: Session, user: User, roadmap_id: str, fields: dict) -> dict:
    """fields: already filtered to the provided keys (target_date/goal/archived)."""
    roadmap = _get_owned(db, user, roadmap_id)
    if "target_date" in fields:
        roadmap.target_date = fields["target_date"]
    if "goal" in fields:
        roadmap.goal_text = fields["goal"]
    if "archived" in fields and fields["archived"] is not None:
        roadmap.archived = bool(fields["archived"])
    db.flush()
    return serialize_roadmap(db, roadmap, with_milestones=True)


def roadmap_progress(db: Session, user: User, roadmap_id: str) -> dict:
    roadmap = _get_owned(db, user, roadmap_id)
    nodes = list(roadmap.nodes)
    topic_ids = [n.topic_id for n in nodes if n.kind == "topic" and n.topic_id]
    masteries = mastery_values(db, user.id, topic_ids)
    progress, topics_done, topics_total = compute_progress(nodes, masteries)
    return {
        "progress": progress,
        "topicsDone": topics_done,
        "topicsTotal": topics_total,
        "mastery": {tid: masteries.get(tid, 0) for tid in topic_ids},
    }


# ---------------------------------------------------------------- AI creation

_ROADMAP_SCHEMA_HINT = (
    'Return ONLY a JSON object shaped exactly like: {"title": "...", "type": "Subject", '
    '"focus": "...", "milestones": [{"title": "...", "topics": [{"title": "...", '
    '"minutes": 60, "summary": "...", "subtopics": ["..."]}]}]}'
)


def _coerce_minutes(value, default: int = 30) -> int:
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return default
    return minutes if 5 <= minutes <= 6000 else default


def _clean_milestones(raw) -> list[dict]:
    """Coerce the AI milestones payload into [{title, topics:[{title, minutes,
    summary, subtopics:[str]}]}]; drops anything malformed, never raises."""
    cleaned: list[dict] = []
    if not isinstance(raw, list):
        return cleaned
    for milestone in raw[:6]:
        if not isinstance(milestone, dict):
            continue
        title = str(milestone.get("title") or "").strip()
        topics_raw = milestone.get("topics")
        topics: list[dict] = []
        if isinstance(topics_raw, list):
            for topic in topics_raw[:8]:
                if not isinstance(topic, dict):
                    continue
                topic_title = str(topic.get("title") or "").strip()
                if not topic_title:
                    continue
                subtopics_raw = topic.get("subtopics")
                subtopics: list[str] = []
                if isinstance(subtopics_raw, list):
                    for sub in subtopics_raw[:6]:
                        if isinstance(sub, str) and sub.strip():
                            subtopics.append(sub.strip()[:200])
                        elif isinstance(sub, dict) and str(sub.get("title") or "").strip():
                            subtopics.append(str(sub["title"]).strip()[:200])
                summary = topic.get("summary")
                topics.append(
                    {
                        "title": topic_title[:200],
                        "minutes": _coerce_minutes(topic.get("minutes")),
                        "summary": str(summary)[:1000] if summary else None,
                        "subtopics": subtopics,
                    }
                )
        if title and topics:
            cleaned.append({"title": title[:200], "topics": topics})
    return cleaned


def create_roadmap(db: Session, user: User, body) -> dict:
    """POST /api/roadmaps — AI-generate, persist the tree, return the full shape."""
    data, _res = ai_router.generate_json(
        TaskType.ROADMAP_GEN,
        [
            {
                "role": "user",
                "content": prompts.roadmap_prompt(
                    body.goal,
                    level=body.level or "Beginner",
                    hours_per_week=body.hours_per_week,
                    deadline=body.deadline,
                    known=body.known_topics or None,
                ),
            }
        ],
        schema_hint=_ROADMAP_SCHEMA_HINT,
    )
    if not isinstance(data, dict):  # defensive: generate_json contract is a dict
        data = {}

    milestones = _clean_milestones(data.get("milestones"))
    if not milestones:  # weird AI shape → minimal but valid plan, never a 500
        milestones = [
            {
                "title": "Getting Started",
                "topics": [
                    {
                        "title": body.goal[:200],
                        "minutes": 30,
                        "summary": None,
                        "subtopics": [],
                    }
                ],
            }
        ]

    rtype = body.type if body.type in _VALID_TYPES else None
    if rtype is None:
        ai_type = str(data.get("type") or "").strip()
        rtype = ai_type if ai_type in _VALID_TYPES else "Topic"
    tone, icon = _TYPE_STYLE.get(rtype, ("indigo", "sparkles"))

    title = str(data.get("title") or "").strip()[:200] or body.goal[:200]
    focus = str(data.get("focus") or "").strip()[:200] or milestones[0]["title"]

    roadmap = Roadmap(
        id=new_id(),
        user_id=user.id,
        title=title,
        type=rtype,
        tone=tone,
        icon=icon,
        goal_text=body.goal,
        target_date=body.deadline,
        focus=focus,
        is_new=True,
        archived=False,
    )
    db.add(roadmap)
    db.flush()

    first_topic_node: RoadmapNode | None = None
    for m_pos, milestone in enumerate(milestones):
        m_status = "current" if m_pos == 0 else "locked"
        m_node = RoadmapNode(
            id=new_id(),
            roadmap_id=roadmap.id,
            parent_id=None,
            kind="milestone",
            title=milestone["title"],
            status=m_status,
            position=m_pos,
            depends_on=[],
        )
        db.add(m_node)
        db.flush()
        for t_pos, topic_spec in enumerate(milestone["topics"]):
            is_first = m_pos == 0 and t_pos == 0
            topic_row = get_or_create_topic(
                db, topic_spec["title"], summary=topic_spec["summary"]
            )
            t_node = RoadmapNode(
                id=new_id(),
                roadmap_id=roadmap.id,
                parent_id=m_node.id,
                kind="topic",
                title=topic_spec["title"],
                status="current" if is_first else "locked",
                position=t_pos,
                minutes=topic_spec["minutes"],
                summary=topic_spec["summary"],
                topic_id=topic_row.id,
                depends_on=[],
            )
            db.add(t_node)
            db.flush()
            if is_first:
                first_topic_node = t_node
            for s_pos, sub_title in enumerate(topic_spec["subtopics"]):
                db.add(
                    RoadmapNode(
                        id=new_id(),
                        roadmap_id=roadmap.id,
                        parent_id=t_node.id,
                        kind="subtopic",
                        title=sub_title,
                        status="current" if is_first and s_pos == 0 else "locked",
                        position=s_pos,
                        minutes=None,
                        depends_on=[],
                    )
                )

    if first_topic_node is not None:
        roadmap.next_action = f"Learn {first_topic_node.title}"
        roadmap.next_topic_id = first_topic_node.topic_id
    db.flush()
    db.refresh(roadmap)
    return serialize_roadmap(db, roadmap, with_milestones=True)
