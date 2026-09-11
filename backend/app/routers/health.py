"""GET /api/health — liveness, DB reachability, resolved AI mode."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.base import get_db
from app.utils.envelope import ok

VERSION = "1.0.0"

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
        try:
            db.rollback()
        except Exception:
            pass
    return ok(
        {
            "status": "ok",
            "db": db_ok,
            "aiMode": settings.resolved_ai_mode,
            "version": VERSION,
        }
    )
