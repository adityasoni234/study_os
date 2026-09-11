"""POST /api/chat — the competition endpoint.

The ONE endpoint that skips the envelope: it returns the flat shape
``{"response": "..."}``. Internally it is the same tutor pipeline, pinned to a
per-user rolling session ("chat-<user id>") so the conversation has memory.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.chat import ChatIn
from app.schemas.tutor import TutorMessageIn
from app.services import tutor
from app.utils.deps import get_current_user

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(
    body: ChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    result = tutor.handle_message(
        db,
        user,
        TutorMessageIn(message=body.message),
        fixed_session_id=f"chat-{user.id}",
    )
    return {"response": result["reply"]["text"]}
