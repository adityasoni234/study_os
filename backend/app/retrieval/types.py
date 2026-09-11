"""Shared retrieval types. Spine file — tutor & notebook services depend on these."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChunkHit:
    chunk_id: str
    source_id: str
    source_title: str
    text: str
    page: int | None
    score: float


@dataclass
class Citation:
    source_id: str
    title: str
    page: int | None
    snippet: str
    url: str | None = None

    def to_dict(self) -> dict:
        return {
            "sourceId": self.source_id,
            "title": self.title,
            "page": self.page,
            "snippet": self.snippet,
            "url": self.url,
        }


class EmbeddingProvider(Protocol):
    name: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...
