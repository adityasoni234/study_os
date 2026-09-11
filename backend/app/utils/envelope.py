"""Standard response envelope. Every endpoint except POST /api/chat uses ok()."""

from typing import Any

from pydantic import BaseModel


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=True)
    if isinstance(value, dict):
        return {k: _dump(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_dump(v) for v in value]
    return value


def ok(data: Any = None, meta: dict | None = None) -> dict:
    return {"success": True, "data": _dump(data), "error": None, "meta": meta or {}}


def err_body(code: str, message: str, meta: dict | None = None) -> dict:
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message},
        "meta": meta or {},
    }
