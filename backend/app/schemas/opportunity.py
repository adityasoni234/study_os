"""Response schemas for opportunities and preparation plans (camelCase JSON)."""

from app.schemas.common import CamelModel


class MatchOut(CamelModel):
    score: int
    reasons: list[str]
    gaps: list[str]


class OpportunityOut(CamelModel):
    id: str
    title: str
    org: str
    type: str
    tone: str
    deadline: str
    days_left: int | None = None
    mode: str
    blurb: str
    eligibility: str
    source: str
    source_url: str
    verified: bool
    match: MatchOut
    saved: bool


class OpportunityListOut(CamelModel):
    opportunities: list[OpportunityOut]


class SaveOut(CamelModel):
    saved: bool


class PrepTaskOut(CamelModel):
    id: str
    label: str
    done: bool


class PrepDayOut(CamelModel):
    day: int
    title: str
    minutes: int
    tasks: list[PrepTaskOut]
    tutor_topic_id: str | None = None
    note: str | None = None


class PrepPlanOut(CamelModel):
    opportunity_id: str
    days_remaining: int
    readiness: int
    gap_note: str
    days: list[PrepDayOut]


class PrepToggleOut(CamelModel):
    done: bool
    readiness: int
