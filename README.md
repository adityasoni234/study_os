# StudyOS — Learn anything. Grow every day.

An adaptive AI learning companion built for **UN SDG 4 · Quality Education**.
Sources → Roadmap → 1:1 Tutor → Practice → Mastery → Growth → Real-world opportunities.

This repository contains:

| Part | Path | Stack |
|---|---|---|
| **Frontend** (this folder) | `/` | React 19 · Vite · TypeScript · Tailwind CSS v4 · React Router 7 · Lucide |
| **Backend** | `/backend` | FastAPI · SQLAlchemy 2 · PostgreSQL + pgvector (SQLite fallback) · OpenAI + Anthropic |

## Run the frontend

```bash
npm install
npm run dev
```

Open http://localhost:5173. You'll land on the marketing page, then sign in.
The prototype is fully interactive with realistic mock data and a scripted adaptive tutor — no
backend required for the demo. Learning state (mastery, mission progress, saved items) persists in
`localStorage`; reset it any time in **Settings → Reset demo data**.

### Authentication

Sign-in uses **Firebase Authentication** (email/password, Google, or anonymous "demo learner").
Copy `.env.example` to `.env` and fill in your Firebase web config:

```bash
cp .env.example .env   # then paste your VITE_FIREBASE_* values
```

In the Firebase console enable **Email/Password**, **Google**, and **Anonymous** under
Authentication → Sign-in method, and add your domain under Authorized domains.
Without a `.env`, the app still runs — auth falls back to a local demo session, so the
demo never blocks.

## Run the backend

See [backend/README.md](backend/README.md). Quick version:

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m scripts.dev_db        # create + seed the dev database (SQLite)
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000/api/docs
```

## Demo flow (what to show judges)

The polished golden path lives in [DEMO.md](DEMO.md).

## How the two halves connect

The UI talks to the backend through one isolated module — [`src/services/api.ts`](src/services/api.ts).
Nothing else in the app calls `fetch`, so pointing at a different backend is a one-file change.
Every call degrades gracefully: if the API isn't reachable, screens fall back to the built-in mock
experience. Today the tutor sends **free-text questions** to the live backend (real retrieval,
real citations, real mastery updates) while the scripted golden path stays deterministic for demos.

## Product map

- **Home** — Today's Mission, journeys, recommendations, opportunity highlight
- **Roadmaps** — adaptive journey timelines, creation wizard, per-topic panels
- **1:1 Tutor** — the hero: explains, quizzes inline, adapts on mistakes, updates mastery
- **Notebook** — sources → grounded chat with citations, study guide, mind map, quiz, flashcards, StudyCast
- **Growth** — progress dimensions, momentum, insights, knowledge map
- **Opportunity Radar** — matched real-world opportunities with explainable match scores → Prepare Me plans
- **Wellbeing** — reset mode, planning help, supportive chat, reflection journal (support, not therapy)
- **Inner Growth** — optional daily verse (authentic classical texts, AI reflection clearly labeled), gratitude
