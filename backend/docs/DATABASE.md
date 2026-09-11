# StudyOS Database

Target: **PostgreSQL 16 + pgvector** (docker-compose). Dev fallback: **SQLite** — every model must
work on both. The only PG-specific type allowed is the guarded embedding column (see below).

## Conventions
- PK: `id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: uuid4().hex)`
- `created_at`/`updated_at`: tz-aware UTC defaults.
- FKs `ondelete="CASCADE"` for owned children. Index every FK used in lookups.
- Enums as `String` columns with Python `Literal`/constants (portable), CHECK constraints optional.
- **Embedding column** (`source_chunks.embedding`): on Postgres use `pgvector` `Vector(1536)`;
  on SQLite fall back to JSON text. Implement once in `app/db/vector_type.py` as a
  `TypeDecorator` choosing the impl by dialect; store `list[float] | None`.
- Never duplicate learner state: **Mastery** is the single source of truth per (user, topic);
  roadmap progress is computed from mastery + node status.

## Entities (canonical list — implement all)

- **User**(id, email?, name, created_at) / **Profile**(user_id PK→users, level, daily_goal_minutes,
  explanation_style, streak_days, preferences JSON)
- **Goal**(id, user_id, title, kind, target_date?, status)
- **Roadmap**(id, user_id, goal_id?, title, type, tone, icon, goal_text, target_date, focus,
  next_action, next_topic_id, adapted_note?, is_new, archived, created_at)
- **RoadmapNode**(id, roadmap_id, parent_id? self-FK, kind: 'milestone'|'topic'|'subtopic',
  title, status, position, minutes, summary?, note?, topic_id? → topics.id, depends_on JSON)
- **Subject**(id, title, icon, tone) / **Topic**(id, subject_id?, slug unique, title, summary) /
  **Subtopic**(id, topic_id, title, position)
- **LearningSession**(id, user_id, topic_id?, mode, started_at, ended_at?) /
  **Message**(id, session_id, role, text, payload JSON?, created_at)
- **Mastery**(id, user_id, topic_id, value 0-100, trend, updated_at; unique (user_id, topic_id))
- **Quiz**(id, user_id, topic_id?, notebook_id?, difficulty, focus, created_at) /
  **QuizQuestion**(id, quiz_id, position, prompt, options JSON, correct_index, explanation, tag) /
  **QuizAttempt**(id, quiz_id, user_id, score, total, answers JSON, strengths JSON, weaknesses JSON, created_at)
- **Notebook**(id, user_id, title, created_at) / **Source**(id, notebook_id, title, kind, status,
  meta, url?, added_at) / **SourceChunk**(id, source_id, notebook_id, position, page?, text,
  embedding VectorOrJSON?, created_at)
- **Flashcard**(id, user_id, topic_id?, front, back, weak, due_at?, created_at)
- **StudyGuide**(id, user_id, topic_id?, notebook_id?, title, sections JSON, created_at)
- **MindMap**(id, user_id, topic_id?, notebook_id?, center, nodes JSON, created_at)
- **Opportunity**(id, title, org, type, tone, description, deadline_text, deadline_date?,
  days_left?, mode, eligibility, skills JSON, source, source_url, verified, created_at)
- **SavedOpportunity**(id, user_id, opportunity_id, created_at; unique pair)
- **OpportunityApplication / PrepPlan**(id, user_id, opportunity_id, readiness, gap_note,
  days JSON, started, created_at) + **PrepTask**(id, plan_id, day, position, label, done)
- **WellbeingLog**(id, user_id, kind, note?, created_at)
- **JournalEntry**(id, user_id, mood, mood_label, note, created_at)
- **WisdomItem**(id, original, transliteration, translation, source_ref, source_note,
  ai_reflection, question, tradition, verified) + **SavedWisdom**(user_id, wisdom_id)
- **Recommendation**(id, user_id, kind, title, reason, route, topic_id?, created_at, dismissed)
- **DailyMission**(id, user_id, date, topic_id, title, context, minutes, steps JSON, adapted_note)

## Migrations
Alembic; migration `0001_initial` may create schema from `Base.metadata` (documented MVP
tradeoff) and must `CREATE EXTENSION IF NOT EXISTS vector` on Postgres. From-zero path:
`alembic upgrade head` (Postgres) or `python -m scripts.dev_db` (SQLite dev: create_all + seeds).

## Seeds (`app/db/seeds/*.py`, each exports `seed(session)`, idempotent)
- `core.py`: demo user `demo-user` (Aditya) + profile (streak 12), topics for the ML domain,
  the **Machine Learning roadmap** exactly matching the example in API_CONTRACT.md (milestones
  Foundations/Core ML/Neural Networks/Capstone; `precision-recall` current at mastery 65),
  plus Python/Career/Communication roadmaps (lighter), mastery rows, default notebook with
  4 ready sources ("ML Course Notes — Unit 3" PDF etc.) and their `SourceChunk` rows using the
  passage texts in `app/db/seeds/passages.py` (embeddings left NULL — retrieval backfills).
- `opportunities.py` (Agent-Opp), `wisdom.py` (Agent-Well).
