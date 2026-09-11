"""All ORM models. `import app.models` registers every table on Base.metadata
(init_db and alembic depend on this — keep every model module imported here)."""

from app.models.assessment import (
    Flashcard,
    MindMap,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    StudyGuide,
)
from app.models.learning import (
    DailyMission,
    LearningSession,
    Mastery,
    Message,
    Recommendation,
    Subject,
    Subtopic,
    Topic,
)
from app.models.notebook import Notebook, Source, SourceChunk
from app.models.opportunity import Opportunity, PrepPlan, PrepTask, SavedOpportunity
from app.models.roadmap import Roadmap, RoadmapNode
from app.models.user import Goal, Profile, User
from app.models.wellbeing import JournalEntry, SavedWisdom, WellbeingLog, WisdomItem

__all__ = [
    "DailyMission",
    "Flashcard",
    "Goal",
    "JournalEntry",
    "LearningSession",
    "Mastery",
    "Message",
    "MindMap",
    "Notebook",
    "Opportunity",
    "PrepPlan",
    "PrepTask",
    "Profile",
    "Quiz",
    "QuizAttempt",
    "QuizQuestion",
    "Recommendation",
    "Roadmap",
    "RoadmapNode",
    "SavedOpportunity",
    "SavedWisdom",
    "Source",
    "SourceChunk",
    "StudyGuide",
    "Subject",
    "Subtopic",
    "Topic",
    "User",
    "WellbeingLog",
    "WisdomItem",
]
