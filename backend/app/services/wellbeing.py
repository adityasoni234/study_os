"""Wellbeing sessions + journal. Supportive study wellbeing ONLY.

Hard scope rules (do not loosen):
- No diagnosis, no treatment claims, no therapist roleplay — ever.
- Every wellbeing response carries DISCLAIMER.
- Privacy: WellbeingLog stores the session *kind* only — never the student's
  message. Journal note content is stored for the student's own journal but is
  never logged and never sent to any AI model.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import router as ai_router
from app.ai.base import TaskType
from app.models.user import User
from app.models.wellbeing import JournalEntry, WellbeingLog
from app.schemas.wellbeing import (
    JournalEntryOut,
    JournalListResponse,
    WellbeingSessionResponse,
)
from app.utils.errors import AppError

DISCLAIMER = "StudyOS offers study support, not medical or mental-health care."

VALID_KINDS: tuple[str, ...] = ("reset", "plan", "talk")

# --- reset: static calm copy, no AI call -------------------------------------

_RESET_REPLY = (
    "Let's take a short pause together. Sit back, let your shoulders drop, and "
    "breathe in slowly through your nose for four counts, hold for four, then "
    "let it out for six. Even two minutes of this tells your body the pressure "
    "is off — your notes will still be there, and you'll come back to them "
    "steadier."
)
_RESET_SUGGESTIONS = ["2-minute breath", "5-minute breath"]

# --- plan: supportive lighter-week planning ----------------------------------

_PLAN_SYSTEM = """You are StudyOS's wellbeing planner — a calm, practical study companion.

Hard scope rules:
- Supportive study-life planning ONLY. You are NOT a doctor, therapist, or counsellor, and you never roleplay as one.
- Never diagnose, never name or suggest conditions, never make medical or treatment claims.
- If the student sounds in serious distress, add one gentle, non-alarming sentence encouraging them to talk to someone they trust or to professional support.

Task: the student feels overloaded. In 3-6 warm sentences, acknowledge the load without judgment, then propose a concretely LIGHTER week: shorter or fewer sessions, one thing deferred, and one protected rest block. Be specific and kind. No clinical language, no bullet lists, no lectures."""

_PLAN_FALLBACK_REPLY = (
    "It sounds like this week has been carrying more than it should — that's "
    "worth taking seriously, and it doesn't mean you're falling behind as a "
    "person. Let's make next week deliberately lighter: keep sessions to about "
    "20 focused minutes, park one topic until next week, and put one full "
    "evening completely off-limits for study. A lighter plan you actually "
    "finish beats a heavy one that finishes you."
)
_PLAN_SUGGESTIONS = [
    "Trim sessions to 20 focused minutes",
    "Defer one topic to next week",
    "Protect one full evening off",
]

# --- talk: warm, non-clinical listening --------------------------------------

_TALK_SYSTEM = """You are StudyOS's wellbeing companion — a warm, steady, non-clinical listener for students.

Hard scope rules:
- Supportive study wellbeing ONLY. You are NOT a therapist, counsellor, or doctor, and you never roleplay as one.
- Never diagnose, never label conditions, never make medical or treatment claims.
- If the student mentions serious distress or crisis, respond with care and gently encourage reaching out to someone they trust or to professional support — one calm sentence, no drama, no clinical language.

How to reply: 3-5 sentences. Listen first — reflect back what they said in plain words, validate the feeling as a normal part of student life, then offer at most one small optional next step (a short pause, a walk, a line in their journal, a lighter plan). Warm and human; no bullet lists, no lectures."""

_TALK_FALLBACK_REPLY = (
    "Thanks for saying that out loud — pressure grows quietly when it stays in "
    "your head, and naming it is already a step. Whatever today looked like, "
    "it doesn't erase the fact that you keep showing up, and that counts. If "
    "it helps, take one slow breath, jot a line in your journal about how this "
    "feels, and let your next study block be a small one."
)
_TALK_SUGGESTIONS = ["Try a 2-minute reset", "Jot this in your journal"]

_DEFAULT_PLAN_MESSAGE = "My study week feels too heavy and I need a lighter plan."
_DEFAULT_TALK_MESSAGE = "I could use a supportive check-in about how studying feels."


def run_session(
    db: Session, user: User, kind: str, message: str | None
) -> WellbeingSessionResponse:
    kind = (kind or "").strip().lower()
    if kind not in VALID_KINDS:
        raise AppError("VALIDATION_ERROR", "kind must be one of: reset, plan, talk.", 400)

    if kind == "reset":
        reply, suggestions = _RESET_REPLY, list(_RESET_SUGGESTIONS)
    elif kind == "plan":
        reply = _generate_reply(
            system=_PLAN_SYSTEM,
            user_text=(message or "").strip() or _DEFAULT_PLAN_MESSAGE,
            fallback=_PLAN_FALLBACK_REPLY,
        )
        suggestions = list(_PLAN_SUGGESTIONS)
    else:  # talk
        reply = _generate_reply(
            system=_TALK_SYSTEM,
            user_text=(message or "").strip() or _DEFAULT_TALK_MESSAGE,
            fallback=_TALK_FALLBACK_REPLY,
        )
        suggestions = list(_TALK_SUGGESTIONS)

    # Record that a session happened — never its content (privacy rule).
    db.add(WellbeingLog(user_id=user.id, kind=kind, note=None))
    db.flush()
    return WellbeingSessionResponse(reply=reply, suggestions=suggestions, disclaimer=DISCLAIMER)


def _generate_reply(*, system: str, user_text: str, fallback: str) -> str:
    """AI reply when a live provider answers; curated supportive copy otherwise.

    The generic mock provider text reads like a tutor, not a wellbeing
    companion — so when the mock handled the call (tests, offline mode) we use
    hand-written copy instead. Wellbeing must never 503: AI errors fall back too.
    """
    try:
        result = ai_router.generate(
            TaskType.CHAT,
            [{"role": "user", "content": user_text}],
            system=system,
            max_tokens=400,
            temperature=0.6,
        )
    except AppError:
        return fallback
    if result.provider == "mock" or not result.text.strip():
        return fallback
    return result.text.strip()


# --- journal ------------------------------------------------------------------

_EVENING_START_HOUR = 18

_BRIGHT_LABELS = {
    "great", "good", "happy", "calm", "focused", "motivated", "energised",
    "energized", "relaxed", "proud", "okay", "fine", "hopeful", "confident",
}
_BRIGHT_MOODS = {"😊", "😄", "🙂", "😌", "🤩", "💪", "✨", "😃", "🥳"}


def create_journal_entry(
    db: Session, user: User, *, mood: str, mood_label: str, note: str
) -> JournalEntryOut:
    entry = JournalEntry(
        user_id=user.id, mood=mood.strip(), mood_label=mood_label.strip(), note=note
    )
    db.add(entry)
    db.flush()
    return _entry_out(entry)


def list_journal(db: Session, user: User) -> JournalListResponse:
    entries = (
        db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at.desc(), JournalEntry.id.desc())
            .limit(50)
        )
        .scalars()
        .all()
    )
    return JournalListResponse(
        entries=[_entry_out(e) for e in entries], pattern=_pattern(list(entries))
    )


def _entry_out(entry: JournalEntry) -> JournalEntryOut:
    return JournalEntryOut(
        id=entry.id,
        mood=entry.mood,
        mood_label=entry.mood_label,
        note=entry.note,
        created_at=entry.created_at,
    )


def _is_bright(entry: JournalEntry) -> bool:
    return (
        entry.mood_label.strip().lower() in _BRIGHT_LABELS
        or entry.mood.strip() in _BRIGHT_MOODS
    )


def _pattern(entries: list[JournalEntry]) -> str | None:
    """One gentle, non-judgmental observation once ≥3 entries exist.

    Counts only — evening-vs-day timing and mood brightness. Wording always
    stays soft ("Noticed gently: …"); never a verdict about the student.
    """
    if len(entries) < 3:
        return None

    evening = [e for e in entries if e.created_at.hour >= _EVENING_START_HOUR]
    day = [e for e in entries if e.created_at.hour < _EVENING_START_HOUR]

    if evening and day:
        evening_rate = sum(1 for e in evening if _is_bright(e)) / len(evening)
        day_rate = sum(1 for e in day if _is_bright(e)) / len(day)
        if day_rate - evening_rate >= 0.25:
            return (
                "Noticed gently: your daytime check-ins tend to read a little "
                "brighter than the late-evening ones. An earlier wind-down on "
                "heavy days might be worth a try."
            )
        if evening_rate - day_rate >= 0.25:
            return (
                "Noticed gently: your evening check-ins tend to read a little "
                "brighter than the daytime ones — winding the day down seems "
                "to suit you."
            )

    if len(evening) > len(day):
        return (
            "Noticed gently: most of your recent check-ins happen in the "
            "evening. A two-minute reset before late sessions could make them "
            "feel lighter."
        )
    if len(day) > len(evening):
        return (
            "Noticed gently: most of your recent check-ins happen earlier in "
            "the day — those daytime pauses seem to be part of your rhythm."
        )
    return (
        "Noticed gently: you've been checking in steadily. The habit itself is "
        "the win — clearer patterns will show up as entries add up."
    )
