"""Growth dashboard + knowledge map endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import User
from app.services import growth as growth_service
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["growth"])


@router.get("/growth")
def get_growth(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    return ok(growth_service.get_growth(db, user))


@router.get("/knowledge-map")
def get_knowledge_map(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    return ok(growth_service.get_knowledge_map(db, user))
