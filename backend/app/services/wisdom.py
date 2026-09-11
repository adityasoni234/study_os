"""Inner-growth wisdom: seed-backed verses, daily rotation, per-user saves.

Verses come from app/db/seeds/wisdom.py — authentic classical texts only,
never generated and never altered. AI never writes or rewrites verse content;
the stored aiReflection is authored, labeled reflection copy.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wellbeing import SavedWisdom, WisdomItem
from app.schemas.wisdom import WisdomItemOut, WisdomListResponse
from app.utils.errors import NotFound


def list_items(db: Session, user: User) -> WisdomListResponse:
    items = _all_items(db)
    saved_ids = _saved_ids(db, user.id)
    return WisdomListResponse(items=[_to_out(i, i.id in saved_ids) for i in items])


def today_item(db: Session, user: User) -> WisdomItemOut:
    items = _all_items(db)
    if not items:
        raise NotFound("Wisdom item")
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    item = items[day_of_year % len(items)]
    saved = db.get(SavedWisdom, (user.id, item.id)) is not None
    return _to_out(item, saved)


def toggle_save(db: Session, user: User, wisdom_id: str) -> bool:
    if db.get(WisdomItem, wisdom_id) is None:
        raise NotFound("Wisdom item")
    existing = db.get(SavedWisdom, (user.id, wisdom_id))
    if existing is not None:
        db.delete(existing)
        db.flush()
        return False
    db.add(SavedWisdom(user_id=user.id, wisdom_id=wisdom_id))
    db.flush()
    return True


def _all_items(db: Session) -> list[WisdomItem]:
    # Stable ordering so the daily rotation index is deterministic.
    return list(db.execute(select(WisdomItem).order_by(WisdomItem.id)).scalars())


def _saved_ids(db: Session, user_id: str) -> set[str]:
    return set(
        db.execute(select(SavedWisdom.wisdom_id).where(SavedWisdom.user_id == user_id)).scalars()
    )


def _to_out(item: WisdomItem, saved: bool) -> WisdomItemOut:
    return WisdomItemOut(
        id=item.id,
        original=item.original,
        transliteration=item.transliteration,
        translation=item.translation,
        source=item.source_ref,
        source_note=item.source_note,
        ai_reflection=item.ai_reflection,
        question=item.question,
        verified=item.verified,
        saved=saved,
    )
