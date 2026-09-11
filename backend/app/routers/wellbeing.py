"""Wellbeing endpoints: POST /wellbeing/session, POST /journal, GET /journal.

Thin per convention: validate → service → envelope. No extra logging here —
journal notes and talk messages must never reach a log line.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.wellbeing import JournalCreateRequest, WellbeingSessionRequest
from app.services import wellbeing
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["wellbeing"])


@router.post("/wellbeing/session")
def wellbeing_session(
    payload: WellbeingSessionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(wellbeing.run_session(db, user, payload.kind, payload.message))


@router.post("/journal")
def create_journal_entry(
    payload: JournalCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(
        wellbeing.create_journal_entry(
            db, user, mood=payload.mood, mood_label=payload.mood_label, note=payload.note
        )
    )


@router.get("/journal")
def list_journal(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(wellbeing.list_journal(db, user))
