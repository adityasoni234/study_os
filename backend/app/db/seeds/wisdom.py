"""Wisdom verses — authentic, widely-cited classical texts only.

The first three entries are copied VERBATIM from the frontend dataset
(src/data/wisdom.ts). The last two are standard renderings of famous
Bhagavad Gita lines. NEVER alter or paraphrase the quotations; the
ai_reflection and question fields are authored StudyOS copy, labeled as such
in the API (aiReflection). Idempotent: checks by id before insert.
"""

from sqlalchemy.orm import Session

from app.models.wellbeing import WisdomItem

VERSES: list[dict] = [
    {
        "id": "gita-2-47",
        "original": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        "transliteration": "karmaṇy-evādhikāras te mā phaleṣu kadācana",
        "translation": "You have a right to your actions alone, never to their fruits.",
        "source_ref": "Bhagavad Gita 2.47",
        "source_note": "Classical text · common English rendering",
        "ai_reflection": (
            "Study sessions go better when the goal is “sit with this for 25 "
            "minutes”, not “be brilliant today”. The effort is yours; the outcome "
            "follows on its own schedule."
        ),
        "question": (
            "Where in your learning could you focus more on the process and less "
            "on the outcome?"
        ),
        "tradition": "Vedanta",
    },
    {
        "id": "vidya",
        "original": "विद्या ददाति विनयम्",
        "transliteration": "vidyā dadāti vinayam",
        "translation": "Knowledge gives humility.",
        "source_ref": "Hitopadesha",
        "source_note": "Classical Sanskrit maxim · common English rendering",
        "ai_reflection": (
            "The more you genuinely learn, the more comfortable “I don’t know "
            "yet” becomes. Getting a question wrong today was knowledge doing its "
            "quiet work."
        ),
        "question": (
            "What is one thing you understand less well than you assumed a month "
            "ago — and why is noticing that a win?"
        ),
        "tradition": "Classical Sanskrit",
    },
    {
        "id": "gita-6-5",
        "original": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।",
        "transliteration": "uddhared ātmanātmānaṁ nātmānam avasādayet",
        "translation": "Lift yourself up by your own self; do not let yourself fall.",
        "source_ref": "Bhagavad Gita 6.5",
        "source_note": "Classical text · common English rendering",
        "ai_reflection": (
            "On the days motivation is missing, the smallest self-kept promise — "
            "one page, one problem — is how you lift yourself. Tiny, repeated, "
            "yours."
        ),
        "question": "What is the smallest promise you could keep to yourself today?",
        "tradition": "Vedanta",
    },
    {
        "id": "gita-2-50",
        "original": "योगः कर्मसु कौशलम्",
        "transliteration": "yogaḥ karmasu kauśalam",
        "translation": "Yoga is skill in action.",
        "source_ref": "Bhagavad Gita 2.50",
        "source_note": "Classical text · common English rendering",
        "ai_reflection": (
            "Skill grows in the doing. One problem worked with full attention "
            "teaches more than an anxious hour spread across everything at once — "
            "the quality of the doing is the practice."
        ),
        "question": (
            "What would your next study block look like if you gave complete "
            "attention to just one small task?"
        ),
        "tradition": "Vedanta",
    },
    {
        "id": "gita-6-35",
        "original": "अभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते॥",
        "transliteration": "abhyāsena tu kaunteya vairāgyeṇa ca gṛhyate",
        "translation": (
            "But by practice and by detachment, O son of Kunti, the mind is "
            "restrained."
        ),
        "source_ref": "Bhagavad Gita 6.35",
        "source_note": "Classical text · common English rendering",
        "ai_reflection": (
            "The verse answers the complaint every student knows — “my mind won't "
            "sit still”. Focus is not a talent you have or lack; it is trained by "
            "gentle repetition, and by letting go of what you cannot control "
            "right now. Every session is a rep."
        ),
        "question": (
            "Which one distraction could you set down, just for your next study "
            "block?"
        ),
        "tradition": "Vedanta",
    },
]


def seed(session: Session) -> None:
    for verse in VERSES:
        if session.get(WisdomItem, verse["id"]) is None:
            session.add(WisdomItem(**verse, verified=True))
    session.flush()
