"""Assessment endpoints: quiz generate/submit + flashcards."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import User
from app.schemas.assessment import (
    FlashcardsGenerateRequest,
    QuizGenerateRequest,
    QuizSubmitRequest,
)
from app.services import flashcards as flashcards_service
from app.services import quiz as quiz_service
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["assessment"])


@router.post("/quiz/generate")
def generate_quiz(
    body: QuizGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(quiz_service.generate_quiz(db, user, body))


@router.post("/quiz/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    body: QuizSubmitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(quiz_service.submit_quiz(db, user, quiz_id, body))


@router.post("/flashcards/generate")
def generate_flashcards(
    body: FlashcardsGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(flashcards_service.generate_flashcards(db, user, body))
