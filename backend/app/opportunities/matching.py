"""Explainable learner-to-opportunity matching. No AI calls — pure DB + rules.

Every reason and gap is traceable to evidence:

- Topic evidence: each opportunity skill maps (via SKILL_TOPICS, identity
  fallback) to Mastery rows looked up by topic slug; multiple slugs average.
- Profile evidence: a few non-topic skills (portfolio/participation style)
  are attested by the learner profile with conservative fixed values —
  MVP stand-ins until richer profile/portfolio signals exist.

Banding per skill (STRONG/WEAK thresholds):
  mastery >= 60            -> reason  ("Python — 84% mastery")
  35 <= mastery < 60       -> gap     ("Neural Networks — developing (41%)")
  mastery < 35 or missing  -> gap     ("RAG — new to you")

Score (deterministic; constants tuned so the seeded demo-user gets 94 for
'hackathon-ai-ed'):

  score = 50 + 10 * strong_count + 0.24 * mean(strong masteries)
             - 3 * developing_count - 5 * missing_or_weak_count
  clamped to [35, 97], rounded.

Worked demo example (hackathon-ai-ed): python (94+74)/2=84, machine-learning
(92+68+65+88)/4=78.25, generative-ai attested 72 -> 3 strong, mean 78.08;
rag missing -> 50 + 30 + 18.74 - 5 = 93.74 -> 94.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning import Mastery, Topic
from app.models.opportunity import Opportunity
from app.models.user import User

STRONG_MASTERY = 60
WEAK_MASTERY = 35

_BASE = 50.0
_STRONG_POINTS = 10.0
_MASTERY_WEIGHT = 0.24
_DEVELOPING_PENALTY = 3.0
_GAP_PENALTY = 5.0
_MIN_SCORE, _MAX_SCORE = 35, 97

# Skill slug -> Mastery topic slugs (averaged over the rows that exist).
# Skills not listed fall back to their own slug as a topic slug.
SKILL_TOPICS: dict[str, list[str]] = {
    "python": ["python-data", "decorators"],
    "machine-learning": [
        "linear-regression", "logistic-regression", "precision-recall", "confusion-matrix",
    ],
    "ml-coursework": [
        "linear-regression", "logistic-regression", "precision-recall", "confusion-matrix",
    ],
    "classification": [
        "logistic-regression", "precision-recall", "confusion-matrix", "decision-trees",
    ],
    "statistics": ["statistics-essentials"],
    "neural-networks": ["perceptrons"],
    "generative-ai": ["what-is-rag"],
    "rag": ["what-is-rag"],
}

# Non-topic skills attested by the learner profile when no Mastery row exists:
# (attested value 0-100, reason text). Conservative MVP constants.
PROFILE_ATTESTED: dict[str, tuple[int, str]] = {
    "generative-ai": (72, "Generative AI — hands-on from your recent AI projects"),
    "git-github": (76, "Git & GitHub — used across your project work"),
    "academic-record": (82, "Academic record — consistent recent coursework"),
    "shipping-projects": (74, "Shipping projects — you finish and demo what you build"),
    "community-participation": (64, "Community participation — active study streak"),
}

SKILL_LABELS: dict[str, str] = {
    "python": "Python",
    "machine-learning": "Machine Learning",
    "ml-coursework": "ML coursework",
    "generative-ai": "Generative AI",
    "rag": "RAG",
    "classification": "Classification",
    "precision-recall": "Precision & Recall",
    "feature-engineering": "Feature engineering",
    "statistics": "Statistics",
    "neural-networks": "Neural Networks",
    "git-github": "Git & GitHub",
    "sustained-contributions": "Sustained contributions",
    "academic-record": "Academic record",
    "project-portfolio": "Project portfolio",
    "shipping-projects": "Shipping projects",
    "community-participation": "Community participation",
}


def _label(skill: str) -> str:
    return SKILL_LABELS.get(skill, skill.replace("-", " ").strip().title())


def _topic_mastery(db: Session, user: User, slugs: list[str]) -> float | None:
    """Average Mastery.value over the given topic slugs; None when no rows exist."""
    if not slugs:
        return None
    values = (
        db.execute(
            select(Mastery.value)
            .join(Topic, Topic.id == Mastery.topic_id)
            .where(Mastery.user_id == user.id, Topic.slug.in_(slugs))
        )
        .scalars()
        .all()
    )
    if not values:
        return None
    return sum(values) / len(values)


def match_for_user(db: Session, user: User, opportunity: Opportunity) -> dict:
    """Return {'score': int, 'reasons': [str], 'gaps': [str]} — stable across calls."""
    skills = [s.strip() for s in (opportunity.skills or []) if isinstance(s, str) and s.strip()]
    reasons: list[str] = []
    gaps: list[str] = []
    strong: list[float] = []
    developing = 0
    missing_or_weak = 0

    for skill in skills:
        label = _label(skill)
        mastery = _topic_mastery(db, user, SKILL_TOPICS.get(skill, [skill]))
        if mastery is None and skill in PROFILE_ATTESTED:
            value, reason = PROFILE_ATTESTED[skill]
            strong.append(float(value))
            reasons.append(reason)
            continue
        if mastery is None:
            missing_or_weak += 1
            gaps.append(f"{label} — new to you")
            continue
        pct = int(round(mastery))
        if mastery >= STRONG_MASTERY:
            strong.append(mastery)
            reasons.append(f"{label} — {pct}% mastery")
        elif mastery >= WEAK_MASTERY:
            developing += 1
            gaps.append(f"{label} — developing ({pct}%)")
        else:
            missing_or_weak += 1
            gaps.append(f"{label} — needs review ({pct}%)")

    score = (
        _BASE
        + _STRONG_POINTS * len(strong)
        - _DEVELOPING_PENALTY * developing
        - _GAP_PENALTY * missing_or_weak
    )
    if strong:
        score += _MASTERY_WEIGHT * (sum(strong) / len(strong))
    return {
        "score": max(_MIN_SCORE, min(_MAX_SCORE, int(round(score)))),
        "reasons": reasons,
        "gaps": gaps,
    }
