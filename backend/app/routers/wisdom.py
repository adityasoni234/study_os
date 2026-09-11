"""Inner-growth endpoints: GET /wisdom/today, GET /wisdom, POST /wisdom/{id}/save."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.wisdom import WisdomSaveResponse
from app.services import wisdom
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["wisdom"])


@router.get("/wisdom/today")
def wisdom_today(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(wisdom.today_item(db, user))


@router.get("/wisdom")
def wisdom_list(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(wisdom.list_items(db, user))


@router.post("/wisdom/{wisdom_id}/save")
def wisdom_save(
    wisdom_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(WisdomSaveResponse(saved=wisdom.toggle_save(db, user, wisdom_id)))
