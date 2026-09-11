"""Seed the 6 demo opportunities. Idempotent (check by id before insert).

Mirrors the frontend mock data in src/data/opportunities.ts exactly (ids, titles,
orgs, types, tones, deadlines, modes, eligibility, sources, blurbs) so the demo
UI and API stay in lockstep. `skills` are derived from each card's match-reason
labels as topic-ish slugs; `days_left` is the static demo value from the
frontend (a future live adapter refreshes it from `deadline_date`).

OPPORTUNITIES is also the corpus behind app.opportunities.adapters.MockSearchAdapter.
"""

import datetime as dt

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity

# Final column values for the `opportunities` table (deadline_date is derived).
OPPORTUNITIES: list[dict] = [
    {
        "id": "hackathon-ai-ed",
        "title": "HackForEd — AI for Education Hackathon",
        "org": "EdTech India Collective",
        "type": "Hackathon",
        "tone": "violet",
        "deadline_text": "Sep 18",
        "days_left": 7,
        "mode": "Online",
        "eligibility": "Open to students 18+, teams of 1–4",
        "skills": ["python", "machine-learning", "generative-ai", "rag"],
        "source": "devfolio.co",
        "source_url": "https://devfolio.co",
        "verified": True,
        "description": (
            "Build an AI tool that improves how people learn. "
            "₹2L prize pool + incubation support."
        ),
    },
    {
        "id": "kaggle-classification",
        "title": "Binary Classification Challenge",
        "org": "Kaggle Community",
        "type": "Competition",
        "tone": "sky",
        "deadline_text": "Sep 30",
        "days_left": 19,
        "mode": "Online",
        "eligibility": "Open to everyone, free entry",
        "skills": ["classification", "precision-recall", "feature-engineering"],
        "source": "kaggle.com",
        "source_url": "https://kaggle.com",
        "verified": True,
        "description": (
            "A friendly playground competition scored on F1 — a perfect way to "
            "apply exactly what you’re learning this week."
        ),
    },
    {
        "id": "research-internship",
        "title": "ML Research Winter Internship",
        "org": "IISc Computational Lab",
        "type": "Research",
        "tone": "indigo",
        "deadline_text": "Oct 10",
        "days_left": 29,
        "mode": "Bengaluru · Hybrid",
        "eligibility": "Undergraduates, 3rd year+",
        "skills": ["python", "statistics", "neural-networks"],
        "source": "iisc.ac.in",
        "source_url": "https://iisc.ac.in",
        "verified": True,
        "description": (
            "An 8-week mentored research project in applied ML. Strong fit once "
            "you reach your Neural Networks milestone."
        ),
    },
    {
        "id": "gsoc-prep",
        "title": "Google Summer of Code — Early Prep",
        "org": "Open Source Community",
        "type": "Open Source",
        "tone": "mint",
        "deadline_text": "Orgs announced Feb",
        "days_left": None,
        "mode": "Online",
        "eligibility": "Students & newcomers to open source",
        "skills": ["python", "git-github", "sustained-contributions"],
        "source": "summerofcode.withgoogle.com",
        "source_url": "https://summerofcode.withgoogle.com",
        "verified": True,
        "description": (
            "Successful applicants start contributing months early. Your Python "
            "strength makes scikit-learn issues a great entry point."
        ),
    },
    {
        "id": "ai-scholarship",
        "title": "National AI Talent Scholarship",
        "org": "FutureSkills Foundation",
        "type": "Scholarship",
        "tone": "amber",
        "deadline_text": "Oct 2",
        "days_left": 21,
        "mode": "Online application",
        "eligibility": "Undergraduate students in India",
        "skills": ["academic-record", "ml-coursework", "project-portfolio"],
        "source": "futureskills.org",
        "source_url": "https://futureskills.org",
        "verified": True,
        "description": (
            "₹1L learning grant for promising AI students. Your portfolio "
            "project would strengthen the application significantly."
        ),
    },
    {
        "id": "campus-fellowship",
        "title": "Campus AI Builders Fellowship",
        "org": "Builders Collective",
        "type": "Fellowship",
        "tone": "coral",
        "deadline_text": "Rolling",
        "days_left": None,
        "mode": "Online + meetups",
        "eligibility": "Student builders, any year",
        "skills": ["shipping-projects", "community-participation"],
        "source": "builderscollective.dev",
        "source_url": "https://builderscollective.dev",
        "verified": True,
        "description": (
            "A semester-long cohort where students ship one AI product with "
            "mentorship from industry engineers."
        ),
    },
]


def _parse_deadline(text: str) -> dt.date | None:
    """Best-effort date for display strings like "Sep 18" (next occurrence).

    Non-date strings ("Rolling", "Orgs announced Feb") return None. Purely
    informative — sorting uses the static `days_left` demo values.
    """
    try:
        parsed = dt.datetime.strptime(text, "%b %d")
    except ValueError:
        return None
    today = dt.date.today()
    candidate = dt.date(today.year, parsed.month, parsed.day)
    if candidate < today:
        candidate = dt.date(today.year + 1, parsed.month, parsed.day)
    return candidate


def seed(session: Session) -> None:
    for spec in OPPORTUNITIES:
        if session.get(Opportunity, spec["id"]) is None:
            session.add(
                Opportunity(deadline_date=_parse_deadline(spec["deadline_text"]), **spec)
            )
    session.flush()
