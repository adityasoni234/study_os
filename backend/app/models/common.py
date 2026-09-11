"""Shared column helpers for model modules (this module defines no tables)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import MappedColumn, mapped_column


def new_id() -> str:
    return uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def pk_column() -> MappedColumn[str]:
    return mapped_column(String(32), primary_key=True, default=new_id)


def created_at_column() -> MappedColumn[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
