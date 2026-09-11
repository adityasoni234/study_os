"""Notebook endpoints (docs/API_CONTRACT.md — Notebook section). Thin layer:
validate → app.services.notebook → envelope. All responses camelCase-enveloped."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.notebook import AskRequest, NotebookCreate, SourceCreate, SourceOut
from app.services import notebook as service
from app.utils.deps import get_current_user
from app.utils.envelope import ok
from app.utils.errors import AppError

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.post("")
def create_notebook(
    payload: NotebookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(service.create_notebook(db, user, payload.title))


@router.get("")
def list_notebooks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok({"notebooks": service.list_notebooks(db, user)})


@router.post("/{notebook_id}/sources")
async def add_source(
    notebook_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Accepts EITHER a multipart file upload (field ``file``, optional
    ``title``) OR a JSON body {kind, title, text?, url?}. PDF and text are
    ingested synchronously and return status 'ready'."""
    notebook = service.get_notebook(db, user, notebook_id)
    content_type = (request.headers.get("content-type") or "").lower()

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        if upload is None or isinstance(upload, str):
            raise AppError("VALIDATION_ERROR", "Attach the upload as a 'file' field.", 422)
        data = await upload.read()
        title_field = form.get("title")
        source = service.add_source_from_file(
            db,
            notebook,
            filename=upload.filename or "",
            content_type=upload.content_type or "",
            data=data,
            title=title_field if isinstance(title_field, str) else None,
        )
    else:
        try:
            body = await request.json()
        except Exception:
            raise AppError(
                "VALIDATION_ERROR", "Send a multipart file upload or a JSON body.", 422
            ) from None
        try:
            payload = SourceCreate.model_validate(body)
        except ValidationError:
            raise AppError(
                "VALIDATION_ERROR", "Invalid source. Check: kind, title, text, url.", 422
            ) from None
        source = service.add_source_from_json(db, notebook, payload)

    return ok(SourceOut.model_validate(source))


@router.get("/{notebook_id}/sources")
def list_sources(
    notebook_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    notebook = service.get_notebook(db, user, notebook_id)
    sources = [SourceOut.model_validate(s) for s in service.list_sources(db, notebook)]
    return ok({"sources": sources})


@router.post("/{notebook_id}/ask")
def ask(
    notebook_id: str,
    payload: AskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return ok(service.ask(db, user, notebook_id, payload.question))
