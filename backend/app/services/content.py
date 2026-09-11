"""Content generation: study guides, mind maps and studycasts.

Each generator accepts topicId or notebookId (at least one, else
VALIDATION_ERROR), calls the AI router and validates/coerces the returned dict
defensively — a weird AI shape can never 500. Study guides and mind maps are
persisted; studycasts are ephemeral (audioUrl stays null in the MVP).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts, router as ai_router
from app.ai.base import TaskType
from app.models import Mastery, MindMap, Notebook, StudyGuide, Topic, User
from app.services.roadmap import get_or_create_topic, slugify
from app.utils.errors import AppError, NotFound
from app.utils.ids import new_id

_GUIDE_KINDS = {
    "overview",
    "concepts",
    "definitions",
    "formulas",
    "examples",
    "mistakes",
    "tips",
    "practice",
    "revision",
}


def _resolve_subject(db: Session, user: User, body) -> tuple[str, str | None, str | None]:
    """(subject_title, topic_id, notebook_id) from topicId/notebookId."""
    if not body.topic_id and not body.notebook_id:
        raise AppError("VALIDATION_ERROR", "Provide topicId or notebookId.", 422)
    subject = "General Review"
    topic_id = None
    notebook_id = None
    if body.notebook_id:
        notebook = db.get(Notebook, body.notebook_id)
        if notebook is None or notebook.user_id != user.id:
            raise NotFound("Notebook")
        notebook_id = notebook.id
        subject = notebook.title
    if body.topic_id:
        topic = get_or_create_topic(db, body.topic_id)
        topic_id = topic.id
        subject = topic.title
    return subject, topic_id, notebook_id


# ----------------------------------------------------------------- study guide


def _clean_sections(raw) -> list[dict]:
    cleaned: list[dict] = []
    seen_ids: set[str] = set()
    if not isinstance(raw, list):
        return cleaned
    for i, item in enumerate(raw[:12]):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        markdown = str(item.get("markdown") or "").strip()
        if not title or not markdown:
            continue
        kind = str(item.get("kind") or "").strip().lower()
        if kind not in _GUIDE_KINDS:
            kind = "overview" if i == 0 else "concepts"
        section_id = slugify(str(item.get("id") or title)) or f"section-{i + 1}"
        while section_id in seen_ids:
            section_id = f"{section_id}-{i + 1}"
        seen_ids.add(section_id)
        cleaned.append(
            {
                "id": section_id,
                "title": title[:200],
                "kind": kind,
                "markdown": markdown,
                "citations": [],  # MVP: guides are not source-grounded yet
            }
        )
    return cleaned


def generate_study_guide(db: Session, user: User, body) -> dict:
    subject, topic_id, notebook_id = _resolve_subject(db, user, body)
    data, _res = ai_router.generate_json(
        TaskType.STUDY_GUIDE,
        [{"role": "user", "content": prompts.study_guide_prompt(subject)}],
        schema_hint=(
            'Return ONLY JSON: {"title": "...", "sections": [{"id": "overview", '
            '"title": "...", "kind": "overview", "markdown": "..."}]}'
        ),
    )
    if not isinstance(data, dict):
        data = {}
    sections = _clean_sections(data.get("sections"))
    if not sections:
        sections = [
            {
                "id": "overview",
                "title": "Overview",
                "kind": "overview",
                "markdown": f"A study guide for **{subject}** could not be fully "
                "generated right now — try again in a moment.",
                "citations": [],
            }
        ]
    title = str(data.get("title") or "").strip()[:300] or f"{subject} — Study Guide"

    db.add(
        StudyGuide(
            id=new_id(),
            user_id=user.id,
            topic_id=topic_id,
            notebook_id=notebook_id,
            title=title,
            sections=sections,
        )
    )
    db.flush()
    return {"title": title, "sections": sections}


# -------------------------------------------------------------------- mind map


def generate_mindmap(db: Session, user: User, body) -> dict:
    subject, topic_id, notebook_id = _resolve_subject(db, user, body)
    data, _res = ai_router.generate_json(
        TaskType.ROADMAP_GEN,  # fast/structured lane; mindmap has no own task type
        [{"role": "user", "content": prompts.mindmap_prompt(subject)}],
        schema_hint=(
            'Return ONLY JSON: {"center": "...", "nodes": [{"id": "n1", '
            '"label": "...", "parentId": null}]}'
        ),
    )
    if not isinstance(data, dict):
        data = {}
    center = str(data.get("center") or "").strip()[:200] or subject

    raw_nodes = data.get("nodes")
    specs: list[dict] = []
    ids: set[str] = set()
    if isinstance(raw_nodes, list):
        for i, item in enumerate(raw_nodes[:32]):
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "").strip()
            if not label:
                continue
            node_id = str(item.get("id") or "").strip() or f"n{i + 1}"
            while node_id in ids:
                node_id = f"{node_id}-{i + 1}"
            ids.add(node_id)
            parent = item.get("parentId")
            specs.append(
                {"id": node_id, "label": label[:120], "parentId": parent}
            )
    for spec in specs:  # parentId must reference an existing node (or be null)
        if spec["parentId"] is not None and str(spec["parentId"]) not in ids:
            spec["parentId"] = None

    # Resolve label slugs against the taxonomy: mastery is None unless the
    # label matches a known topic that has a Mastery row (source of truth).
    slugs = {slugify(spec["label"]) for spec in specs}
    topic_by_slug: dict[str, Topic] = {}
    if slugs:
        for topic in db.execute(select(Topic).where(Topic.slug.in_(slugs))).scalars():
            topic_by_slug[topic.slug] = topic
    mastery_by_topic: dict[str, int] = {}
    if topic_by_slug:
        rows = db.execute(
            select(Mastery.topic_id, Mastery.value).where(
                Mastery.user_id == user.id,
                Mastery.topic_id.in_({t.id for t in topic_by_slug.values()}),
            )
        ).all()
        mastery_by_topic = {tid: int(v) for tid, v in rows}

    nodes = []
    for spec in specs:
        topic = topic_by_slug.get(slugify(spec["label"]))
        nodes.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "parentId": spec["parentId"],
                "mastery": mastery_by_topic.get(topic.id) if topic else None,
                "topicId": topic.id if topic else None,
            }
        )

    db.add(
        MindMap(
            id=new_id(),
            user_id=user.id,
            topic_id=topic_id,
            notebook_id=notebook_id,
            center=center,
            nodes=nodes,
        )
    )
    db.flush()
    return {"center": center, "nodes": nodes}


# ------------------------------------------------------------------- studycast


def generate_studycast(db: Session, user: User, body) -> dict:
    subject, _topic_id, _notebook_id = _resolve_subject(db, user, body)
    minutes = max(1, min(30, int(getattr(body, "minutes", 5) or 5)))
    data, _res = ai_router.generate_json(
        TaskType.STUDYCAST,
        [{"role": "user", "content": prompts.studycast_prompt(subject, minutes=minutes)}],
        schema_hint=(
            'Return ONLY JSON: {"title": "...", "lines": [{"speaker": "A", "text": "..."}]}'
        ),
    )
    if not isinstance(data, dict):
        data = {}

    lines: list[dict] = []
    raw_lines = data.get("lines")
    if isinstance(raw_lines, list):
        for i, item in enumerate(raw_lines[:200]):
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            speaker = str(item.get("speaker") or "").strip().upper()
            if speaker not in ("A", "B"):
                speaker = "A" if len(lines) % 2 == 0 else "B"
            lines.append({"speaker": speaker, "text": text})
    if not lines:
        lines = [
            {"speaker": "A", "text": f"Let's talk about {subject} — where should we start?"},
            {
                "speaker": "B",
                "text": "Right at the core idea. The full episode could not be "
                "generated just now, so give it another try in a moment.",
            },
        ]

    title = str(data.get("title") or "").strip()[:200] or f"{subject}, Plainly"
    return {
        "id": new_id(),
        "title": title,
        "minutes": minutes,
        "lines": lines,
        "audioUrl": None,
    }
