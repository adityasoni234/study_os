"""Tutor orchestration: sessions, learner context, mode routing, quiz checks.

Flow per message (handle_message):
  resolve/create the LearningSession → persist the student Message → infer the
  mode (explicit > intent rules) → build learner context (profile, mastery,
  weak topics, recent history, retrieval hits) → route to the right AI task →
  persist the tutor Message → return the contract-shaped dict.

Provider/model names never appear in anything returned from here.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import intent, prompts
from app.ai import router as ai_router
from app.ai.base import AIMessage, TaskType
from app.models.learning import LearningSession, Mastery, Message, Topic
from app.models.user import Profile, User
from app.schemas.tutor import TutorMessageIn
from app.services import mastery as mastery_service
from app.utils.errors import AppError, NotFound

HISTORY_LIMIT = 6
RETRIEVAL_K = 4
_WHY_RE = re.compile(r"\bwhy\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------


def handle_message(
    db: Session,
    user: User,
    body: TutorMessageIn,
    *,
    fixed_session_id: str | None = None,
) -> dict:
    """Process one student message and return the tutor/message contract dict.

    ``fixed_session_id`` lets the flat /chat endpoint reuse one well-known
    session per user (created on first use) instead of minting new sessions.
    """
    message_text = (body.message or "").strip()
    is_answer = body.answer_index is not None and bool(body.question_id)
    if not message_text and not is_answer:
        raise AppError("VALIDATION_ERROR", "Invalid request. Check: message.", 422)

    session = _resolve_session(db, user, body.session_id, fixed_session_id)

    mode = body.mode if body.mode in intent.MODES else None
    if is_answer:
        mode = "feedback"
    elif mode is None:
        mode = intent.classify(message_text)
    if mode == "feedback" and not is_answer:
        mode = "review"  # "give me feedback" without an answer reads as review

    # Topic: explicit beats the session's remembered one; unknown slugs create
    # a Topic row so mastery can attach to it.
    topic: Topic | None = None
    topic_ref = body.topic_id or session.topic_id
    if topic_ref:
        topic = mastery_service.ensure_topic(db, topic_ref)
        session.topic_id = topic.id
    mastery_row = (
        mastery_service.get_or_create(db, user.id, topic.slug or topic.id) if topic else None
    )

    history = _history(db, session.id)
    _persist(db, session, "student", message_text or f"(answered option {body.answer_index})")

    hits: list = []
    citations: list[dict] = []
    if mode != "feedback" and message_text and (topic is not None or "?" in message_text):
        hits, citations = _retrieve(db, user.id, message_text)

    system_prompt = _system_prompt(db, user, topic, mastery_row, hits)
    ai_history = _to_ai_messages(history)

    misconception: str | None = None
    mastery_delta = 0
    quiz_out: dict | None = None
    answer_correct: bool | None = None

    if mode == "feedback":
        reply_text, misconception, mastery_row, mastery_delta, topic, answer_correct = (
            _handle_feedback(db, user, body, topic)
        )
    elif mode == "explain_differently":
        reply_text = _handle_explain_differently(
            ai_history, history, message_text, topic, body.style, system_prompt
        )
    else:
        task = (
            TaskType.DEEP_EXPLAIN
            if mode in ("teach", "review", "practice") and _wants_deep_explain(message_text)
            else TaskType.TUTOR_FAST
        )
        result = ai_router.generate(
            task,
            [*ai_history, {"role": "user", "content": message_text}],
            system=system_prompt,
            max_tokens=800,
        )
        reply_text = result.text.strip() or "Let's take that step by step — tell me a bit more."

    tutor_payload: dict | None = None
    if mode == "quiz":
        quiz_stored = _generate_quiz_question(topic, message_text, hits)
        if quiz_stored is not None:
            tutor_payload = {"quiz": quiz_stored}

    tutor_msg = _persist(db, session, "tutor", reply_text, payload=tutor_payload)

    if tutor_payload is not None:
        stored = tutor_payload["quiz"]
        quiz_out = {
            "questionId": tutor_msg.id,
            "question": stored["question"],
            "options": stored["options"],
            "correctIndex": None,  # withheld; submit via mode="feedback"
        }

    session.mode = mode
    db.flush()

    topic_slug = (topic.slug or topic.id) if topic is not None else None
    return {
        "sessionId": session.id,
        "reply": {
            "role": "tutor",
            "text": reply_text,
            "citations": citations,
            "suggestions": _suggestions(mode, correct=answer_correct),
            "quiz": quiz_out,
        },
        "state": {
            "topicId": topic_slug,
            "mastery": int(mastery_row.value) if mastery_row is not None else None,
            "masteryDelta": mastery_delta,
            "mode": mode,
            "misconception": misconception,
        },
    }


def get_session_view(db: Session, user: User, session_id: str) -> dict:
    """GET /api/tutor/session/{id} — NotFound for unknown or foreign sessions."""
    session = db.get(LearningSession, session_id)
    if session is None or session.user_id != user.id:
        raise NotFound("Session")

    topic = db.get(Topic, session.topic_id) if session.topic_id else None
    mastery_value: int | None = None
    if topic is not None:
        row = db.execute(
            select(Mastery).where(Mastery.user_id == user.id, Mastery.topic_id == topic.id)
        ).scalar_one_or_none()
        mastery_value = int(row.value) if row is not None else None

    topic_slug = (topic.slug or topic.id) if topic is not None else None
    return {
        "id": session.id,
        "topicId": topic_slug,
        "messages": [
            {"role": m.role, "text": m.text, "createdAt": m.created_at}
            for m in _history(db, session.id, limit=None)
        ],
        "state": {
            "topicId": topic_slug,
            "mastery": mastery_value,
            "masteryDelta": 0,
            "mode": session.mode,
            "misconception": None,
        },
    }


# ---------------------------------------------------------------------------
# mode handlers
# ---------------------------------------------------------------------------


def _handle_feedback(
    db: Session,
    user: User,
    body: TutorMessageIn,
    topic: Topic | None,
) -> tuple[str, str | None, Mastery | None, int, Topic | None, bool]:
    """Evaluate a quiz answer: ground truth locally, feedback wording via AI."""
    stored = _pending_quiz(db, user, body.question_id or "")
    question = str(stored.get("question", ""))
    options = [str(o) for o in stored.get("options", [])]
    correct_index = int(stored.get("correctIndex", 0))
    explanation = str(stored.get("explanation") or "").strip()
    chosen = int(body.answer_index or 0)
    is_correct = chosen == correct_index

    quiz_topic_ref = stored.get("topicId") or (topic.slug if topic is not None else None)
    if quiz_topic_ref:
        topic = mastery_service.ensure_topic(db, str(quiz_topic_ref))

    data, _result = ai_router.generate_json(
        TaskType.EVALUATE_ANSWER,
        [
            {
                "role": "user",
                "content": prompts.evaluate_answer_prompt(
                    question,
                    options,
                    chosen,
                    correct_index,
                    topic=topic.title if topic is not None else None,
                ),
            }
        ],
        system=prompts.TUTOR_SYSTEM,
    )
    ai_agrees = data.get("correct") is is_correct
    feedback_text = str(data.get("feedback") or "").strip()

    if is_correct:
        misconception = None
        reply = (
            feedback_text
            if ai_agrees and feedback_text
            else "That's right — nicely done. "
            + (f"{explanation} " if explanation else "")
            + "Ready to stretch a little further?"
        )
    else:
        misconception = str(data.get("misconception") or "").strip() or None
        reply = (
            feedback_text
            if ai_agrees and feedback_text
            else "You're close — let's look at it together. "
            + (f"{explanation} " if explanation else "")
            + "Want to try a similar one?"
        )

    mastery_row: Mastery | None = None
    mastery_delta = 0
    if topic is not None:
        mastery_row, mastery_delta = mastery_service.apply_result(
            db, user.id, topic.slug or topic.id, correct=is_correct
        )

    return reply, misconception, mastery_row, mastery_delta, topic, is_correct


def _handle_explain_differently(
    ai_history: list[AIMessage],
    history: list[Message],
    message_text: str,
    topic: Topic | None,
    style: str | None,
    system_prompt: str,
) -> str:
    concept = message_text
    if topic is not None and len(message_text) < 60:
        concept = topic.title  # short chip taps ("Explain simpler") mean the topic
    previous = next((m.text for m in reversed(history) if m.role == "tutor"), None)
    prompt = prompts.explain_differently_prompt(
        concept,
        style=style or "simpler",
        previous_explanation=previous[:600] if previous else None,
    )
    result = ai_router.generate(
        TaskType.TUTOR_FAST,
        [*ai_history, {"role": "user", "content": prompt}],
        system=system_prompt,
        max_tokens=600,
    )
    return result.text.strip() or "Let me put that another way — tell me which part felt fuzzy."


def _generate_quiz_question(
    topic: Topic | None, message_text: str, hits: list
) -> dict | None:
    """One inline check question; the correct index stays server-side."""
    topic_title = topic.title if topic is not None else (message_text[:80] or "this topic")
    data, _result = ai_router.generate_json(
        TaskType.QUIZ_GEN,
        [
            {
                "role": "user",
                "content": prompts.quiz_prompt(
                    topic_title, n=1, context=_excerpt_block(hits) or None
                ),
            }
        ],
    )
    for candidate in data.get("questions") or []:
        if not isinstance(candidate, dict):
            continue
        prompt_text = str(candidate.get("prompt") or "").strip()
        options = candidate.get("options")
        correct_index = candidate.get("correctIndex")
        if (
            prompt_text
            and isinstance(options, list)
            and len(options) >= 2
            and isinstance(correct_index, int)
            and 0 <= correct_index < len(options)
        ):
            return {
                "question": prompt_text,
                "options": [str(o) for o in options],
                "correctIndex": correct_index,
                "explanation": str(candidate.get("explanation") or ""),
                "topicId": (topic.slug or topic.id) if topic is not None else None,
            }
    return None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _resolve_session(
    db: Session,
    user: User,
    session_id: str | None,
    fixed_session_id: str | None,
) -> LearningSession:
    if fixed_session_id:
        sid = fixed_session_id[:32]
        session = db.get(LearningSession, sid)
        if session is None:
            session = LearningSession(id=sid, user_id=user.id)
            db.add(session)
            db.flush()
        return session
    if session_id:
        session = db.get(LearningSession, session_id)
        if session is None or session.user_id != user.id:
            raise NotFound("Session")
        return session
    session = LearningSession(user_id=user.id)
    db.add(session)
    db.flush()
    return session


def _history(db: Session, session_id: str, limit: int | None = HISTORY_LIMIT) -> list[Message]:
    rows = (
        db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )
        .scalars()
        .all()
    )
    return rows[-limit:] if limit else rows


def _persist(
    db: Session, session: LearningSession, role: str, text: str, payload: dict | None = None
) -> Message:
    message = Message(session_id=session.id, role=role, text=text, payload=payload)
    db.add(message)
    db.flush()
    return message


def _to_ai_messages(history: list[Message]) -> list[AIMessage]:
    role_map = {"student": "user", "tutor": "assistant"}
    return [
        {"role": role_map.get(m.role, "user"), "content": m.text}
        for m in history
        if (m.text or "").strip()
    ]


def _retrieve(db: Session, user_id: str, query: str) -> tuple[list, list[dict]]:
    """Grounding hits + citation dicts; empty until Agent-RAG's store lands."""
    try:
        from app.retrieval.citations import build_citations
        from app.retrieval.store import search_chunks
    except ImportError:  # store not landed yet (built by Agent-RAG)
        return [], []
    except Exception:  # half-landed module must not break tutoring
        return [], []
    try:
        hits = search_chunks(db, user_id, query, k=RETRIEVAL_K)
        citations = [c.to_dict() for c in build_citations(hits)]
        return list(hits or []), citations
    except Exception:  # retrieval must never break tutoring
        return [], []


def _excerpt_block(hits: list) -> str:
    blocks = []
    for i, hit in enumerate(hits, start=1):
        text = " ".join(str(getattr(hit, "text", "")).split())[:700]
        title = getattr(hit, "source_title", "Source")
        if text:
            blocks.append(f"[S{i}] {title}\n{text}")
    return "\n\n".join(blocks)


def _system_prompt(
    db: Session,
    user: User,
    topic: Topic | None,
    mastery_row: Mastery | None,
    hits: list,
) -> str:
    lines: list[str] = []
    profile = db.get(Profile, user.id)
    if profile is not None:
        lines.append(
            f"- Student level: {profile.level}; preferred explanation style: "
            f"{profile.explanation_style}."
        )
    if topic is not None and mastery_row is not None:
        lines.append(
            f"- Current topic: {topic.title} (mastery {int(mastery_row.value)}%, "
            f"trend {mastery_row.trend})."
        )
    weak = mastery_service.weak_topics(db, user.id, below=60, limit=3)
    if weak:
        lines.append(
            "- Weaker topics to reinforce gently when relevant: "
            + ", ".join(f"{w.title} ({w.mastery}%)" for w in weak)
            + "."
        )

    system = prompts.TUTOR_SYSTEM
    if lines:
        system += "\n\nSTUDENT CONTEXT:\n" + "\n".join(lines)
    excerpts = _excerpt_block(hits)
    if excerpts:
        system += "\n\nCONTEXT (excerpts from the student's own sources):\n" + excerpts
    return system


def _pending_quiz(db: Session, user: User, question_id: str) -> dict:
    """The stored quiz payload for a questionId (= tutor Message id) the user owns."""
    message = db.get(Message, question_id) if question_id else None
    payload = message.payload if message is not None else None
    if not payload or not isinstance(payload.get("quiz"), dict):
        raise NotFound("Quiz question")
    session = db.get(LearningSession, message.session_id)
    if session is None or session.user_id != user.id:
        raise NotFound("Quiz question")
    return payload["quiz"]


def _wants_deep_explain(message: str) -> bool:
    if len(message) < 40:
        return False
    lower = message.lower()
    return "confused" in lower or _WHY_RE.search(message) is not None


def _suggestions(mode: str, *, correct: bool | None = None) -> list[str]:
    """3-4 contextual quick-reply chips."""
    if mode == "feedback":
        if correct:
            return ["Next question ✏️", "Make it harder", "Why does this work?", "Switch topic"]
        return [
            "Explain simpler",
            "Real-world example",
            "Try a similar question",
            "Break it into steps",
        ]
    if mode == "quiz":
        return ["Another question ✏️", "Explain this answer", "Make it easier"]
    if mode == "explain_differently":
        return ["Give me an analogy", "Show it in code", "Test me ✏️"]
    if mode == "practice":
        return ["Harder practice", "Check my answer", "Explain simpler"]
    if mode == "review":
        return ["Quick recap", "Test me ✏️", "What am I still missing?"]
    if mode == "mastery":
        return ["What should I review?", "Test me ✏️", "Start today's mission"]
    return ["Explain simpler", "Test me ✏️", "Real-world example", "Why does this matter?"]
