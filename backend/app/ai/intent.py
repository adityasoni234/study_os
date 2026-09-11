"""Fast intent classification for tutor messages.

Rule-first (regex keywords, fully offline). Only when the rules are ambiguous
(two or more different modes matched) AND the app is in live AI mode do we ask
the model with a tiny prompt — and any error there falls back to "teach".
"""

from __future__ import annotations

import re

from app.ai.base import TaskType
from app.config import settings

MODES: tuple[str, ...] = (
    "teach",
    "practice",
    "review",
    "quiz",
    "feedback",
    "mastery",
    "explain_differently",
)

# Priority-ordered: earlier rules win ties when we cannot ask the model.
_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("quiz", re.compile(r"\b(test|quiz(?:zes)?|exam|mcqs?|assess(?:ment)?)\b", re.IGNORECASE)),
    (
        "explain_differently",
        re.compile(
            r"\b(simpler|simplify|analog(?:y|ies)|metaphor|examples?|visual(?:ly|ise|ize)?|"
            r"diagram|eli5|differently)\b|\banother way\b|\bsimple (?:terms|words)\b|"
            r"\breal[- ]world\b",
            re.IGNORECASE,
        ),
    ),
    (
        "review",
        re.compile(
            r"\b(review|recap|revise|revisit|refresher|again|forgot|forget)\b", re.IGNORECASE
        ),
    ),
    (
        "practice",
        re.compile(r"\b(practi[cs]e|drill|exercises?|worksheet)\b", re.IGNORECASE),
    ),
    (
        "feedback",
        re.compile(r"\b(feedback|grade)\b|\bcheck my answer\b|\bhow did i do\b", re.IGNORECASE),
    ),
    (
        "mastery",
        re.compile(r"\b(mastery|progress|score)\b|\bhow am i doing\b", re.IGNORECASE),
    ),
)


def classify(message: str) -> str:
    """Map a student message to a tutor mode. Deterministic and offline-safe."""
    text = (message or "").strip()
    if not text:
        return "teach"
    matched = [mode for mode, pattern in _RULES if pattern.search(text)]
    if not matched:
        return "teach"
    if len(matched) == 1:
        return matched[0]
    # Ambiguous: several rule families fired. Ask the model only in live mode.
    if settings.resolved_ai_mode == "live":
        return _classify_with_ai(text) or "teach"
    return matched[0]


def _classify_with_ai(message: str) -> str | None:
    """Tiny model call to break a tie. Returns None on any problem."""
    try:
        from app.ai import router  # local import keeps startup light

        data, _ = router.generate_json(
            TaskType.INTENT,
            [{"role": "user", "content": f"Student message: {message[:400]}"}],
            system="Classify the student's intent for a tutoring app.",
            max_tokens=16,
            schema_hint=(
                'Return ONLY JSON: {"mode": "..."} where mode is one of '
                '"teach", "practice", "review", "quiz", "feedback", "mastery", '
                '"explain_differently".'
            ),
        )
        mode = str(data.get("mode", "")).strip().lower()
        return mode if mode in MODES else None
    except Exception:
        return None
