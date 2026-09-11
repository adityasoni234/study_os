"""Roadmaps endpoints — thin: validate → service → envelope."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import User
from app.schemas.roadmap import RoadmapCreate, RoadmapPatch
from app.services import roadmap as roadmap_service
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.get("")
def list_roadmaps(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    return ok(roadmap_service.list_roadmaps(db, user))


@router.post("")
def create_roadmap(
    body: RoadmapCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(roadmap_service.create_roadmap(db, user, body))


@router.get("/{roadmap_id}")
def get_roadmap(
    roadmap_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(roadmap_service.get_roadmap(db, user, roadmap_id))


@router.patch("/{roadmap_id}")
def patch_roadmap(
    roadmap_id: str,
    body: RoadmapPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    fields = body.model_dump(exclude_unset=True)
    return ok(roadmap_service.patch_roadmap(db, user, roadmap_id, fields))


@router.get("/{roadmap_id}/progress")
def roadmap_progress(
    roadmap_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(roadmap_service.roadmap_progress(db, user, roadmap_id))
