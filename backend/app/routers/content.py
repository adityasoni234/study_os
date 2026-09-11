"""Content endpoints: study guide, mind map, studycast."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import User
from app.schemas.content import ContentSourceRequest, StudycastGenerateRequest
from app.services import content as content_service
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["content"])


@router.post("/study-guide/generate")
def generate_study_guide(
    body: ContentSourceRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(content_service.generate_study_guide(db, user, body))


@router.post("/mindmap/generate")
def generate_mindmap(
    body: ContentSourceRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(content_service.generate_mindmap(db, user, body))


@router.post("/studycast/generate")
def generate_studycast(
    body: StudycastGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(content_service.generate_studycast(db, user, body))
