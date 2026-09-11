"""Tutor endpoints: POST /api/tutor/message, GET /api/tutor/session/{id}."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.tutor import TutorMessageIn
from app.services import tutor
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["tutor"])


@router.post("/tutor/message")
def tutor_message(
    body: TutorMessageIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(tutor.handle_message(db, user, body))


@router.get("/tutor/session/{session_id}")
def tutor_session(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(tutor.get_session_view(db, user, session_id))
