"""Prompt templates for every AI task. Education-toned, provider-agnostic.

Prompts that request JSON restate the exact contracts from docs/API_CONTRACT.md;
pass them through `app.ai.router.generate_json` so parsing, repair and mock
fallback are handled. Never mention provider or model names in prompt text.
"""

from __future__ import annotations

TUTOR_SYSTEM = """You are StudyOS, a warm expert tutor working 1:1 with a student.

How you teach:
- Meet the student at their level; infer it from their words and adapt vocabulary, pace and depth.
- Be encouraging, never shaming. Say "You're close" or "Let's try another approach" — never that something was obvious or that they should already know it.
- Lead with the core idea in plain words, then one concrete example, then the detail.
- When it genuinely helps, end with ONE short check-for-understanding question. Never more than one.
- Use plain markdown: short paragraphs, occasional bullet lists. No big headings unless the student asked for structured notes.

Grounding rules:
- If a CONTEXT block of source excerpts is provided, base your answer on it and cite the excerpts inline like [S1] or [S2] right after the claims they support.
- If the context does not contain the answer, say so honestly, then clearly separate any general guidance you add from the sourced material.
- Never invent citations, facts, or figures."""


def source_qa_prompt(question: str, chunks: list[tuple[str, str, str]]) -> str:
    """Build a grounded Q&A prompt. chunks = [(label, title, text)], e.g. ("S1", ...)."""
    if chunks:
        blocks = []
        for label, title, text in chunks:
            excerpt = " ".join(str(text).split())
            blocks.append(f"[{label}] {title}\n{excerpt}")
        context = "\n\n".join(blocks)
    else:
        context = "(no relevant excerpts were found)"
    return f"""CONTEXT (excerpts from the student's own sources):

{context}

QUESTION: {question}

Answer the question using ONLY the context above.
- Cite the excerpts supporting each claim inline, like [S1] or [S1][S3], right after the claim.
- If the context does not contain the answer, say so honestly in one sentence and do not invent sources — then, clearly separated, offer brief general guidance if you can.
- Keep the answer focused and student-friendly."""


def quiz_prompt(
    topic_title: str,
    difficulty: str = "medium",
    n: int = 5,
    focus: str = "mixed",
    context: str | None = None,
) -> str:
    focus_line = {
        "mixed": "Mix styles across definitions, conceptual understanding, and applied scenarios.",
        "definitions": "Focus on definitions and precise terminology.",
        "concepts": "Focus on conceptual understanding and why-it-works reasoning.",
        "applications": "Focus on applied, scenario-based problems.",
    }.get(focus, "Mix styles across definitions, concepts, and applications.")
    context_block = f"\nBase the quiz on these source excerpts:\n{context}\n" if context else ""
    return f"""Create a quiz of exactly {n} multiple-choice questions on "{topic_title}" at {difficulty} difficulty.
{focus_line}{context_block}
Return ONLY a JSON object in exactly this shape:
{{"questions": [{{"prompt": "...", "options": ["...", "...", "...", "..."], "correctIndex": 0, "explanation": "...", "tag": "Definitions"}}]}}

Rules:
- Exactly {n} questions; each has exactly 4 options and exactly one correct answer.
- "correctIndex" is an integer 0-3; vary it across questions.
- "tag" is exactly one of: "Definitions", "Concepts", "Applications".
- Distractors must be plausible mistakes a student actually makes — no joke options.
- "explanation" teaches in 1-2 sentences why the correct answer is right, warmly and without shaming."""


def roadmap_prompt(
    goal: str,
    level: str = "Beginner",
    hours_per_week: int = 5,
    deadline: str | None = None,
    known: list[str] | None = None,
) -> str:
    deadline_line = f"Target deadline: {deadline}.\n" if deadline else ""
    known_line = (
        f"They already know: {', '.join(known)}. Compress or skip those parts.\n" if known else ""
    )
    return f"""Design a personalised learning roadmap.

Goal: {goal}
Current level: {level}
Available time: about {hours_per_week} hours per week.
{deadline_line}{known_line}
Return ONLY a JSON object in exactly this shape:
{{"title": "...", "type": "Subject", "focus": "...", "milestones": [{{"title": "...", "topics": [{{"title": "...", "minutes": 60, "summary": "...", "subtopics": ["..."]}}]}}]}}

Rules:
- 3-5 milestones ordered from fundamentals to applied work; each milestone has 2-4 topics.
- "minutes" is a realistic whole-number estimate of focused work for that topic.
- "summary" is 1-2 motivating sentences on what the topic covers and why it matters for the goal.
- "subtopics" lists 2-4 short, concrete items.
- "focus" names the single most valuable theme to start with.
- "type" is one of "Subject", "Topic", "Exam", "Skill" — whichever best matches the goal.
- Fit the total workload honestly to the weekly hours and any deadline; better a leaner plan completed than a heroic one abandoned."""


def flashcards_prompt(topic_title: str, count: int = 8, context: str | None = None) -> str:
    context_block = f"\nBase the cards on these source excerpts:\n{context}\n" if context else ""
    return f"""Create exactly {count} flashcards for the topic "{topic_title}".{context_block}
Return ONLY a JSON object in exactly this shape:
{{"cards": [{{"front": "...", "back": "..."}}]}}

Rules:
- "front" is one crisp question or term (about 15 words max).
- "back" is the answer in 1-3 short sentences a student can recall verbatim.
- Cover the highest-value material first: definitions, formulas, contrasts, then one common mistake.
- Plain text only on the cards — no numbering, no markdown."""


def study_guide_prompt(subject: str, context: str | None = None) -> str:
    context_block = (
        f"\nGround the guide in these source excerpts and stay faithful to them:\n{context}\n"
        if context
        else ""
    )
    return f"""Write a structured study guide for "{subject}".{context_block}
Return ONLY a JSON object in exactly this shape:
{{"title": "...", "sections": [{{"id": "overview", "title": "...", "kind": "overview", "markdown": "..."}}]}}

Rules:
- 5-8 sections. "kind" must be one of: "overview", "concepts", "definitions", "formulas", "examples", "mistakes", "tips", "practice", "revision".
- Put "overview" first; include "mistakes" (common errors) and "practice" whenever the subject allows.
- "id" is a short unique kebab-case slug; "title" is the human heading.
- "markdown" is the body in clean markdown: short paragraphs, bullet lists, **bold** key terms; formulas in plain notation.
- Write like a calm expert tutor: direct, encouraging, zero filler."""


def mindmap_prompt(subject: str, context: str | None = None) -> str:
    context_block = f"\nGround the map in these source excerpts:\n{context}\n" if context else ""
    return f"""Build a mind map of "{subject}".{context_block}
Return ONLY a JSON object in exactly this shape:
{{"center": "...", "nodes": [{{"id": "n1", "label": "...", "parentId": null}}]}}

Rules:
- "center" is the subject itself; do not repeat it as a node.
- 8-16 nodes total: 3-5 first-level branches ("parentId": null) plus their children ("parentId" set to the parent's "id").
- "id" values are short unique strings ("n1", "n2", ...); every "parentId" must be null or an existing id.
- "label" is at most 4 words, concrete enough that a student could ask a tutor about it.
- Organise branches by how the ideas relate, from fundamentals toward applications."""


def studycast_prompt(subject: str, minutes: int = 5, context: str | None = None) -> str:
    lines_target = max(8, minutes * 4)
    context_block = (
        f"\nBase the conversation on these source excerpts:\n{context}\n" if context else ""
    )
    return f"""Write a studycast — a two-host audio study dialogue — about "{subject}", sized for about {minutes} minutes of listening.{context_block}
Return ONLY a JSON object in exactly this shape:
{{"title": "...", "lines": [{{"speaker": "A", "text": "..."}}]}}

Rules:
- Speaker "A" is the curious learner: asks sharp questions and voices the confusions real students have. Speaker "B" is the friendly expert.
- Roughly {lines_target} lines, alternating A and B, each 1-3 spoken sentences — natural speech, contractions welcome.
- Open with a hook (why this matters), build one idea at a time, and close with a 3-point recap from B.
- No stage directions, no markdown, no host names — only "speaker" and "text"."""


def evaluate_answer_prompt(
    question: str,
    options: list[str],
    chosen: int,
    correct: int,
    topic: str | None = None,
) -> str:
    numbered = "\n".join(f"{i}. {option}" for i, option in enumerate(options))
    topic_line = f' on the topic "{topic}"' if topic else ""
    chosen_text = options[chosen] if 0 <= chosen < len(options) else str(chosen)
    correct_text = options[correct] if 0 <= correct < len(options) else str(correct)
    return f"""Evaluate a student's answer to a quiz question{topic_line}.

Question: {question}
Options:
{numbered}
The student chose option {chosen}: "{chosen_text}"
The correct answer is option {correct}: "{correct_text}"

Return ONLY a JSON object in exactly this shape:
{{"correct": false, "misconception": "...", "feedback": "..."}}

Rules:
- "correct" is true only when the chosen option is the correct one.
- "misconception": when wrong, name the specific underlying confusion in one sentence (which two ideas got mixed up); null when the answer is correct.
- "feedback": 2-3 warm sentences. Never shame. When wrong, start from what was right in their thinking ("You're close — ..."), guide them toward the key distinction, and end with one short nudge question. When right, reinforce why it is right and stretch them slightly."""


def misconception_prompt(topic_title: str, observations: list[str]) -> str:
    """observations = short strings describing recent mistakes/answers on this topic."""
    observed = "\n".join(f"- {item}" for item in observations) or "- (no details recorded)"
    return f"""A student studying "{topic_title}" keeps stumbling. Recent evidence:
{observed}

Identify the single most likely misconception behind this pattern.
Return ONLY a JSON object in exactly this shape:
{{"misconception": "...", "clarification": "...", "checkQuestion": "..."}}

Rules:
- "misconception" names the confused belief in one precise sentence (the two ideas being mixed up).
- "clarification" untangles it in 2-4 sentences with one concrete example — encouraging, never shaming.
- "checkQuestion" is one short question that becomes easy once the confusion is resolved."""


_EXPLAIN_STYLES: dict[str, str] = {
    "simpler": (
        "Re-explain it in the plainest possible language: short sentences, everyday "
        "words, no jargon. Aim at a bright 12-year-old."
    ),
    "analogy": (
        "Re-explain it through one vivid everyday analogy. Commit to the analogy, "
        "then map each of its parts back to the real idea."
    ),
    "real_world": (
        "Re-explain it through one concrete real-world scenario where this idea "
        "genuinely matters, told as a mini-story."
    ),
    "visual": (
        "Re-explain it as a picture in words: describe, step by step, a simple "
        "diagram the student could sketch, using spatial language (left, right, "
        "arrows, boxes)."
    ),
    "mathematical": (
        "Re-explain it precisely through the underlying mathematics: define each "
        "symbol, state the key equation(s), and walk through them term by term."
    ),
    "technical": (
        "Re-explain it rigorously with correct technical terminology, as to a "
        "junior practitioner — precise but well organised."
    ),
    "code": (
        "Re-explain it through a short runnable Python example with a comment on "
        "every step; let the code carry the explanation."
    ),
}


def explain_differently_prompt(
    concept: str,
    style: str = "simpler",
    previous_explanation: str | None = None,
) -> str:
    """style: simpler | analogy | real_world | visual | mathematical | technical | code"""
    instruction = _EXPLAIN_STYLES.get(style, _EXPLAIN_STYLES["simpler"])
    previous_block = (
        f"\nThe explanation that did not land:\n{previous_explanation}\n"
        if previous_explanation
        else ""
    )
    return f"""The student wants "{concept}" explained a different way.{previous_block}
{instruction}

Keep it under about 180 words, end with one quick check question, and keep the tone warm — an explanation not landing the first time is normal, not a failure."""
