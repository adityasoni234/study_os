"""Request schema for POST /api/chat (competition endpoint, flat response)."""

from pydantic import Field

from app.schemas.common import CamelModel


class ChatIn(CamelModel):
    message: str = Field(min_length=1, max_length=8000)
