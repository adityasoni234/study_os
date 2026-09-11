"""Response schemas for the Growth + Knowledge-map endpoints (both are GETs,
so there are no request bodies). Services build these models and the envelope
serialises them by alias (camelCase)."""

from app.schemas.common import CamelModel


class GrowthDimension(CamelModel):
    id: str
    label: str
    value: int
    delta: int
    tone: str


class WeekDay(CamelModel):
    day: str
    minutes: int


class GrowthInsight(CamelModel):
    kind: str  # strongest|improving|attention
    title: str
    detail: str
    route: str


class NextStep(CamelModel):
    title: str
    reason: str
    route: str


class KnowledgeTopic(CamelModel):
    topic_id: str
    title: str
    mastery: int
    route: str


class KnowledgeArea(CamelModel):
    id: str
    title: str
    icon: str
    tone: str
    topics: list[KnowledgeTopic]
