"""Response schemas for the learning endpoints (mastery, recommendations, mission).

Services build these; routers wrap them in the standard envelope. CamelModel
serialises snake_case fields as camelCase JSON.
"""

from datetime import datetime

from app.schemas.common import CamelModel


class MasteryTopicOut(CamelModel):
    topic_id: str
    title: str
    mastery: int
    trend: str  # up|flat|down
    updated_at: datetime


class RecommendationOut(CamelModel):
    id: str
    kind: str  # review|learn|practice|opportunity
    title: str
    reason: str
    topic_id: str | None = None
    route: str


class MissionStepOut(CamelModel):
    id: str
    label: str
    done: bool = False


class MissionOut(CamelModel):
    topic_id: str
    title: str
    context: str
    minutes: int
    steps: list[MissionStepOut]
    adapted_note: str
