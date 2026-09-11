"""Demo seed data: user, taxonomy, roadmaps, mastery, notebook. Idempotent (check by id
before insert); readable ids on purpose so API examples in docs/API_CONTRACT.md reproduce."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seeds.passages import PASSAGES
from app.models import (
    Mastery,
    Notebook,
    Profile,
    Roadmap,
    RoadmapNode,
    Source,
    SourceChunk,
    Subject,
    Topic,
    User,
)

DEMO_USER_ID = "demo-user"

# (id, title, icon, tone)
SUBJECTS: list[tuple[str, str, str, str]] = [
    ("machine-learning", "Machine Learning", "brain", "indigo"),
    ("python", "Python", "code", "sky"),
    ("ai-engineering", "AI Engineering", "layers", "amber"),
    ("communication", "Communication", "chat", "mint"),
]

# (id == slug, subject_id, title, summary). The last three exist so the ML roadmap's
# Foundations mastery numbers (94/88/82) resolve through Mastery, the single source of truth.
TOPICS: list[tuple[str, str | None, str, str]] = [
    ("precision-recall", "machine-learning", "Precision & Recall",
     "What your positive predictions get right (precision) vs how many real positives you catch (recall)."),
    ("confusion-matrix", "machine-learning", "Confusion Matrix",
     "The 2x2 table of TP, FP, FN, TN that every classification metric is built from."),
    ("linear-regression", "machine-learning", "Linear Regression",
     "Fitting a line to predict continuous values by minimising squared error."),
    ("logistic-regression", "machine-learning", "Logistic Regression",
     "Classification with the sigmoid: turning a linear score into a probability."),
    ("roc-curves", "machine-learning", "ROC Curves",
     "True-positive rate vs false-positive rate across thresholds; AUC summarises the curve."),
    ("decision-trees", "machine-learning", "Decision Trees",
     "Splitting data on feature thresholds to build interpretable if/else models."),
    ("perceptrons", "machine-learning", "Perceptrons",
     "The simplest neural unit: weighted sum, threshold, and a learning rule."),
    ("what-is-rag", "ai-engineering", "What is RAG",
     "Retrieval-Augmented Generation: grounding LLM answers in your own documents."),
    ("decorators", "python", "Decorators",
     "Functions that wrap other functions to add behaviour without changing them."),
    ("structured-answers", "communication", "Structured Answers",
     "Answering questions with a clear scaffold: claim, reasons, example, takeaway."),
    ("python-data", "machine-learning", "Python for Data",
     "NumPy and pandas fundamentals for loading, cleaning, and shaping data."),
    ("statistics-essentials", "machine-learning", "Statistics Essentials",
     "Distributions, sampling, and hypothesis tests that underpin ML."),
    ("linear-algebra-basics", "machine-learning", "Linear Algebra Basics",
     "Vectors, matrices, and dot products — the language of models."),
]

# (topic_id, value, trend)
MASTERY: list[tuple[str, int, str]] = [
    ("precision-recall", 65, "up"),
    ("confusion-matrix", 88, "up"),
    ("linear-regression", 92, "flat"),
    ("logistic-regression", 68, "down"),
    ("roc-curves", 12, "flat"),
    ("decorators", 74, "up"),
    ("structured-answers", 55, "flat"),
    ("perceptrons", 41, "flat"),
    ("python-data", 94, "flat"),
    ("statistics-essentials", 88, "flat"),
    ("linear-algebra-basics", 82, "flat"),
]

ROADMAPS: list[dict] = [
    {
        "id": "ml", "title": "Machine Learning", "type": "Subject", "tone": "indigo",
        "icon": "brain",
        "goal_text": "Master core ML concepts and be able to build and evaluate real models.",
        "target_date": "Nov 30", "focus": "Classification Metrics",
        "next_action": "Learn Precision & Recall", "next_topic_id": "precision-recall",
        "adapted_note": ("Your last quiz mixed up precision and recall — today starts with a "
                         "2-minute confusion matrix recap before new material."),
        "is_new": False,
    },
    {
        "id": "career", "title": "AI Engineer Career", "type": "Career", "tone": "violet",
        "icon": "rocket",
        "goal_text": "Land an AI engineering role by shipping real projects.",
        "target_date": "Mar 15", "focus": "Portfolio Projects",
        "next_action": "Build a small RAG demo", "next_topic_id": "what-is-rag",
        "adapted_note": None, "is_new": False,
    },
    {
        "id": "python", "title": "Python", "type": "Skill", "tone": "sky", "icon": "code",
        "goal_text": "Write clean, idiomatic Python beyond the basics.",
        "target_date": None, "focus": "Intermediate Python",
        "next_action": "Master decorators", "next_topic_id": "decorators",
        "adapted_note": None, "is_new": False,
    },
    {
        "id": "communication", "title": "Communication", "type": "Personal", "tone": "mint",
        "icon": "chat",
        "goal_text": "Explain ideas clearly and answer questions with structure.",
        "target_date": None, "focus": "Structured Communication",
        "next_action": "Practice structured answers", "next_topic_id": "structured-answers",
        "adapted_note": None, "is_new": False,
    },
    {
        "id": "rag", "title": "RAG Systems", "type": "Topic", "tone": "amber", "icon": "layers",
        "goal_text": "Understand and build Retrieval-Augmented Generation systems.",
        "target_date": "Sep 28", "focus": "RAG Fundamentals",
        "next_action": "Learn what RAG is", "next_topic_id": "what-is-rag",
        "adapted_note": None, "is_new": True,
    },
]

# (id, parent_id, kind, title, status, position, minutes, topic_id, summary)
# Ordered parent-first so inserts satisfy the self-referential FK on Postgres.
NodeRow = tuple[str, str | None, str, str, str, int, int | None, str | None, str | None]

NODES: dict[str, list[NodeRow]] = {
    # Mirrors the Roadmap example in docs/API_CONTRACT.md exactly.
    "ml": [
        ("ml-m1", None, "milestone", "Foundations", "done", 0, None, None, None),
        ("ml-m2", None, "milestone", "Core Machine Learning", "current", 1, None, None, None),
        ("ml-m3", None, "milestone", "Neural Networks", "locked", 2, None, None, None),
        ("ml-m4", None, "milestone", "Capstone", "locked", 3, None, None, None),
        ("python-data", "ml-m1", "topic", "Python for Data", "done", 0, 120, "python-data",
         "NumPy arrays, pandas DataFrames, and tidy data workflows."),
        ("statistics-essentials", "ml-m1", "topic", "Statistics Essentials", "done", 1, 150,
         "statistics-essentials", "Distributions, sampling, and the tests behind model claims."),
        ("linear-algebra-basics", "ml-m1", "topic", "Linear Algebra Basics", "done", 2, 135,
         "linear-algebra-basics", "Vectors, matrices, and dot products for model maths."),
        ("linear-regression", "ml-m2", "topic", "Linear Regression", "done", 0, 120,
         "linear-regression", "Least squares, residuals, and reading model coefficients."),
        ("logistic-regression", "ml-m2", "topic", "Logistic Regression", "review", 1, 110,
         "logistic-regression", "Sigmoid outputs, decision boundaries, and log loss."),
        ("classification-metrics", "ml-m2", "topic", "Classification Metrics", "current", 2, 90,
         "precision-recall", "Judging classifiers: the confusion matrix and what to optimise."),
        ("decision-trees", "ml-m2", "topic", "Decision Trees", "locked", 3, 100,
         "decision-trees", "Greedy splits, impurity, and pruning."),
        ("svm", "ml-m2", "topic", "SVM", "locked", 4, 110, None,
         "Maximum-margin classifiers and the kernel trick."),
        ("ml-sub-confusion-matrix", "classification-metrics", "subtopic", "Confusion Matrix",
         "done", 0, 20, "confusion-matrix", None),
        ("ml-sub-precision-recall", "classification-metrics", "subtopic", "Precision & Recall",
         "current", 1, 25, "precision-recall", None),
        ("ml-sub-roc-curves", "classification-metrics", "subtopic", "ROC Curves",
         "locked", 2, 20, "roc-curves", None),
        ("perceptrons", "ml-m3", "topic", "Perceptrons", "locked", 0, 90, "perceptrons",
         "From weighted sums to the first trainable classifier."),
        ("backpropagation", "ml-m3", "topic", "Backpropagation", "locked", 1, 120, None,
         "How gradients flow backwards to train multi-layer networks."),
        ("ml-capstone-project", "ml-m4", "topic", "End-to-End ML Project", "locked", 0, 240, None,
         "Frame, train, evaluate, and present a full ML project."),
    ],
    # ~42% done (3 of 7 topics) for the career roadmap.
    "career": [
        ("career-m1", None, "milestone", "ML Foundations", "done", 0, None, None, None),
        ("career-m2", None, "milestone", "Portfolio Projects", "current", 1, None, None, None),
        ("career-m3", None, "milestone", "Job Preparation", "locked", 2, None, None, None),
        ("career-python", "career-m1", "topic", "Python & Data Stack", "done", 0, 120, None, None),
        ("career-math", "career-m1", "topic", "Math for ML", "done", 1, 150, None, None),
        ("career-ml-basics", "career-m1", "topic", "Core ML Concepts", "done", 2, 180, None, None),
        ("career-rag-demo", "career-m2", "topic", "Build a RAG Demo", "current", 0, 240,
         "what-is-rag", None),
        ("career-e2e-app", "career-m2", "topic", "End-to-End ML App", "locked", 1, 300, None, None),
        ("career-interviews", "career-m3", "topic", "ML Interview Prep", "locked", 0, 180, None, None),
        ("career-portfolio", "career-m3", "topic", "Portfolio & Resume", "locked", 1, 120, None, None),
    ],
    "python": [
        ("py-m1", None, "milestone", "Core Python", "done", 0, None, None, None),
        ("py-m2", None, "milestone", "Intermediate Python", "current", 1, None, None, None),
        ("py-m3", None, "milestone", "Advanced Python", "locked", 2, None, None, None),
        ("py-functions", "py-m1", "topic", "Functions & Scope", "done", 0, 60, None, None),
        ("py-oop", "py-m1", "topic", "Classes & OOP", "done", 1, 90, None, None),
        ("py-decorators", "py-m2", "topic", "Decorators", "current", 0, 60, "decorators", None),
        ("py-generators", "py-m2", "topic", "Generators & Iterators", "locked", 1, 60, None, None),
        ("py-async", "py-m3", "topic", "Async & Concurrency", "locked", 0, 120, None, None),
        ("py-typing", "py-m3", "topic", "Typing & Protocols", "locked", 1, 90, None, None),
    ],
    "communication": [
        ("comm-m1", None, "milestone", "Foundations", "done", 0, None, None, None),
        ("comm-m2", None, "milestone", "Structured Communication", "current", 1, None, None, None),
        ("comm-m3", None, "milestone", "High-Stakes Settings", "locked", 2, None, None, None),
        ("comm-clarity", "comm-m1", "topic", "Clarity & Brevity", "done", 0, 45, None, None),
        ("comm-structured", "comm-m2", "topic", "Structured Answers", "current", 0, 45,
         "structured-answers", None),
        ("comm-stories", "comm-m2", "topic", "Storytelling", "locked", 1, 60, None, None),
        ("comm-presentations", "comm-m3", "topic", "Presentations", "locked", 0, 90, None, None),
        ("comm-interviews", "comm-m3", "topic", "Interview Communication", "locked", 1, 60, None, None),
    ],
    "rag": [
        ("rag-m1", None, "milestone", "RAG Fundamentals", "current", 0, None, None, None),
        ("rag-what", "rag-m1", "topic", "What is RAG", "current", 0, 45, "what-is-rag",
         "Why retrieval fixes hallucination: fetch, ground, cite."),
        ("rag-embeddings", "rag-m1", "topic", "Embeddings Intuition", "locked", 1, 60, None,
         "Meaning as geometry: similar text lands close together."),
        ("rag-vector-chunking", "rag-m1", "topic", "Vector Search & Chunking", "locked", 2, 60,
         None, "Splitting documents and finding nearest neighbours."),
        ("rag-grounding-app", "rag-m1", "topic", "Grounding & Mini RAG App", "locked", 3, 90,
         None, "Cited answers end-to-end in a tiny app."),
    ],
}

# (id, title, kind, meta, url)
SOURCES: list[tuple[str, str, str, str, str | None]] = [
    ("src-ml-notes", "ML Course Notes — Unit 3: Model Evaluation", "pdf", "PDF · 42 pages", None),
    ("src-statquest", "StatQuest — Precision & Recall, Clearly Explained", "youtube",
     "YouTube · 9 min", None),
    ("src-sklearn", "scikit-learn — Metrics & Scoring Guide", "web", "Web · scikit-learn.org",
     "https://scikit-learn.org/stable/modules/model_evaluation.html"),
    ("src-week6", "My lecture notes — Week 6", "notes", "Notes · Week 6", None),
]

# (chunk id == PASSAGES key, source_id, position, page). Embeddings stay NULL — retrieval backfills.
CHUNKS: list[tuple[str, str, int, int | None]] = [
    ("unit3-p14", "src-ml-notes", 0, 14),
    ("unit3-p15", "src-ml-notes", 1, 15),
    ("unit3-p18", "src-ml-notes", 2, 18),
    ("unit3-p22", "src-ml-notes", 3, 22),
    ("unit3-p31", "src-ml-notes", 4, 31),
    ("statquest", "src-statquest", 0, None),
]

NOTEBOOK_ID = "default-notebook"


def _add_if_missing(session: Session, model: type, obj_id: str, **fields) -> None:
    if session.get(model, obj_id) is None:
        session.add(model(id=obj_id, **fields))


def seed(session: Session) -> None:
    if session.get(User, DEMO_USER_ID) is None:
        session.add(User(id=DEMO_USER_ID, name="Aditya", email="adityaksoni234@gmail.com"))
    if session.get(Profile, DEMO_USER_ID) is None:
        session.add(Profile(user_id=DEMO_USER_ID, level="Intermediate", daily_goal_minutes=25,
                            explanation_style="visual", streak_days=12, preferences={}))

    for subject_id, title, icon, tone in SUBJECTS:
        _add_if_missing(session, Subject, subject_id, title=title, icon=icon, tone=tone)
    for topic_id, subject_id, title, summary in TOPICS:
        _add_if_missing(session, Topic, topic_id, subject_id=subject_id, slug=topic_id,
                        title=title, summary=summary)

    for spec in ROADMAPS:
        _add_if_missing(session, Roadmap, spec["id"], user_id=DEMO_USER_ID,
                        **{k: v for k, v in spec.items() if k != "id"})
        for node_id, parent_id, kind, title, status, position, minutes, topic_id, summary in NODES[spec["id"]]:
            _add_if_missing(session, RoadmapNode, node_id, roadmap_id=spec["id"],
                            parent_id=parent_id, kind=kind, title=title, status=status,
                            position=position, minutes=minutes, topic_id=topic_id,
                            summary=summary, depends_on=[])

    for topic_id, value, trend in MASTERY:
        exists = session.execute(
            select(Mastery.id).where(Mastery.user_id == DEMO_USER_ID,
                                     Mastery.topic_id == topic_id)
        ).scalar_one_or_none()
        if exists is None:
            session.add(Mastery(user_id=DEMO_USER_ID, topic_id=topic_id, value=value, trend=trend))

    _add_if_missing(session, Notebook, NOTEBOOK_ID, user_id=DEMO_USER_ID, title="My Notebook")
    for source_id, title, kind, meta, url in SOURCES:
        _add_if_missing(session, Source, source_id, notebook_id=NOTEBOOK_ID, title=title,
                        kind=kind, status="ready", meta=meta, url=url)
    for chunk_id, source_id, position, page in CHUNKS:
        _add_if_missing(session, SourceChunk, chunk_id, source_id=source_id,
                        notebook_id=NOTEBOOK_ID, position=position, page=page,
                        text=PASSAGES[chunk_id], embedding=None)

    session.flush()
