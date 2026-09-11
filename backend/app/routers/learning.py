"""Learning endpoints: mastery, recommendations, daily mission."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.services import mastery, mission
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["learning"])


@router.get("/mastery")
def list_mastery(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok({"topics": mastery.list_summary(db, user.id)})


@router.get("/mastery/{topic_id}")
def get_mastery(
    topic_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(mastery.topic_summary(db, user.id, topic_id))


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok({"recommendations": mission.recommendations(db, user)})


@router.get("/daily-mission")
def get_daily_mission(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    row = mission.get_or_create(db, user)
    return ok(mission.to_out(db, row))


@router.post("/daily-mission/steps/{step_id}/complete")
def complete_mission_step(
    step_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(mission.complete_step(db, user, step_id))
