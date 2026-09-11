"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-11

MVP tradeoff (documented in docs/DATABASE.md): as the first-and-only revision, this
migration creates the schema straight from Base.metadata instead of hand-written
op.create_table calls — the models are the single source of truth. Every future
revision must use explicit op.* operations against this baseline.
"""

from typing import Sequence, Union

from alembic import op

import app.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Must exist before any VECTOR(1536) column is created.
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    # The vector extension is left installed on purpose (other schemas may use it).
    Base.metadata.drop_all(bind=op.get_bind())
