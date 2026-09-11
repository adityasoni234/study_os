"""Deterministic mock payloads for the MockProvider.

Zero-network, always-valid content so every feature works offline (AI_MODE=mock)
and in tests. JSON payloads match the shapes in docs/API_CONTRACT.md; text
replies read like a warm tutor. Keyword detection inspects the prompt text
(system + messages) that app/ai/prompts.py produces, so each prompt template
carries its own trigger word ("quiz", "roadmap", "flashcard", ...).
"""

from __future__ import annotations

import copy
import re

from app.ai.base import AIMessage

_COUNT_RE = re.compile(r"exactly (\d+)")


def tutor_reply(messages: list[AIMessage]) -> str:
    """A 2-3 sentence tutor-style answer referencing the last user message."""
    last = ""
    for message in reversed(messages):
        if message.get("role") == "user" and str(message.get("content", "")).strip():
            last = str(message["content"]).strip()
            break
    snippet = " ".join(last.split())
    if len(snippet) > 120:
        snippet = snippet[:117].rstrip() + "..."
    if not snippet:
        snippet = "this topic"
    return (
        f'Good question — let\'s look at "{snippet}" together. '
        "The trick is to start from what the words literally mean, pin that down "
        "with one concrete example, and only then layer the formal details on top. "
        "Quick check before we go further: how would you sum up the main idea in "
        "one sentence to a friend?"
    )


def json_payload(system: str | None, messages: list[AIMessage]) -> dict:
    """Pick a realistic JSON payload by inspecting the prompt text for hints."""
    blob = " ".join(
        part
        for part in [system or "", *(str(m.get("content", "")) for m in messages)]
        if part
    ).lower()
    if "intent" in blob or "classify" in blob:
        return {"mode": "teach"}
    if "evaluate" in blob:
        return _evaluation()
    if "misconception" in blob:
        return _misconception()
    if "studycast" in blob or "dialogue" in blob or "podcast" in blob:
        return _studycast()
    if "study guide" in blob or "sections" in blob:
        return _study_guide()
    if "flashcard" in blob:
        return _flashcards(_requested_count(blob, default=6, lo=1, hi=12))
    if "mind map" in blob or "mindmap" in blob or "mind" in blob:
        return _mindmap()
    if "roadmap" in blob or "milestone" in blob:
        return _roadmap()
    if "quiz" in blob or "questions" in blob:
        return _quiz(_requested_count(blob, default=5, lo=1, hi=10))
    return {"result": "ok"}


def _requested_count(blob: str, *, default: int, lo: int, hi: int) -> int:
    match = _COUNT_RE.search(blob)
    if not match:
        return default
    return max(lo, min(hi, int(match.group(1))))


def _cycle(base: list[dict], n: int) -> list[dict]:
    """Return n items cycled from base, keeping repeated prompts/fronts unique."""
    out: list[dict] = []
    size = len(base)
    for i in range(n):
        item = copy.deepcopy(base[i % size])
        if i >= size:
            for key in ("prompt", "front"):
                if key in item:
                    item[key] = f"{item[key]} (variant {i // size + 1})"
        out.append(item)
    return out


_QUIZ_QUESTIONS: list[dict] = [
    {
        "prompt": "Which formula defines precision for a binary classifier?",
        "options": [
            "TP / (TP + FP)",
            "TP / (TP + FN)",
            "TN / (TN + FP)",
            "(TP + TN) / all predictions",
        ],
        "correctIndex": 0,
        "explanation": (
            "Precision asks: of everything the model flagged positive, how much "
            "really was positive? That is TP / (TP + FP)."
        ),
        "tag": "Definitions",
    },
    {
        "prompt": "Which formula defines recall (also called sensitivity)?",
        "options": [
            "TP / (TP + FP)",
            "TP / (TP + FN)",
            "FP / (FP + TN)",
            "TN / (TN + FN)",
        ],
        "correctIndex": 1,
        "explanation": (
            "Recall asks: of all the real positives out there, how many did the "
            "model find? That is TP / (TP + FN)."
        ),
        "tag": "Definitions",
    },
    {
        "prompt": (
            "A spam filter flags very few emails, but almost every flagged email "
            "really is spam. What does this behaviour suggest?"
        ),
        "options": [
            "High precision, possibly low recall",
            "High recall, possibly low precision",
            "High recall and high precision",
            "Low precision and low recall",
        ],
        "correctIndex": 0,
        "explanation": (
            "Few false positives means high precision, but being so cautious it "
            "likely misses real spam — so recall may be low."
        ),
        "tag": "Concepts",
    },
    {
        "prompt": (
            "In screening for a serious disease, which metric is usually "
            "prioritised so that few true cases slip through?"
        ),
        "options": ["Precision", "Recall", "Specificity alone", "Training accuracy"],
        "correctIndex": 1,
        "explanation": (
            "A missed real case (false negative) is the costly mistake here, so "
            "screening favours high recall and confirms positives later."
        ),
        "tag": "Applications",
    },
    {
        "prompt": "The F1 score combines precision and recall using which operation?",
        "options": ["Arithmetic mean", "Geometric mean", "Harmonic mean", "Weighted median"],
        "correctIndex": 2,
        "explanation": (
            "F1 = 2PR / (P + R), the harmonic mean — it stays low unless both "
            "precision and recall are reasonably high."
        ),
        "tag": "Concepts",
    },
]


def _quiz(n: int = 5) -> dict:
    return {"questions": _cycle(_QUIZ_QUESTIONS, n)}


def _roadmap() -> dict:
    return {
        "title": "Machine Learning Foundations",
        "type": "Subject",
        "focus": "Classification Metrics",
        "milestones": [
            {
                "title": "Foundations",
                "topics": [
                    {
                        "title": "Python for Data",
                        "minutes": 120,
                        "summary": (
                            "NumPy arrays, pandas DataFrames and quick plots — the "
                            "toolkit every later step builds on."
                        ),
                        "subtopics": ["NumPy basics", "pandas DataFrames", "Plotting results"],
                    },
                    {
                        "title": "Data Preparation",
                        "minutes": 90,
                        "summary": (
                            "Cleaning, splitting and scaling data so models train on "
                            "honest inputs instead of leaks and noise."
                        ),
                        "subtopics": ["Train/test split", "Feature scaling", "Missing values"],
                    },
                ],
            },
            {
                "title": "Core Models",
                "topics": [
                    {
                        "title": "Linear & Logistic Regression",
                        "minutes": 150,
                        "summary": (
                            "Fit a line, then a decision boundary — the two workhorse "
                            "models and how gradient descent tunes them."
                        ),
                        "subtopics": ["Loss functions", "Gradient descent", "Decision boundaries"],
                    },
                    {
                        "title": "Classification Metrics",
                        "minutes": 100,
                        "summary": (
                            "Accuracy can lie on imbalanced data — read a confusion "
                            "matrix and choose precision, recall or F1 deliberately."
                        ),
                        "subtopics": ["Confusion matrix", "Precision & recall", "F1 score"],
                    },
                ],
            },
            {
                "title": "Applied Practice",
                "topics": [
                    {
                        "title": "End-to-End Evaluation Project",
                        "minutes": 180,
                        "summary": (
                            "Train, evaluate and iterate on a small classifier, "
                            "reporting results with the right metrics."
                        ),
                        "subtopics": ["Cross-validation", "Error analysis", "Reporting results"],
                    },
                ],
            },
        ],
    }


def _flashcards(n: int = 6) -> dict:
    base = [
        {
            "front": "What does precision measure?",
            "back": (
                "Of everything the model predicted positive, the fraction that was "
                "actually positive: TP / (TP + FP)."
            ),
        },
        {
            "front": "What does recall measure?",
            "back": (
                "Of all actual positives, the fraction the model found: "
                "TP / (TP + FN). Also called sensitivity."
            ),
        },
        {
            "front": "What is the F1 score?",
            "back": (
                "The harmonic mean of precision and recall: 2PR / (P + R). It is "
                "only high when both are high."
            ),
        },
        {
            "front": "What is a confusion matrix?",
            "back": (
                "A 2x2 table of prediction outcomes: true positives, false "
                "positives, false negatives and true negatives."
            ),
        },
        {
            "front": "False positive vs false negative?",
            "back": (
                "False positive: flagged positive but actually negative. False "
                "negative: a real positive the model missed."
            ),
        },
        {
            "front": "Why can accuracy mislead on imbalanced data?",
            "back": (
                "Predicting the majority class for everything scores high accuracy "
                "while catching zero minority cases — check precision and recall."
            ),
        },
    ]
    return {"cards": _cycle(base, n)}


def _mindmap() -> dict:
    return {
        "center": "Machine Learning",
        "nodes": [
            {"id": "n1", "label": "Supervised Learning", "parentId": None},
            {"id": "n2", "label": "Unsupervised Learning", "parentId": None},
            {"id": "n3", "label": "Model Evaluation", "parentId": None},
            {"id": "n4", "label": "Regression", "parentId": "n1"},
            {"id": "n5", "label": "Classification", "parentId": "n1"},
            {"id": "n6", "label": "Clustering", "parentId": "n2"},
            {"id": "n7", "label": "Precision & Recall", "parentId": "n3"},
            {"id": "n8", "label": "Confusion Matrix", "parentId": "n3"},
        ],
    }


def _study_guide() -> dict:
    return {
        "title": "Precision & Recall — Study Guide",
        "sections": [
            {
                "id": "overview",
                "title": "The Big Picture",
                "kind": "overview",
                "markdown": (
                    "Accuracy alone can hide serious failures, especially on "
                    "imbalanced data. **Precision** and **recall** split model "
                    "quality into two honest halves: how *trustworthy* the "
                    "positive predictions are, and how *complete* they are."
                ),
            },
            {
                "id": "key-definitions",
                "title": "Key Definitions",
                "kind": "definitions",
                "markdown": (
                    "- **True positive (TP)** — predicted positive, actually positive.\n"
                    "- **False positive (FP)** — predicted positive, actually negative.\n"
                    "- **False negative (FN)** — predicted negative, actually positive.\n"
                    "- **Precision** — the share of flagged items that were right.\n"
                    "- **Recall** — the share of real positives that were found."
                ),
            },
            {
                "id": "formulas",
                "title": "Formulas",
                "kind": "formulas",
                "markdown": (
                    "- Precision = TP / (TP + FP)\n"
                    "- Recall = TP / (TP + FN)\n"
                    "- F1 = 2 · P · R / (P + R) — the harmonic mean, low unless "
                    "both are high."
                ),
            },
            {
                "id": "worked-examples",
                "title": "Worked Example",
                "kind": "examples",
                "markdown": (
                    "A model flags 10 emails as spam; 8 really are spam, and 4 "
                    "spam emails were missed.\n\n"
                    "- Precision = 8 / 10 = **0.8**\n"
                    "- Recall = 8 / 12 = **0.67**\n\n"
                    "Strict filters raise precision but drop recall; lenient ones "
                    "do the reverse — that is the trade-off."
                ),
            },
            {
                "id": "common-mistakes",
                "title": "Common Mistakes",
                "kind": "mistakes",
                "markdown": (
                    "- Swapping the denominators: precision divides by *predicted* "
                    "positives, recall by *actual* positives.\n"
                    "- Trusting accuracy on imbalanced data.\n"
                    "- Reporting only one of the two — always ask what the costly "
                    "error type is."
                ),
            },
            {
                "id": "practice-set",
                "title": "Practice",
                "kind": "practice",
                "markdown": (
                    "1. A screening test finds 45 of 50 real cases and raises 30 "
                    "false alarms. Compute precision and recall.\n"
                    "2. Name one application where recall matters more than "
                    "precision, and one where the reverse holds — justify both."
                ),
            },
        ],
    }


def _studycast() -> dict:
    return {
        "title": "Precision vs Recall, Plainly",
        "lines": [
            {"speaker": "A", "text": "Okay, honest confession: precision and recall still blur together for me. Why do we even need two numbers?"},
            {"speaker": "B", "text": "Because one number hides the story. Imagine a spam filter — there are two totally different ways it can be wrong."},
            {"speaker": "A", "text": "Flagging a real email as spam, or letting actual spam sneak into my inbox, right?"},
            {"speaker": "B", "text": "Exactly. Precision asks: of everything it flagged, how much was truly spam? Recall asks: of all the spam out there, how much did it catch?"},
            {"speaker": "A", "text": "So a super cautious filter that only flags obvious spam would have high precision but terrible recall?"},
            {"speaker": "B", "text": "You've got it. And a paranoid filter that flags half your inbox gets great recall but awful precision. Tightening one usually loosens the other."},
            {"speaker": "A", "text": "Then how do I compare two models without juggling both numbers in my head?"},
            {"speaker": "B", "text": "Use F1, the harmonic mean of the two. Quick recap: precision is trust in the flags, recall is coverage of the real cases, and F1 only looks good when both do."},
        ],
    }


def _evaluation() -> dict:
    return {
        "correct": False,
        "misconception": (
            "Mixing up precision (how trustworthy the positive predictions are) "
            "with recall (how many real positives were found)."
        ),
        "feedback": (
            "You're close — what you described is recall: the share of real "
            "positives the model managed to catch. Precision flips the question "
            "and asks how many of the *flagged* items were actually right. Look "
            "at which total sits in the denominator: predicted positives means "
            "precision, actual positives means recall."
        ),
    }


def _misconception() -> dict:
    return {
        "misconception": (
            "Believing that a high overall accuracy means the model performs "
            "well on the rare class it was built to catch."
        ),
        "clarification": (
            "On imbalanced data, a model can score 99% accuracy by always "
            "predicting the majority class — while finding none of the rare "
            "cases that matter. That is why precision and recall are checked "
            "separately: they focus only on how the positive class is handled. "
            "For example, a fraud model that never flags anything is 'accurate' "
            "yet useless."
        ),
        "checkQuestion": (
            "A model predicts 'no fraud' for all 1,000 transactions, and 10 were "
            "fraud. What is its accuracy, and what is its recall on fraud?"
        ),
    }
