"""Opportunity listing, detail and save-toggle. Matching is computed per request
from Mastery rows (see app.opportunities.matching) so scores track learning."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, SavedOpportunity
from app.models.user import User
from app.opportunities.matching import match_for_user
from app.schemas.opportunity import (
    MatchOut,
    OpportunityListOut,
    OpportunityOut,
    SaveOut,
)
from app.utils.errors import NotFound

NEW_TAB_COUNT = 3


def _to_out(opp: Opportunity, match: dict, saved: bool) -> OpportunityOut:
    return OpportunityOut(
        id=opp.id,
        title=opp.title,
        org=opp.org,
        type=opp.type,
        tone=opp.tone,
        deadline=opp.deadline_text,
        days_left=opp.days_left,
        mode=opp.mode,
        blurb=opp.description,
        eligibility=opp.eligibility,
        source=opp.source,
        source_url=opp.source_url,
        verified=opp.verified,
        match=MatchOut(**match),
        saved=saved,
    )


def _saved_order(db: Session, user: User) -> dict[str, int]:
    """opportunity_id -> save recency rank (0 = most recent)."""
    rows = db.execute(
        select(SavedOpportunity.opportunity_id)
        .where(SavedOpportunity.user_id == user.id)
        .order_by(SavedOpportunity.created_at.desc(), SavedOpportunity.id)
    ).scalars().all()
    return {opp_id: rank for rank, opp_id in enumerate(rows)}


def list_opportunities(db: Session, user: User, tab: str = "best") -> OpportunityListOut:
    opportunities = db.execute(select(Opportunity)).scalars().all()
    saved_rank = _saved_order(db, user)

    items = [
        (opp, match_for_user(db, user, opp), opp.id in saved_rank) for opp in opportunities
    ]

    if tab == "saved":
        items = [entry for entry in items if entry[2]]
        items.sort(key=lambda entry: saved_rank[entry[0].id])
    elif tab == "closing":
        items.sort(
            key=lambda entry: (
                entry[0].days_left is None,  # nulls last
                entry[0].days_left if entry[0].days_left is not None else 0,
                -entry[1]["score"],
                entry[0].id,
            )
        )
    elif tab == "new":
        items.sort(key=lambda entry: (entry[0].created_at, entry[0].id), reverse=True)
        items = items[:NEW_TAB_COUNT]
    else:  # best
        items.sort(key=lambda entry: (-entry[1]["score"], entry[0].id))

    return OpportunityListOut(
        opportunities=[_to_out(opp, match, saved) for opp, match, saved in items]
    )


def get_opportunity(db: Session, user: User, opportunity_id: str) -> OpportunityOut:
    opp = db.get(Opportunity, opportunity_id)
    if opp is None:
        raise NotFound("Opportunity")
    match = match_for_user(db, user, opp)
    saved = _is_saved(db, user, opportunity_id)
    return _to_out(opp, match, saved)


def toggle_save(db: Session, user: User, opportunity_id: str) -> SaveOut:
    if db.get(Opportunity, opportunity_id) is None:
        raise NotFound("Opportunity")
    existing = db.execute(
        select(SavedOpportunity).where(
            SavedOpportunity.user_id == user.id,
            SavedOpportunity.opportunity_id == opportunity_id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        db.delete(existing)
        db.flush()
        return SaveOut(saved=False)
    db.add(SavedOpportunity(user_id=user.id, opportunity_id=opportunity_id))
    db.flush()
    return SaveOut(saved=True)


def _is_saved(db: Session, user: User, opportunity_id: str) -> bool:
    return (
        db.execute(
            select(SavedOpportunity.id).where(
                SavedOpportunity.user_id == user.id,
                SavedOpportunity.opportunity_id == opportunity_id,
            )
        ).scalar_one_or_none()
        is not None
    )
