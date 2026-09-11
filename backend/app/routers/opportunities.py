"""Opportunities API: tabs + match, detail, save toggle, prepare plans.

Thin per ARCHITECTURE.md: validate → service → ok() envelope. Auto-mounted
under /api by app.routers discovery.
"""

from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.services import opportunity as opportunity_service
from app.services import prepare as prepare_service
from app.utils.deps import get_current_user
from app.utils.envelope import ok

router = APIRouter(tags=["opportunities"])

Tab = Literal["best", "closing", "new", "saved"]


@router.get("/opportunities")
def list_opportunities(
    tab: Tab = "best",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(opportunity_service.list_opportunities(db, user, tab))


@router.get("/opportunities/{opportunity_id}")
def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(opportunity_service.get_opportunity(db, user, opportunity_id))


@router.post("/opportunities/{opportunity_id}/save")
def toggle_save(
    opportunity_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(opportunity_service.toggle_save(db, user, opportunity_id))


@router.post("/opportunities/{opportunity_id}/prepare")
def prepare(
    opportunity_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(prepare_service.prepare_plan(db, user, opportunity_id))


@router.post("/prepare/tasks/{task_id}/toggle")
def toggle_prepare_task(
    task_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(prepare_service.toggle_task(db, user, task_id))
