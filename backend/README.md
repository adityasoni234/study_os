# StudyOS Backend

FastAPI backend for **StudyOS** — an AI study companion: adaptive tutoring with mastery
tracking, AI-generated roadmaps, quizzes and flashcards, notebook RAG with citations
(PDF/text/URL), matched opportunities (hackathons/internships) with prep plans, plus
growth, wellbeing, and daily-wisdom features.

- **API base:** `http://localhost:8000/api` · **Docs:** [`/api/docs`](http://localhost:8000/api/docs) · **OpenAPI:** [`/api/openapi.json`](http://localhost:8000/api/openapi.json)
- **Contracts:** [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) · **Conventions:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · **Schema:** [`docs/DATABASE.md`](docs/DATABASE.md)

## Architecture

```
Frontend (React, :5173)
   ↕ JSON over HTTP (camelCase envelope)
FastAPI app (app/main.py) ── CORS · request-id logging · rate limit · error handlers
   ↕
Routers (app/routers/*)            thin: validate → service → envelope   [auto-mounted under /api]
Services (app/services/*)          business logic, DB + AI orchestration
AI layer (app/ai/*)                provider-neutral: task → OpenAI/Anthropic/mock routing
Retrieval (app/retrieval/*)        ingestion, embeddings, vector search, citations
Opportunities (app/opportunities/*) search adapters + explainable matching
   ↕
SQLAlchemy 2 models (app/models/*) → PostgreSQL 16 + pgvector (prod) / SQLite (dev)
```

Routers and seed modules are **auto-discovered**: drop a module in `app/routers/`
(exporting `router`) or `app/db/seeds/` (exporting `seed(session)`) — no wiring needed.

## Quickstart — SQLite (zero infra)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.dev_db          # optional: create tables + seed demo data
uvicorn app.main:app --reload
```

`uvicorn` alone also works: on startup the app auto-creates tables and runs the
idempotent seeds when the database is SQLite. Without keys, AI runs in **mock mode** —
every feature works with deterministic content.

## Postgres + pgvector (Docker)

```bash
cd backend
docker compose up --build         # db (pgvector/pg16) + api on :8000
```

The API container runs `alembic upgrade head` before starting, then seeds idempotently.
The image installs `psycopg[binary]` (the Postgres driver) — it is intentionally **not**
in `requirements.txt` so the SQLite path stays zero-dep. Pointing a local venv at
Postgres instead? Run `pip install "psycopg[binary]"` and set:

```bash
export DATABASE_URL='postgresql+psycopg://studyos:studyos@localhost:5432/studyos'
alembic upgrade head && uvicorn app.main:app --reload
```

## Environment variables

Copy `.env.example` to `.env` and adjust. All are optional — defaults run out of the box.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./studyos.db` | SQLAlchemy URL. Postgres: `postgresql+psycopg://studyos:studyos@localhost:5432/studyos` |
| `OPENAI_API_KEY` | *(empty)* | OpenAI key (fast/structured tasks) |
| `ANTHROPIC_API_KEY` | *(empty)* | Anthropic key (deep reasoning/evaluation) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model id |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Anthropic model id |
| `ANTHROPIC_WORKSPACE_ID` | *(empty)* | Only for org-level Anthropic keys — workspace-scoped keys don't need it |
| `AI_MODE` | `auto` | `mock` \| `live` \| `auto` (auto = live iff keys present) |
| `CROSS_CHECK` | `false` | GPT→Claude review for deep evaluation tasks (costlier) |
| `EMBEDDING_PROVIDER` | `auto` | `auto` \| `mock` \| `openai` |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `SEARCH_PROVIDER` | `mock` | Opportunity search adapter (`mock` ships curated data) |
| `APP_ENV` | `dev` | Environment label in logs |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated allowed origins |
| `MAX_UPLOAD_MB` | `25` | Upload cap for notebook sources |
| `RATE_LIMIT_PER_MINUTE` | `120` | Sliding-window limit per user/IP |

## Tests & smoke test

```bash
.venv/bin/pytest                                  # in-memory SQLite + mock AI
BASE_URL=http://localhost:8000 python -m scripts.smoke_test   # against a running server
```

The smoke test prints PASS/WARN/FAIL with latency per endpoint; a 404 is a warning
(feature not mounted yet), any FAIL exits 1.

## Frontend integration

- **Envelope** — every endpoint returns camelCase JSON:
  `{"success": true, "data": {…}, "error": null, "meta": {…}}`; on failure
  `error` is `{"code": "NOT_FOUND", "message": "…"}` with an appropriate HTTP status.
- **Single exception:** `POST /api/chat` returns the flat shape `{"response": "…"}`.
- **Auth (MVP):** send `X-User-ID: <id>` (optional; defaults to `demo-user`, auto-created
  with a profile). Keep using this header — real auth swaps in behind it.
- Every response carries an `X-Request-ID` header (also accepted inbound) for tracing.
- Error codes: `NOT_FOUND`, `VALIDATION_ERROR`, `AI_UNAVAILABLE`, `RATE_LIMITED`,
  `UNSUPPORTED_FILE`, `FILE_TOO_LARGE`, `INTERNAL_ERROR`.

## Deployment notes

- One process is fine for the MVP: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  (add `--workers N` behind a real DB; the rate limiter is per-process/in-memory).
- Postgres path: run `alembic upgrade head` before starting the app (the Docker CMD
  already does). Seeds are idempotent and safe to run on every boot.
- Set `CORS_ORIGINS` to your deployed frontend origin(s); keep credentials mode on.
- Logs are single-line JSON on stdout (`{"ts","requestId","method","path","status","ms"}`)
  — ship them straight to your log aggregator.

## Security notes

- **AI keys live server-side only** — never sent to the browser, never logged, never
  echoed in API responses (provider/model names are not leaked either).
- Errors are sanitized: no stack traces, SQL, or provider payloads cross the API
  boundary (`INTERNAL_ERROR` with a generic message instead).
- Request logging records metadata only — never bodies, journal text, or chat content.
- Rate limiting (429 `RATE_LIMITED`) is on by default; `/api/health` and docs are exempt.
- MVP auth is a trusted header (`X-User-ID`) suitable for demos, not the open internet —
  front it with a gateway or replace `app/utils/deps.py` internals before public exposure.
