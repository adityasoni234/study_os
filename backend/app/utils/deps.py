"""Shared FastAPI dependencies.

Auth (MVP): header ``X-User-ID`` (missing/blank → ``demo-user``). The User row —
and its Profile — are auto-created on first sight. Real auth later swaps the
internals of ``get_current_user`` without touching any endpoint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import get_db

if TYPE_CHECKING:  # models are imported lazily at runtime (see below)
    from app.models.user import User

DEMO_USER_ID = "demo-user"
_ID_MAX_LEN = 32  # id columns are String(32)


def _construct(model: type, **kwargs: Any):
    """Build a model instance from the kwargs it actually has (tolerates schema drift)."""
    return model(**{k: v for k, v in kwargs.items() if hasattr(model, k)})


def get_current_user(request: Request, db: Session = Depends(get_db)) -> "User":
    # Lazy import so app.utils never depends on models at import time — import
    # order (and partially-built trees) can never break the app.
    from app.models.user import Profile, User

    raw = request.headers.get("X-User-ID") or DEMO_USER_ID
    user_id = raw.strip()[:_ID_MAX_LEN] or DEMO_USER_ID

    user = db.get(User, user_id)
    profile = db.get(Profile, user_id)
    if user is not None and profile is not None:
        return user

    if user is None:
        user = _construct(
            User,
            id=user_id,
            name="Aditya" if user_id == DEMO_USER_ID else "Learner",
        )
        db.add(user)
    if profile is None:
        db.add(
            _construct(
                Profile,
                user_id=user_id,
                level="Beginner",
                daily_goal_minutes=30,
                explanation_style="simple",
                streak_days=0,
                preferences={},
            )
        )
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request created the same row first — use theirs.
        db.rollback()
        user = db.get(User, user_id)
        if user is None:  # pragma: no cover - only under pathological races
            raise
    return user
