"""Quiz generation and grading.

- Generate: AI (QUIZ_GEN) → validated questions persisted server-side with the
  correct index; the API response NEVER includes correctIndex.
- Submit: grade against the DB, update Mastery (the shared source of truth):
  pct>=0.8 → +8, >=0.6 → +5, else +2, capped at 95. If Agent-Tutor's
  app.services.mastery module exists, its apply-style helper is preferred
  (lazy import, best-effort); the direct update always works as fallback.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts, router as ai_router
from app.ai.base import TaskType
from app.models import Mastery, Notebook, Quiz, QuizAttempt, QuizQuestion, User
from app.services.roadmap import get_or_create_topic
from app.utils.errors import AppError, NotFound
from app.utils.ids import new_id

log = logging.getLogger("studyos")

_TAGS = ("Definitions", "Concepts", "Applications")

_QUIZ_SCHEMA_HINT = (
    'Return ONLY a JSON object shaped exactly like: {"questions": [{"prompt": "...", '
    '"options": ["...", "...", "...", "..."], "correctIndex": 0, "explanation": "...", '
    '"tag": "Definitions"}]}'
)


def _clean_questions(raw, limit: int) -> list[dict]:
    """Coerce the AI payload into valid question dicts; drop garbage, never raise."""
    cleaned: list[dict] = []
    if not isinstance(raw, list):
        return cleaned
    for i, item in enumerate(raw):
        if len(cleaned) >= limit:
            break
        if not isinstance(item, dict):
            continue
        prompt = str(item.get("prompt") or "").strip()
        options_raw = item.get("options")
        if not prompt or not isinstance(options_raw, list):
            continue
        options = [str(o).strip() for o in options_raw if str(o).strip()][:6]
        if len(options) < 2:
            continue
        try:
            correct = int(item.get("correctIndex"))
        except (TypeError, ValueError):
            correct = 0
        if not 0 <= correct < len(options):
            correct = 0
        tag = str(item.get("tag") or "").strip().title()
        if tag not in _TAGS:
            tag = _TAGS[i % len(_TAGS)]
        cleaned.append(
            {
                "prompt": prompt,
                "options": options,
                "correct_index": correct,
                "explanation": str(item.get("explanation") or "").strip(),
                "tag": tag,
            }
        )
    return cleaned


def generate_quiz(db: Session, user: User, body) -> dict:
    """POST /api/quiz/generate — persist Quiz + questions, respond without answers."""
    if not body.topic_id and not body.notebook_id:
        raise AppError("VALIDATION_ERROR", "Provide topicId or notebookId.", 422)

    subject = "General Review"
    topic = None
    notebook_id = None
    if body.notebook_id:
        notebook = db.get(Notebook, body.notebook_id)
        if notebook is None or notebook.user_id != user.id:
            raise NotFound("Notebook")
        notebook_id = notebook.id
        subject = notebook.title
    if body.topic_id:
        topic = get_or_create_topic(db, body.topic_id)
        subject = topic.title

    n = max(3, min(8, int(body.length or 5)))
    data, _res = ai_router.generate_json(
        TaskType.QUIZ_GEN,
        [
            {
                "role": "user",
                "content": prompts.quiz_prompt(
                    subject, difficulty=body.difficulty, n=n, focus=body.focus
                ),
            }
        ],
        schema_hint=_QUIZ_SCHEMA_HINT,
    )
    questions = _clean_questions(data.get("questions") if isinstance(data, dict) else None, 8)
    if not questions:
        raise AppError("AI_UNAVAILABLE", "Could not build a quiz right now — please retry.", 503)

    quiz = Quiz(
        id=new_id(),
        user_id=user.id,
        topic_id=topic.id if topic else None,
        notebook_id=notebook_id,
        difficulty=str(body.difficulty or "medium")[:16],
        focus=str(body.focus or "mixed")[:32],
    )
    db.add(quiz)
    rows: list[QuizQuestion] = []
    for position, spec in enumerate(questions):
        row = QuizQuestion(
            id=new_id(),
            quiz_id=quiz.id,
            position=position,
            prompt=spec["prompt"],
            options=spec["options"],
            correct_index=spec["correct_index"],
            explanation=spec["explanation"],
            tag=spec["tag"],
        )
        db.add(row)
        rows.append(row)
    db.flush()

    return {
        "quizId": quiz.id,
        "topicId": quiz.topic_id,
        "questions": [
            {"id": r.id, "prompt": r.prompt, "options": list(r.options), "tag": r.tag}
            for r in rows
        ],
    }


# ------------------------------------------------------------------ submission


def _mastery_delta(pct: float) -> int:
    if pct >= 0.8:
        return 8
    if pct >= 0.6:
        return 5
    return 2


def _apply_mastery_direct(
    db: Session, user_id: str, topic_id: str, pct: float
) -> tuple[int, int]:
    """(before, after) — the shared rule applied straight to the Mastery row."""
    row = db.execute(
        select(Mastery).where(Mastery.user_id == user_id, Mastery.topic_id == topic_id)
    ).scalar_one_or_none()
    before = int(row.value) if row is not None else 0
    after = max(before, min(95, before + _mastery_delta(pct)))
    trend = "up" if after > before else "flat"
    if row is None:
        db.add(Mastery(user_id=user_id, topic_id=topic_id, value=after, trend=trend))
    else:
        row.value = after
        row.trend = trend if after > before else row.trend
    db.flush()
    return before, after


def _apply_mastery(db: Session, user_id: str, topic_id: str, pct: float) -> tuple[int, int]:
    """Prefer Agent-Tutor's shared helper when it exists; fall back to direct."""
    try:
        from app.services import mastery as mastery_service  # noqa: PLC0415
    except ImportError:
        return _apply_mastery_direct(db, user_id, topic_id, pct)
    for name in ("apply_quiz_result", "apply_score", "apply_delta", "apply"):
        fn = getattr(mastery_service, name, None)
        if not callable(fn):
            continue
        try:
            result = fn(db, user_id, topic_id, pct)
        except TypeError:
            continue  # unknown signature — try the next candidate / fallback
        except Exception:  # helper bug must not break quiz submission
            log.warning("mastery helper %s failed; using direct update", name)
            break
        if (
            isinstance(result, tuple)
            and len(result) == 2
            and all(isinstance(v, int) for v in result)
        ):
            return result  # (before, after)
        break  # helper ran but returned another shape — recompute directly below
    return _apply_mastery_direct(db, user_id, topic_id, pct)


def submit_quiz(db: Session, user: User, quiz_id: str, body) -> dict:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None or quiz.user_id != user.id:
        raise NotFound("Quiz")
    questions = list(quiz.questions)
    by_id = {q.id: q for q in questions}

    selected: dict[str, int | None] = {}
    for answer in body.answers:
        if answer.question_id not in by_id:
            raise AppError(
                "VALIDATION_ERROR", "Unknown questionId in answers.", 422
            )
        selected[answer.question_id] = answer.selected_index

    score = 0
    per_question: list[dict] = []
    tag_totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # tag -> [correct, total]
    for q in questions:
        chosen = selected.get(q.id)
        correct = chosen is not None and int(chosen) == int(q.correct_index)
        if correct:
            score += 1
        tag = q.tag or "Concepts"
        tag_totals[tag][0] += 1 if correct else 0
        tag_totals[tag][1] += 1
        per_question.append(
            {
                "questionId": q.id,
                "correct": correct,
                "correctIndex": int(q.correct_index),
                "explanation": q.explanation or "",
            }
        )

    total = len(questions)
    pct = score / total if total else 0.0
    strengths = sorted(t for t, (c, n) in tag_totals.items() if n and c / n >= 0.75)
    weaknesses = sorted(t for t, (c, n) in tag_totals.items() if n and c / n < 0.5)

    mastery_before: int | None = None
    mastery_after: int | None = None
    if quiz.topic_id:
        mastery_before, mastery_after = _apply_mastery(db, user.id, quiz.topic_id, pct)

    db.add(
        QuizAttempt(
            id=new_id(),
            quiz_id=quiz.id,
            user_id=user.id,
            score=score,
            total=total,
            answers=[
                {"questionId": qid, "selectedIndex": idx} for qid, idx in selected.items()
            ],
            strengths=strengths,
            weaknesses=weaknesses,
        )
    )
    db.flush()

    if weaknesses and quiz.topic_id:
        recommendation = {"title": "Practice weak areas", "route": f"/quiz/{quiz.topic_id}"}
    else:
        recommendation = {"title": "Keep the momentum", "route": "/"}

    return {
        "score": score,
        "total": total,
        "masteryBefore": mastery_before,
        "masteryAfter": mastery_after,
        "perQuestion": per_question,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
    }
