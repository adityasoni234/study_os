"""Portable embedding column: pgvector Vector(1536) on Postgres, JSON-in-Text on SQLite."""

import json
from typing import Any

from sqlalchemy import Text
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

EMBEDDING_DIM = 1536


class EmbeddingVector(TypeDecorator):
    """Stores ``list[float] | None``. The only dialect-aware type in the schema."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            # Imported lazily so SQLite-only environments never need pgvector.
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(EMBEDDING_DIM))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: list[float] | None, dialect: Dialect) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value  # pgvector's own bind processor handles list[float]
        return json.dumps([float(x) for x in value])

    def process_result_value(self, value: Any, dialect: Dialect) -> list[float] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return [float(x) for x in value]  # normalise numpy array -> list
        return [float(x) for x in json.loads(value)]
