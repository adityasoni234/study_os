import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import type { GratitudeEntry, QuizRecord, Reflection, SourceItem, Tone } from '@/types'
import { uid } from '@/lib/utils'

export interface Toast {
  id: string
  title: string
  desc?: string
  tone: Tone
}

interface PersistedState {
  auth: { authed: boolean; name: string }
  mastery: Record<string, number>
  mission: { learn: boolean; practice: boolean; check: boolean }
  quizzes: QuizRecord[]
  saved: string[]
  prepStarted: boolean
  prepTasks: Record<string, boolean>
  reflections: Reflection[]
  gratitude: GratitudeEntry[]
  createdRoadmaps: string[]
  extraSources: SourceItem[]
  masteryMode: boolean
  planAdjusted: boolean
  lastSessionTopic: string | null
}

const DEFAULT_STATE: PersistedState = {
  auth: { authed: false, name: 'Aditya' },
  mastery: { 'precision-recall': 65 },
  mission: { learn: false, practice: false, check: false },
  quizzes: [],
  saved: [],
  prepStarted: false,
  prepTasks: {},
  reflections: [],
  gratitude: [],
  createdRoadmaps: [],
  extraSources: [],
  masteryMode: false,
  planAdjusted: false,
  lastSessionTopic: null,
}

const STORAGE_KEY = 'studyos-state-v1'

function loadState(): PersistedState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return DEFAULT_STATE
    const parsed = JSON.parse(raw) as Partial<PersistedState>
    return {
      ...DEFAULT_STATE,
      ...parsed,
      auth: { ...DEFAULT_STATE.auth, ...parsed.auth },
      mission: { ...DEFAULT_STATE.mission, ...parsed.mission },
    }
  } catch {
    return DEFAULT_STATE
  }
}

interface AppApi {
  state: PersistedState
  toasts: Toast[]
  toast: (title: string, desc?: string, tone?: Tone) => void
  dismissToast: (id: string) => void

  signIn: (name: string) => void
  signOut: () => void
  masteryOf: (topicId: string, fallback?: number) => number
  setMastery: (topicId: string, value: number) => void
  completeMissionStep: (step: 'learn' | 'practice' | 'check') => void
  recordQuiz: (rec: Omit<QuizRecord, 'id' | 'date'>) => void
  toggleSaved: (oppId: string) => void
  startPrep: () => void
  togglePrepTask: (key: string) => void
  addReflection: (r: Omit<Reflection, 'id' | 'date'>) => void
  addGratitude: (text: string) => void
  createRoadmap: (id: string) => void
  addSource: (s: Omit<SourceItem, 'id' | 'status'>) => string
  markSourceReady: (id: string) => void
  setMasteryMode: (on: boolean) => void
  applyLighterPlan: () => void
  setLastSessionTopic: (topicId: string) => void
  roadmapProgress: (roadmapId: string, base: number) => number
  resetDemo: () => void
}

const Ctx = createContext<AppApi | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PersistedState>(loadState)
  const [toasts, setToasts] = useState<Toast[]>([])
  const timers = useRef<Record<string, number>>({})

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      /* private mode etc. — fine */
    }
  }, [state])

  const dismissToast = useCallback((id: string) => {
    setToasts((t) => t.filter((x) => x.id !== id))
    const timer = timers.current[id]
    if (timer) window.clearTimeout(timer)
  }, [])

  const toast = useCallback(
    (title: string, desc?: string, tone: Tone = 'indigo') => {
      const id = uid('toast')
      setToasts((t) => [...t.slice(-2), { id, title, desc, tone }])
      timers.current[id] = window.setTimeout(() => dismissToast(id), 4600)
    },
    [dismissToast],
  )

  const api = useMemo<AppApi>(() => {
    const update = (fn: (s: PersistedState) => PersistedState) => setState(fn)

    return {
      state,
      toasts,
      toast,
      dismissToast,

      signIn: (name) =>
        update((s) => ({ ...s, auth: { authed: true, name: name.trim() || 'Aditya' } })),

      signOut: () => update((s) => ({ ...s, auth: { ...s.auth, authed: false } })),

      masteryOf: (topicId, fallback = 0) => state.mastery[topicId] ?? fallback,

      setMastery: (topicId, value) =>
        update((s) => ({
          ...s,
          mastery: { ...s.mastery, [topicId]: Math.max(s.mastery[topicId] ?? 0, value) },
        })),

      completeMissionStep: (step) =>
        update((s) => ({ ...s, mission: { ...s.mission, [step]: true } })),

      recordQuiz: (rec) =>
        update((s) => ({
          ...s,
          quizzes: [...s.quizzes, { ...rec, id: uid('quiz'), date: new Date().toISOString() }],
        })),

      toggleSaved: (oppId) =>
        update((s) => ({
          ...s,
          saved: s.saved.includes(oppId) ? s.saved.filter((x) => x !== oppId) : [...s.saved, oppId],
        })),

      startPrep: () => update((s) => ({ ...s, prepStarted: true })),

      togglePrepTask: (key) =>
        update((s) => ({ ...s, prepTasks: { ...s.prepTasks, [key]: !s.prepTasks[key] } })),

      addReflection: (r) =>
        update((s) => ({
          ...s,
          reflections: [
            { ...r, id: uid('refl'), date: new Date().toISOString() },
            ...s.reflections,
          ],
        })),

      addGratitude: (text) =>
        update((s) => ({
          ...s,
          gratitude: [
            { id: uid('grat'), text, date: new Date().toISOString() },
            ...s.gratitude,
          ],
        })),

      createRoadmap: (id) =>
        update((s) =>
          s.createdRoadmaps.includes(id) ? s : { ...s, createdRoadmaps: [...s.createdRoadmaps, id] },
        ),

      addSource: (src) => {
        const id = uid('src')
        update((s) => ({
          ...s,
          extraSources: [{ ...src, id, status: 'processing' }, ...s.extraSources],
        }))
        return id
      },

      markSourceReady: (id) =>
        update((s) => ({
          ...s,
          extraSources: s.extraSources.map((x) => (x.id === id ? { ...x, status: 'ready' } : x)),
        })),

      setMasteryMode: (on) => update((s) => ({ ...s, masteryMode: on })),

      applyLighterPlan: () => update((s) => ({ ...s, planAdjusted: true })),

      setLastSessionTopic: (topicId) => update((s) => ({ ...s, lastSessionTopic: topicId })),

      roadmapProgress: (roadmapId, base) => {
        if (roadmapId === 'ml') {
          const m = state.mission
          return Math.min(base + (m.learn ? 2 : 0) + (m.practice ? 2 : 0) + (m.check ? 2 : 0), 99)
        }
        if (roadmapId === 'prep') {
          const done = Object.values(state.prepTasks).filter(Boolean).length
          return Math.min(Math.round((done / 18) * 100), 100)
        }
        return base
      },

      resetDemo: () => {
        try {
          localStorage.removeItem(STORAGE_KEY)
        } catch {
          /* noop */
        }
        setState(DEFAULT_STATE)
      },
    }
  }, [state, toasts, toast, dismissToast])

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>
}

export function useApp(): AppApi {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useApp must be used inside AppProvider')
  return ctx
}
