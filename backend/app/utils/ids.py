"""ID helpers. Convention (ARCHITECTURE.md): ids are string UUID4 hex, column String(32)."""

from uuid import uuid4


def new_id() -> str:
    """Return a fresh 32-char UUID4 hex string — the canonical StudyOS id."""
    return uuid4().hex
