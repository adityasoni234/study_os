import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  ArrowLeft,
  Check,
  Code2,
  Eye,
  Feather,
  Globe,
  Lightbulb,
  Mic,
  Paperclip,
  RefreshCw,
  Send,
  Sigma,
  Sparkles,
  Target,
  Wrench,
  X,
} from 'lucide-react'
import type { ChatMsg, InlineQuiz, ScriptEffect, TutorBlock } from '@/types'
import { topicTitle } from '@/data/roadmaps'
import { useTutorEngine, type LiveSend, type QuizAnswerState } from '@/components/tutor/engine'
import { api, backendAvailable } from '@/services/api'
import { Blocks } from '@/components/tutor/blocks'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'
import { Ring } from '@/components/ui/Progress'
import { masteryTone } from '@/lib/tones'

function TutorAvatar() {
  return (
    <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-violet text-white shadow-(--shadow-soft)">
      <Sparkles size={14} />
    </span>
  )
}

function TypingBubble({ label }: { label: string }) {
  return (
    <div className="flex items-start gap-3">
      <TutorAvatar />
      <div className="flex items-center gap-2.5 rounded-2xl rounded-tl-md border bg-card px-4 py-3 shadow-(--shadow-soft)">
        <span className="flex gap-1">
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo [animation-delay:0.15s]" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo [animation-delay:0.3s]" />
        </span>
        <span className="text-[12.5px] font-medium text-ink-faint">{label}</span>
      </div>
    </div>
  )
}

function QuizCard({
  quiz,
  answer,
  onAnswer,
}: {
  quiz: InlineQuiz
  answer?: QuizAnswerState
  onAnswer: (selected: number) => void
}) {
  return (
    <div className="rounded-xl border border-indigo-soft bg-indigo-mist p-4">
      <div className="mb-2 flex items-center gap-1.5 text-[11.5px] font-bold tracking-wide text-indigo-ink uppercase">
        <Target size={12} /> Quick check
      </div>
      <div className="text-[14.5px] leading-relaxed font-medium">{quiz.question}</div>
      <div className="mt-3 space-y-2">
        {quiz.options.map((opt, i) => {
          const isSelected = answer?.selected === i
          const isCorrect = i === quiz.correct
          const showState = answer != null
          return (
            <button
              key={i}
              disabled={showState}
              onClick={() => onAnswer(i)}
              className={cn(
                'flex w-full items-center justify-between gap-3 rounded-lg border bg-card px-3.5 py-2.5 text-left text-[13.5px] font-medium transition-all duration-200',
                !showState && 'hover:-translate-y-px hover:border-indigo/50 hover:shadow-(--shadow-soft)',
                showState && isCorrect && 'border-mint bg-mint-soft text-mint-ink',
                showState && isSelected && !isCorrect && 'border-coral bg-coral-soft text-coral-ink',
                showState && !isSelected && !isCorrect && 'opacity-50',
              )}
            >
              {opt}
              {showState && isCorrect && <Check size={15} strokeWidth={3} className="shrink-0" />}
              {showState && isSelected && !isCorrect && <X size={15} strokeWidth={3} className="shrink-0" />}
            </button>
          )
        })}
      </div>
      {answer != null && (
        <div
          className={cn(
            'anim-fade mt-3 text-[12.5px] font-semibold',
            answer.correct ? 'text-mint-ink' : 'text-amber-ink',
          )}
        >
          {answer.correct ? 'Exactly right.' : 'You’re close — let’s look at this together.'}
        </div>
      )}
    </div>
  )
}

const explainOptions = [
  { id: 'simpler', label: 'Simpler', icon: Feather },
  { id: 'analogy', label: 'With an analogy', icon: Lightbulb },
  { id: 'real-world', label: 'Real-world', icon: Globe },
  { id: 'visual', label: 'Visual thinking', icon: Eye },
  { id: 'mathematical', label: 'Mathematical', icon: Sigma },
  { id: 'technical', label: 'Technical', icon: Wrench },
  { id: 'with-code', label: 'With code', icon: Code2 },
]

export default function TutorSession() {
  const { topicId = 'ask' } = useParams()
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const title = topicTitle(topicId)
  const {
    masteryOf,
    setMastery,
    completeMissionStep,
    setLastSessionTopic,
    toast,
    state,
    setMasteryMode,
  } = useApp()

  const mastery = masteryOf(topicId, topicId === 'precision-recall' ? 65 : 0)
  const showMastery = topicId !== 'ask'
  const [explainOpen, setExplainOpen] = useState(false)
  const [input, setInput] = useState('')
  const [masteryPulse, setMasteryPulse] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const prevMastery = useRef(mastery)

  const onEffect = useCallback(
    (e: ScriptEffect) => {
      if (e === 'learn-complete') {
        setMastery('precision-recall', 72)
        completeMissionStep('learn')
        setLastSessionTopic(topicId)
        toast('Mastery updated', 'Precision & Recall: 65% → 72%', 'mint')
        window.setTimeout(
          () => toast('Roadmap adapted', 'Next up: a short practice run to lock it in.', 'violet'),
          1400,
        )
      } else if (e === 'learn-partial') {
        setMastery('precision-recall', 69)
        completeMissionStep('learn')
        setLastSessionTopic(topicId)
        toast('Progress saved', 'Precision & Recall: 65% → 69% — practice will lift it further.', 'mint')
      } else if (e === 'session-done') {
        toast('Session saved', 'Tomorrow’s topic is queued: ROC Curves. 🌱', 'indigo')
      }
    },
    [completeMissionStep, setLastSessionTopic, setMastery, toast, topicId],
  )

  const onNavigateIntent = useCallback(
    (intent: string) => {
      switch (intent) {
        case 'go-practice':
          navigate('/quiz/precision-recall')
          break
        case 'go-quiz':
          navigate(`/quiz/${topicId}`)
          break
        case 'go-home':
          navigate('/')
          break
        case 'go-prep':
          navigate('/opportunities/hackathon-ai-ed/prepare')
          break
        case 'go-mission':
        case 'go-pr':
          navigate('/tutor/precision-recall')
          break
        case 'go-create':
          navigate('/roadmaps?create=1')
          break
        default:
          navigate('/')
      }
    },
    [navigate, topicId],
  )

  // Live tutor for free-text questions; silently unused when no backend is running.
  const sessionId = useRef<string | null>(null)
  const liveSend = useCallback<LiveSend>(async (text) => {
    if (!(await backendAvailable())) return null
    const res = await api.tutorMessage({
      sessionId: sessionId.current,
      topicId: topicId === 'ask' ? null : topicId,
      message: text,
    })
    sessionId.current = res.sessionId
    const blocks: TutorBlock[] = [{ kind: 'p', text: res.reply.text }]
    for (const c of res.reply.citations ?? []) {
      blocks.push({ kind: 'cite', label: `${c.title}${c.page != null ? ` · p.${c.page}` : ''}` })
    }
    return {
      blocks,
      chips: (res.reply.suggestions ?? []).slice(0, 3).map((label, i) => ({
        label,
        to: 'fallback',
        primary: i === 0,
      })),
    }
  }, [topicId])

  const engine = useTutorEngine({
    topicId,
    title,
    initialQuery: params.get('q') ?? undefined,
    onEffect,
    onNavigateIntent,
    liveSend,
  })

  // Auto-scroll on new content.
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [engine.messages, engine.typing])

  // Pulse the mastery chip when it changes.
  useEffect(() => {
    if (mastery !== prevMastery.current) {
      prevMastery.current = mastery
      setMasteryPulse((p) => p + 1)
    }
  }, [mastery])

  const lastTutorId = [...engine.messages].reverse().find((m) => m.role === 'tutor')?.id

  const submitText = () => {
    if (!input.trim()) return
    engine.sendText(input)
    setInput('')
  }

  const toggleMasteryMode = () => {
    const next = !state.masteryMode
    setMasteryMode(next)
    if (next) {
      engine.announce(
        'Mastery mode is on 🎯 I’ll keep checking understanding from different angles until you’re consistently above 85% — no rushing, no pressure, just steady reps.',
      )
    }
  }

  const backTo = topicId === 'what-is-rag' ? '/opportunities/hackathon-ai-ed/prepare' : topicId === 'ask' ? '/tutor' : '/roadmaps/ml'

  return (
    <div className="flex h-dvh flex-col">
      {/* Session header */}
      <header className="z-20 border-b bg-card/85 backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-[820px] items-center gap-3 px-4">
          <Link
            to={backTo}
            aria-label="Back"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-soft transition-colors hover:bg-paper-deep hover:text-ink"
          >
            <ArrowLeft size={17} />
          </Link>
          <div className="min-w-0 flex-1">
            <div className="truncate text-[14.5px] leading-tight font-semibold">{title}</div>
            <div className="truncate text-[11.5px] text-ink-faint">
              {topicId === 'ask'
                ? 'Your personal tutor · adapts to you'
                : topicId === 'what-is-rag'
                  ? 'RAG Systems · Hackathon prep'
                  : 'Machine Learning · Mission topic'}
            </div>
          </div>
          {showMastery && (
            <div
              key={masteryPulse}
              className={cn(
                'flex items-center gap-2 rounded-full border bg-card py-1 pr-3 pl-1.5',
                masteryPulse > 0 && 'anim-pop border-mint/60',
              )}
            >
              <Ring value={mastery} size={22} stroke={3.5} tone={masteryTone(mastery)} />
              <span className="text-[12px] font-bold tnum">
                {mastery}% <span className="hidden font-medium text-ink-faint sm:inline">mastery</span>
              </span>
            </div>
          )}
          <button
            onClick={toggleMasteryMode}
            aria-pressed={state.masteryMode}
            title="Teach me until I master it"
            className={cn(
              'hidden h-8 items-center gap-1.5 rounded-full border px-3 text-[12px] font-semibold transition-all sm:flex',
              state.masteryMode
                ? 'border-indigo bg-indigo text-white'
                : 'text-ink-soft hover:border-indigo/50 hover:text-indigo-ink',
            )}
          >
            <Target size={13} /> {state.masteryMode ? 'Mastery mode on' : 'Teach me until I master it'}
          </button>
        </div>
      </header>

      {/* Conversation */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-[820px] space-y-5 px-4 py-6">
          {engine.messages.map((m: ChatMsg) => (
            <div key={m.id} className="anim-in">
              {m.role === 'tutor' ? (
                <div className="flex items-start gap-3">
                  <TutorAvatar />
                  <div className="min-w-0 max-w-[calc(100%-3rem)] flex-1">
                    <div className="rounded-2xl rounded-tl-md border bg-card p-4 shadow-(--shadow-soft) lg:p-4.5">
                      {m.blocks != null && <Blocks blocks={m.blocks} />}
                      {m.quiz != null && (
                        <div className={cn(m.blocks?.length ? 'mt-3.5' : '')}>
                          <QuizCard
                            quiz={m.quiz}
                            answer={engine.quizAnswers[m.quiz.id]}
                            onAnswer={(i) => engine.answerQuiz(m.quiz!, i)}
                          />
                        </div>
                      )}
                    </div>
                    {m.chips != null && m.id === lastTutorId && engine.typing == null && (
                      <div className="anim-fade mt-2.5 flex flex-wrap gap-2">
                        {m.chips.map((chip) => (
                          <button
                            key={chip.label}
                            onClick={() => engine.sendChip(chip)}
                            className={cn(
                              'rounded-full border px-3.5 py-1.5 text-[13px] font-medium transition-all duration-150 active:scale-95',
                              chip.primary
                                ? 'border-indigo bg-indigo text-white hover:bg-indigo-deep'
                                : 'bg-card text-ink-soft hover:border-indigo/50 hover:text-indigo-ink',
                            )}
                          >
                            {chip.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-tr-md bg-indigo px-4 py-2.5 text-[14px] leading-relaxed text-white shadow-(--shadow-soft)">
                    {m.text}
                  </div>
                </div>
              )}
            </div>
          ))}
          {engine.typing != null && <TypingBubble label={engine.typing} />}
        </div>
      </div>

      {/* Input bar */}
      <div className="border-t bg-card/90 backdrop-blur">
        <div className="mx-auto w-full max-w-[820px] px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                onClick={() => setExplainOpen((o) => !o)}
                aria-expanded={explainOpen}
                className={cn(
                  'flex h-10 items-center gap-1.5 rounded-xl border px-3 text-[12.5px] font-semibold whitespace-nowrap transition-all',
                  explainOpen
                    ? 'border-indigo bg-indigo-soft text-indigo-ink'
                    : 'text-ink-soft hover:border-indigo/40 hover:text-indigo-ink',
                )}
              >
                <RefreshCw size={13} />
                <span className="hidden sm:inline">Explain differently</span>
              </button>
              {explainOpen && (
                <>
                  <button
                    aria-label="Close menu"
                    className="fixed inset-0 z-30 cursor-default"
                    onClick={() => setExplainOpen(false)}
                  />
                  <div className="anim-pop absolute bottom-full left-0 z-40 mb-2 w-52 rounded-xl border bg-card p-1.5 shadow-(--shadow-lift)">
                    {explainOptions.map((o) => (
                      <button
                        key={o.id}
                        onClick={() => {
                          setExplainOpen(false)
                          engine.jumpTo(o.id, `Explain it ${o.label.toLowerCase()}`)
                        }}
                        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-[13px] font-medium text-ink-soft transition-colors hover:bg-paper-deep hover:text-ink"
                      >
                        <o.icon size={14} className="text-indigo-ink" /> {o.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <div className="flex h-10 flex-1 items-center gap-1 rounded-xl border bg-paper px-2 transition-colors focus-within:border-indigo">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && submitText()}
                placeholder="Ask anything about this topic…"
                aria-label="Message your tutor"
                className="h-full min-w-0 flex-1 bg-transparent px-2 text-[14px] outline-none placeholder:text-ink-faint"
              />
              <button
                aria-label="Attach material"
                onClick={() => toast('Ground this chat', 'Add sources in your Notebook and I’ll cite them here.', 'indigo')}
                className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-faint transition-colors hover:bg-paper-deep hover:text-ink"
              >
                <Paperclip size={15} />
              </button>
              <button
                aria-label="Voice input"
                onClick={() => toast('Voice input', 'Voice conversations arrive with the full release.', 'indigo')}
                className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-faint transition-colors hover:bg-paper-deep hover:text-ink"
              >
                <Mic size={15} />
              </button>
            </div>

            <button
              onClick={submitText}
              aria-label="Send"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo text-white transition-all hover:bg-indigo-deep active:scale-95 disabled:opacity-40"
              disabled={!input.trim()}
            >
              <Send size={16} />
            </button>
          </div>
          <p className="mt-2 text-center text-[10.5px] text-ink-faint">
            Your tutor cites your sources where it can, and may make mistakes — verify anything important.
          </p>
        </div>
      </div>
    </div>
  )
}
