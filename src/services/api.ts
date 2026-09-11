/**
 * Isolated API layer. The UI never calls fetch directly — swap this file to
 * point at a different backend without touching a single screen.
 *
 * Every call degrades gracefully: when the backend is unreachable the caller
 * falls back to the built-in mock experience, so the prototype always works.
 */

const BASE = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api').replace(/\/$/, '')

export interface Envelope<T> {
  success: boolean
  data: T | null
  error: { code: string; message: string } | null
  meta: Record<string, unknown>
}

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
  ) {
    super(message)
  }
}

let online: boolean | null = null

/** Cached liveness probe so offline demos don't retry on every interaction. */
export async function backendAvailable(): Promise<boolean> {
  if (online !== null) return online
  try {
    const res = await fetch(`${BASE}/health`, { signal: AbortSignal.timeout(1500) })
    online = res.ok
  } catch {
    online = false
  }
  return online
}

async function request<T>(
  path: string,
  init: RequestInit & { userId?: string } = {},
): Promise<T> {
  const { userId, headers, ...rest } = init
  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': userId ?? 'demo-user',
      ...headers,
    },
    signal: AbortSignal.timeout(60_000),
  })

  const body = (await res.json()) as Envelope<T> | Record<string, unknown>

  if ('success' in body) {
    const env = body as Envelope<T>
    if (!env.success || env.error) {
      throw new ApiError(env.error?.code ?? 'INTERNAL_ERROR', env.error?.message ?? 'Request failed.')
    }
    return env.data as T
  }
  // Flat-shape endpoints (POST /chat).
  return body as T
}

/* ---------- Tutor ---------- */

export interface TutorCitation {
  sourceId: string
  title: string
  page: number | null
  snippet: string
  url: string | null
}

export interface TutorReply {
  sessionId: string
  reply: {
    role: 'tutor'
    text: string
    citations: TutorCitation[]
    suggestions: string[]
    quiz: { questionId: string; question: string; options: string[] } | null
  }
  state: {
    topicId: string | null
    mastery: number
    masteryDelta: number
    mode: string
    misconception: string | null
  }
}

export const api = {
  /** Competition endpoint — flat {response} shape. */
  chat: (message: string, userId?: string) =>
    request<{ response: string }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
      userId,
    }),

  tutorMessage: (
    body: {
      sessionId?: string | null
      topicId?: string | null
      message: string
      mode?: string
      style?: string
      questionId?: string
      answerIndex?: number
    },
    userId?: string,
  ) => request<TutorReply>('/tutor/message', { method: 'POST', body: JSON.stringify(body), userId }),

  askNotebook: (notebookId: string, question: string, userId?: string) =>
    request<{ answer: string; citations: TutorCitation[]; grounded: boolean }>(
      `/notebooks/${notebookId}/ask`,
      { method: 'POST', body: JSON.stringify({ question }), userId },
    ),

  generateQuiz: (
    body: { topicId?: string; notebookId?: string; difficulty?: string; length?: number; focus?: string },
    userId?: string,
  ) =>
    request<{
      quizId: string
      topicId: string | null
      questions: { id: string; prompt: string; options: string[]; tag: string }[]
    }>('/quiz/generate', { method: 'POST', body: JSON.stringify(body), userId }),

  submitQuiz: (
    quizId: string,
    answers: { questionId: string; selectedIndex: number }[],
    userId?: string,
  ) =>
    request<{
      score: number
      total: number
      masteryBefore: number
      masteryAfter: number
      perQuestion: { questionId: string; correct: boolean; correctIndex: number; explanation: string }[]
      strengths: string[]
      weaknesses: string[]
      recommendation: { title: string; route: string }
    }>(`/quiz/${quizId}/submit`, { method: 'POST', body: JSON.stringify({ answers }), userId }),

  roadmaps: (userId?: string) => request<{ roadmaps: unknown[] }>('/roadmaps', { userId }),
  roadmap: (id: string, userId?: string) => request<unknown>(`/roadmaps/${id}`, { userId }),
  growth: (userId?: string) => request<unknown>('/growth', { userId }),
  opportunities: (tab = 'best', userId?: string) =>
    request<{ opportunities: unknown[] }>(`/opportunities?tab=${tab}`, { userId }),
  dailyMission: (userId?: string) => request<unknown>('/daily-mission', { userId }),
}
