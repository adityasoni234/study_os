# StudyOS API Contract

Base URL: `http://localhost:8000/api` · Docs: `GET /api/docs` · Spec: `GET /api/openapi.json`

**Envelope (every endpoint except `POST /api/chat`):**

```json
{ "success": true,  "data": { }, "error": null, "meta": { "requestId": "…" } }
{ "success": false, "data": null, "error": { "code": "NOT_FOUND", "message": "…" }, "meta": { } }
```

- JSON keys are **camelCase**. Timestamps are ISO-8601 UTC. IDs are opaque strings, stable across calls.
- Auth: send `X-User-ID: <id>` (optional; defaults to `demo-user`, auto-created).
- Fields may be `null`; object *shapes* never change between calls.
- Error codes: `NOT_FOUND`, `VALIDATION_ERROR`, `AI_UNAVAILABLE`, `RATE_LIMITED`, `UNSUPPORTED_FILE`, `FILE_TOO_LARGE`, `INTERNAL_ERROR`.

## Core

### POST /api/chat  — competition endpoint (flat shape, no envelope)
Req `{"message": "Explain precision vs recall"}` → Res `{"response": "…tutor answer…"}`

### POST /api/tutor/message
Req:
```json
{ "sessionId": null, "topicId": "precision-recall", "message": "Explain simpler",
  "mode": "teach" }
```
`mode`: `teach|practice|review|quiz|feedback|mastery|explain_differently` (optional; server infers).
Res data:
```json
{ "sessionId": "…", "reply": { "role": "tutor", "text": "…", "citations": [Citation], "suggestions": ["Test me", "Give an analogy"], "quiz": null },
  "state": { "topicId": "precision-recall", "mastery": 72, "masteryDelta": 7, "mode": "teach", "misconception": null } }
```
`reply.quiz` (when tutor asks a check): `{ "questionId": "…", "question": "…", "options": ["…"], "correctIndex": null }` (correct index withheld; submit via tutor/message with mode `feedback` and `answerIndex`).

### GET /api/tutor/session/{id}
Res data: `{ "id": "…", "topicId": "…", "messages": [{ "role": "tutor|student", "text": "…", "createdAt": "…" }], "state": {…} }`

## Roadmaps

`Roadmap` object (list + detail):
```json
{ "id": "ml", "title": "Machine Learning", "type": "Subject", "tone": "indigo", "icon": "brain",
  "goal": "…", "targetDate": "Nov 30", "progress": 68, "focus": "Classification Metrics",
  "nextAction": "Learn Precision & Recall", "nextTopicId": "precision-recall",
  "adaptedNote": "…", "isNew": false,
  "milestones": [ { "id": "ml-m1", "title": "Foundations", "status": "done",
      "topics": [ { "id": "python-data", "title": "Python for Data", "status": "done",
                    "mastery": 94, "minutes": 120, "summary": "…",
                    "subtopics": [ { "title": "Confusion Matrix", "state": "done" } ], "note": null } ] } ] }
```
`status`: milestone `done|current|locked`; topic `done|current|locked|review`.

- `POST /api/roadmaps` req `{ "goal": "…", "type": "Topic", "level": "Beginner", "hoursPerWeek": 5, "deadline": "Sep 18", "knownTopics": ["python"] }` → res data: full Roadmap (AI-generated, persisted).
- `GET /api/roadmaps` → `{ "roadmaps": [Roadmap-without-milestones] }`
- `GET /api/roadmaps/{id}` → full Roadmap.
- `PATCH /api/roadmaps/{id}` req any of `{ "targetDate", "goal", "archived" }` → updated Roadmap.
- `GET /api/roadmaps/{id}/progress` → `{ "progress": 71, "topicsDone": 4, "topicsTotal": 12, "mastery": { "precision-recall": 72 } }`

## Learning

- `GET /api/mastery` → `{ "topics": [ { "topicId": "…", "title": "…", "mastery": 72, "trend": "up|flat|down", "updatedAt": "…" } ] }`
- `GET /api/mastery/{topic_id}` → one of the above (404 if never seen).
- `GET /api/recommendations` → `{ "recommendations": [ { "id": "…", "kind": "review|learn|practice|opportunity", "title": "…", "reason": "…", "topicId": null, "route": "/tutor/…" } ] }`
- `GET /api/daily-mission` → `{ "topicId": "precision-recall", "title": "Precision & Recall", "context": "Machine Learning · Classification", "minutes": 25, "steps": [ { "id": "learn", "label": "…", "done": false } ], "adaptedNote": "…" }`
- `POST /api/daily-mission/steps/{step_id}/complete` → updated mission.

## Notebook

- `POST /api/notebooks` req `{ "title": "…" }` → Notebook `{ "id", "title", "createdAt", "sourceCount" }`
- `GET /api/notebooks` → `{ "notebooks": [Notebook] }` (a default notebook always exists).
- `POST /api/notebooks/{id}/sources` — multipart file (`file`) **or** JSON `{ "kind": "text|url|youtube|notes", "title": "…", "text": "…", "url": "…" }`.
  Res data: `Source` = `{ "id", "title", "kind": "pdf|web|youtube|notes|text", "status": "ready|processing|failed", "meta": "PDF · 42 pages", "addedAt" }`. PDF+text are synchronous (return `ready`).
- `GET /api/notebooks/{id}/sources` → `{ "sources": [Source] }`
- `POST /api/notebooks/{id}/ask` req `{ "question": "…" }` → 
```json
{ "answer": "…", "citations": [ { "sourceId": "…", "title": "ML Course Notes — Unit 3", "page": 14, "snippet": "…", "url": null } ],
  "grounded": true }
```
`grounded:false` + empty citations when nothing relevant was found (answer says so honestly).

## Assessment

- `POST /api/quiz/generate` req `{ "topicId": "precision-recall", "notebookId": null, "difficulty": "medium", "length": 5, "focus": "mixed" }`
  → `{ "quizId": "…", "topicId": "…", "questions": [ { "id": "…", "prompt": "…", "options": ["…"], "tag": "Definitions" } ] }` (no answers).
- `POST /api/quiz/{id}/submit` req `{ "answers": [ { "questionId": "…", "selectedIndex": 2 } ] }` →
```json
{ "score": 4, "total": 5, "masteryBefore": 65, "masteryAfter": 75,
  "perQuestion": [ { "questionId": "…", "correct": true, "correctIndex": 0, "explanation": "…" } ],
  "strengths": ["Definitions"], "weaknesses": ["Applications"],
  "recommendation": { "title": "Practice weak areas", "route": "/quiz/precision-recall" } }
```
- `POST /api/flashcards/generate` req `{ "topicId": "…", "notebookId": null, "count": 8 }` → `{ "cards": [ { "id", "front", "back", "weak": true } ] }`

## Content

- `POST /api/study-guide/generate` req `{ "topicId"| "notebookId" }` → `{ "title": "…", "sections": [ { "id", "title", "kind": "overview|concepts|definitions|formulas|examples|mistakes|tips|practice|revision", "markdown": "…", "citations": [Citation] } ] }`
- `POST /api/mindmap/generate` req `{ "topicId"|"notebookId" }` → `{ "center": "Machine Learning", "nodes": [ { "id", "label", "parentId": null, "mastery": 65, "topicId": "…" } ] }`
- `POST /api/studycast/generate` req `{ "notebookId", "minutes": 5 }` → `{ "id", "title", "minutes", "lines": [ { "speaker": "A|B", "text": "…" } ], "audioUrl": null }`

## Opportunities

`Opportunity`:
```json
{ "id": "hackathon-ai-ed", "title": "…", "org": "…", "type": "Hackathon", "tone": "violet",
  "deadline": "Sep 18", "daysLeft": 7, "mode": "Online", "blurb": "…", "eligibility": "…",
  "source": "devfolio.co", "sourceUrl": "https://…", "verified": true,
  "match": { "score": 94, "reasons": ["Python skill match"], "gaps": ["RAG experience"] },
  "saved": false }
```
- `GET /api/opportunities?tab=best|closing|new|saved` → `{ "opportunities": [Opportunity] }`
- `GET /api/opportunities/{id}` → Opportunity.
- `POST /api/opportunities/{id}/save` → `{ "saved": true }` (toggles).
- `POST /api/opportunities/{id}/prepare` → 
```json
{ "opportunityId": "…", "daysRemaining": 6, "readiness": 72,
  "gapNote": "RAG is new to you — Day 2 is lighter…",
  "days": [ { "day": 1, "title": "…", "minutes": 45, "tasks": [ { "id": "…", "label": "…", "done": false } ], "tutorTopicId": null, "note": null } ] }
```
- `POST /api/prepare/tasks/{task_id}/toggle` → `{ "done": true, "readiness": 78 }`

## Growth

- `GET /api/growth` → `{ "dimensions": [ { "id": "learning", "label": "Learning", "value": 78, "delta": 4, "tone": "indigo" } ], "week": [ { "day": "Mon", "minutes": 45 } ], "streakDays": 12, "insights": [ { "kind": "strongest|improving|attention", "title": "…", "detail": "…", "route": "…" } ], "nextStep": { "title": "…", "reason": "…", "route": "…" } }`
- `GET /api/knowledge-map` → `{ "areas": [ { "id", "title", "icon", "tone", "topics": [ { "topicId", "title", "mastery", "route": "/tutor/…" } ] } ] }`

## Wellbeing

- `POST /api/wellbeing/session` req `{ "kind": "reset|plan|talk", "message": "…" }` → `{ "reply": "…", "suggestions": ["…"], "disclaimer": "StudyOS offers study support, not medical care." }`
- `POST /api/journal` req `{ "mood": "😊", "moodLabel": "Great", "note": "…" }` → JournalEntry `{ "id", "mood", "moodLabel", "note", "createdAt" }`
- `GET /api/journal` → `{ "entries": [JournalEntry], "pattern": "Sessions before 9pm feel better…" | null }`

## Inner growth

`WisdomItem`: `{ "id", "original", "transliteration", "translation", "source": "Bhagavad Gita 2.47", "sourceNote": "Classical text · common English rendering", "aiReflection": "…", "question": "…", "verified": true, "saved": false }`
- `GET /api/wisdom/today` → WisdomItem (rotates daily).
- `GET /api/wisdom` → `{ "items": [WisdomItem] }`
- `POST /api/wisdom/{id}/save` → `{ "saved": true }` (toggles).

## Health

`GET /api/health` → `{ "status": "ok", "db": true, "aiMode": "mock|live", "version": "1.0.0" }` (enveloped).
