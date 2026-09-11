# StudyOS Backend — Architecture

**Read this first. It is the source of truth for conventions. Do not deviate without updating it.**

## System

```
Frontend (React, :5173)
   ↕ JSON over HTTP (camelCase)
FastAPI app  (app/main.py)
   ↕
Routers (app/routers/*)          — thin: validate → call service → envelope
Services (app/services/*)        — business logic, DB + AI orchestration
AI layer (app/ai/*)              — provider-neutral generation + routing
Retrieval (app/retrieval/*)      — ingestion, embeddings, vector search, citations
Opportunities (app/opportunities/*) — search adapters + explainable matching
   ↕
SQLAlchemy 2 models (app/models/*) → PostgreSQL + pgvector (prod) / SQLite (dev fallback)
```

## Hard conventions

1. **Response envelope** — every endpoint returns
   `{"success": true, "data": ..., "error": null, "meta": {...}}` via `app.utils.envelope.ok()`,
   errors via raising `app.utils.errors.AppError(code, message, status)`.
   **Single exception:** `POST /api/chat` returns the flat competition shape `{"response": "..."}`.
2. **JSON is camelCase.** All Pydantic response/request schemas inherit
   `app.schemas.common.CamelModel`. Python stays snake_case.
3. **IDs** are string UUID4 hex (`uuid4().hex`), column type `String(32)`. Seeded demo rows may
   use readable ids (e.g. `"ml"`, `"demo-user"`) — treat ids as opaque strings everywhere.
4. **Timestamps** are timezone-aware UTC datetimes; Pydantic serialises them ISO-8601.
5. **Auth (MVP):** header `X-User-ID`; missing → `demo-user`. `app.utils.deps.get_current_user`
   returns the `User` row, **auto-creating it** if absent. Keep auth swappable behind this dependency.
6. **DB style:** sync SQLAlchemy 2 (`Mapped`/`mapped_column`), sessions via `app.db.base.get_db`
   FastAPI dependency. Endpoints are plain `def` (FastAPI runs them in a threadpool) except
   streaming ones. Postgres is the target; **SQLite must keep working** (no PG-only column types
   outside the guarded embedding column — see DATABASE.md).
7. **AI:** all model calls go through `app.ai.router.generate(task, ...)`. Never call providers
   directly from services. Never leak provider/model names into API responses.
8. **Errors:** never expose stack traces, SQL, provider payloads, or keys. `AppError` codes are
   SCREAMING_SNAKE (`NOT_FOUND`, `VALIDATION_ERROR`, `AI_UNAVAILABLE`, `RATE_LIMITED`,
   `INTERNAL_ERROR`).
9. **Logging:** structured single-line JSON via `app.utils.logging_mw` (request id, route, ms,
   status). Log AI task/provider/latency — never message content, keys, or journal text.
10. **Router discovery:** every module in `app/routers/` exporting a module-level `router`
    (`APIRouter`) is auto-mounted under `/api`. Add a file; don't touch `main.py`.
11. **Seeds:** every module in `app/db/seeds/` exporting `seed(session)` is auto-run by
    `python -m scripts.dev_db` (idempotent — check before insert). Add a file; don't edit others'.
12. **Tests:** pytest; use the `client` fixture from `tests/conftest.py` (in-memory SQLite +
    mock AI). Each feature owner adds `tests/test_<area>.py`.

## Model routing (task → provider)

| TaskType (app.ai.base.TaskType) | Primary | Why |
|---|---|---|
| CHAT, TUTOR_FAST, QUIZ_GEN, FLASHCARDS, ROADMAP_GEN, SOURCE_QA, STUDYCAST, INTENT | openai | fast, structured, cheap |
| DEEP_EXPLAIN, MISCONCEPTION, EVALUATE_ANSWER, SYNTHESIS, STUDY_GUIDE | anthropic | deep reasoning, evaluation |

Fallback chain: primary → other live provider → mock. `AI_MODE=mock|live|auto` (auto = live iff
keys exist). `CROSS_CHECK=true` enables GPT→Claude review for EVALUATE_ANSWER/DEEP_EXPLAIN only.

## File ownership (agents: stay in your lane)

| Area | Owner | Paths |
|---|---|---|
| Spine (do not rewrite) | orchestrator | `app/config.py`, `app/db/base.py`, `app/utils/{envelope,errors}.py`, `app/ai/base.py`, `app/retrieval/types.py`, `app/schemas/common.py`, `app/routers/__init__.py`, `app/db/seeds/__init__.py` |
| DB | Agent-DB | `app/models/*`, `alembic*`, `app/db/seeds/core.py`, `scripts/dev_db.py`, `docs/DATABASE.md` |
| Core app | Agent-Core | `app/main.py`, `app/utils/{deps,logging_mw,ratelimit}.py`, `app/routers/health.py`, `tests/conftest.py`, `tests/test_health.py`, `tests/test_errors.py`, `Dockerfile`, `docker-compose.yml`, `README.md`, `scripts/smoke_test.py` |
| AI | Agent-AI | `app/ai/{providers,router,prompts,intent}*.py`, `tests/test_ai_router.py` |
| Tutor/learning | Agent-Tutor | `app/services/{tutor,mastery,mission}.py`, `app/routers/{chat,tutor,learning}.py`, `app/schemas/{chat,tutor,learning}.py`, `tests/test_chat.py`, `tests/test_tutor.py`, `tests/test_mastery.py` |
| RAG | Agent-RAG | `app/retrieval/{ingest,embeddings,store,citations}.py`, `app/services/notebook.py`, `app/routers/notebooks.py`, `app/schemas/notebook.py`, `tests/test_rag.py` |
| Roadmap/assessment | Agent-Roadmap | `app/services/{roadmap,quiz,flashcards,content,growth}.py`, `app/routers/{roadmaps,assessment,content,growth}.py`, `app/schemas/{roadmap,assessment,content,growth}.py`, `tests/test_roadmap.py`, `tests/test_quiz.py` |
| Opportunities | Agent-Opp | `app/opportunities/*`, `app/services/{opportunity,prepare}.py`, `app/routers/opportunities.py`, `app/schemas/opportunity.py`, `app/db/seeds/opportunities.py`, `tests/test_opportunities.py` |
| Wellbeing/wisdom | Agent-Well | `app/services/{wellbeing,wisdom}.py`, `app/routers/{wellbeing,wisdom}.py`, `app/schemas/{wellbeing,wisdom}.py`, `app/db/seeds/wisdom.py`, `tests/test_wellbeing.py` |

## Priorities

P0: health, /chat, providers+routing, tutor with learner context, roadmaps, mastery, quiz,
PDF/text RAG with citations, opportunities+match, stable contracts, tests.
P1: flashcards, study guide, mind map, growth, knowledge map, prepare-me.
P2: studycast, wellbeing, journal, wisdom.
Never trade P0 stability for P2 scope.
