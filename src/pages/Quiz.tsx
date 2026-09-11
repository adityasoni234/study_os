import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronRight,
  Lightbulb,
  PenLine,
  Sparkles,
  Target,
  TrendingUp,
  X,
} from 'lucide-react'
import { Page } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, Eyebrow } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ProgressBar, Ring } from '@/components/ui/Progress'
import { Segmented } from '@/components/ui/Segmented'
import { questionsFor } from '@/data/quiz'
import { topicTitle } from '@/data/roadmaps'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'
import type { QuizQuestion } from '@/types'

type Phase = 'setup' | 'generating' | 'running' | 'results'

const genLines = [
  'Preparing your quiz…',
  'Tailoring difficulty to your level…',
  'Weighting the areas you missed recently…',
]

export default function Quiz() {
  const { topicId = 'precision-recall' } = useParams()
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const mode: 'practice' | 'check' = params.get('mode') === 'check' ? 'check' : 'practice'
  const title = topicTitle(topicId)
  const { masteryOf, setMastery, completeMissionStep, recordQuiz, toast } = useApp()

  const [phase, setPhase] = useState<Phase>('setup')
  const [difficulty, setDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>(
    mode === 'check' ? 'Hard' : 'Medium',
  )
  const [length, setLength] = useState<'5' | '10' | '15'>('5')
  const [focus, setFocus] = useState<'Concepts' | 'Applications' | 'Mixed'>('Mixed')
  const [genLine, setGenLine] = useState(0)

  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [answers, setAnswers] = useState<boolean[]>([])

  const startQuiz = useCallback(() => {
    setPhase('generating')
    setGenLine(0)
  }, [])

  useEffect(() => {
    if (phase !== 'generating') return
    const t1 = window.setTimeout(() => setGenLine(1), 700)
    const t2 = window.setTimeout(() => setGenLine(2), 1400)
    const t3 = window.setTimeout(() => {
      setQuestions(questionsFor(topicId, mode))
      setIndex(0)
      setSelected(null)
      setAnswers([])
      setPhase('running')
    }, 2100)
    return () => [t1, t2, t3].forEach(clearTimeout)
  }, [phase, topicId, mode])

  const question = questions[index]
  const answered = selected != null
  const isLast = index === questions.length - 1

  const choose = useCallback(
    (i: number) => {
      if (answered || !question) return
      setSelected(i)
      setAnswers((a) => [...a, i === question.correct])
    },
    [answered, question],
  )

  const next = useCallback(() => {
    if (isLast) {
      setPhase('results')
    } else {
      setIndex((i) => i + 1)
      setSelected(null)
    }
  }, [isLast])

  // Keyboard: 1–4 to answer, Enter to continue.
  useEffect(() => {
    if (phase !== 'running') return
    const onKey = (e: KeyboardEvent) => {
      if (!answered && ['1', '2', '3', '4'].includes(e.key)) {
        choose(Number(e.key) - 1)
      } else if (answered && e.key === 'Enter') {
        next()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [phase, answered, choose, next])

  const score = answers.filter(Boolean).length

  // Tag breakdown for the results screen.
  const tagStats = useMemo(() => {
    const map = new Map<string, { right: number; total: number }>()
    questions.forEach((q, i) => {
      const s = map.get(q.tag) ?? { right: 0, total: 0 }
      s.total += 1
      if (answers[i]) s.right += 1
      map.set(q.tag, s)
    })
    return [...map.entries()].map(([tag, s]) => ({ tag, ...s, pct: s.right / s.total }))
  }, [questions, answers])

  // Record results once.
  useEffect(() => {
    if (phase !== 'results') return
    const pct = score / questions.length
    const weak = tagStats.filter((t) => t.pct < 1).map((t) => t.tag)
    recordQuiz({ topicId, topicTitle: title, mode, score, total: questions.length, weakTags: weak })

    if (topicId === 'precision-recall') {
      if (mode === 'practice') {
        completeMissionStep('practice')
        const newMastery = pct >= 0.8 ? 78 : pct >= 0.6 ? 75 : 72
        setMastery('precision-recall', newMastery)
        toast('Mastery updated', `Precision & Recall is now ${newMastery}%`, 'mint')
        window.setTimeout(
          () => toast('Roadmap adapted', 'One step left today: the mastery check.', 'violet'),
          1400,
        )
      } else {
        if (pct >= 0.66) {
          completeMissionStep('check')
          setMastery('precision-recall', 82)
          toast('Mission complete 🎉', 'Precision & Recall reached 82% — ROC Curves unlocks tomorrow.', 'mint')
        } else {
          toast('Almost there', 'A short review will get you across the line.', 'amber')
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase])

  const strongest = tagStats.length ? [...tagStats].sort((a, b) => b.pct - a.pct)[0] : null
  const weakest = tagStats.length ? [...tagStats].sort((a, b) => a.pct - b.pct)[0] : null

  return (
    <Page className="max-w-[760px]">
      {phase === 'setup' && (
        <div className="anim-in">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 inline-flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft transition-colors hover:text-ink"
          >
            <ArrowLeft size={15} /> Back
          </button>
          <Card className="p-6 lg:p-7">
            <Eyebrow className="flex items-center gap-1.5 text-indigo-ink">
              {mode === 'check' ? <Target size={13} /> : <PenLine size={13} />}
              {mode === 'check' ? 'Mastery check' : 'Practice quiz'}
            </Eyebrow>
            <h1 className="mt-2 font-display text-[24px] leading-tight font-semibold">{title}</h1>
            <p className="mt-1 text-[13.5px] text-ink-soft">
              {mode === 'check'
                ? '3 harder questions to confirm today’s concept is locked in. ~4 minutes.'
                : 'Drawn from your roadmap and your sources — weighted toward what you missed recently.'}
            </p>

            {mode === 'practice' && (
              <div className="mt-6 space-y-5">
                <div>
                  <div className="mb-1.5 text-[13px] font-semibold">Difficulty</div>
                  <Segmented
                    options={[
                      { value: 'Easy', label: 'Easy' },
                      { value: 'Medium', label: 'Medium' },
                      { value: 'Hard', label: 'Hard' },
                    ]}
                    value={difficulty}
                    onChange={setDifficulty}
                  />
                </div>
                <div>
                  <div className="mb-1.5 text-[13px] font-semibold">Length</div>
                  <Segmented
                    options={[
                      { value: '5', label: '5 questions' },
                      { value: '10', label: '10' },
                      { value: '15', label: '15' },
                    ]}
                    value={length}
                    onChange={setLength}
                  />
                </div>
                <div>
                  <div className="mb-1.5 text-[13px] font-semibold">Focus</div>
                  <Segmented
                    options={[
                      { value: 'Concepts', label: 'Concepts' },
                      { value: 'Applications', label: 'Applications' },
                      { value: 'Mixed', label: 'Mixed' },
                    ]}
                    value={focus}
                    onChange={setFocus}
                  />
                </div>
              </div>
            )}

            <Button size="lg" className="mt-7 w-full sm:w-auto" onClick={startQuiz}>
              {mode === 'check' ? 'Begin mastery check' : 'Start quiz'} <ArrowRight size={16} />
            </Button>
          </Card>
        </div>
      )}

      {phase === 'generating' && (
        <div className="flex min-h-[50vh] items-center justify-center">
          <div className="space-y-3.5">
            {genLines.map((l, i) => (
              <div
                key={l}
                className={cn(
                  'flex items-center gap-3 text-[14.5px] transition-all duration-300',
                  i <= genLine ? 'opacity-100' : 'opacity-25',
                )}
              >
                <span
                  className={cn(
                    'flex h-6 w-6 items-center justify-center rounded-full',
                    i < genLine ? 'bg-mint text-white' : 'bg-indigo-soft',
                  )}
                >
                  {i < genLine ? (
                    <Check size={13} strokeWidth={3} />
                  ) : (
                    <span className="flex gap-0.5">
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo" />
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo [animation-delay:0.15s]" />
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo [animation-delay:0.3s]" />
                    </span>
                  )}
                </span>
                {l}
              </div>
            ))}
          </div>
        </div>
      )}

      {phase === 'running' && question != null && (
        <div className="anim-in" key={question.id}>
          <div className="mb-5 flex items-center justify-between gap-4">
            <div className="text-[13px] font-semibold text-ink-soft">
              Question {index + 1} <span className="text-ink-faint">of {questions.length}</span>
            </div>
            <div className="flex items-center gap-3">
              <ProgressBar
                value={((index + (answered ? 1 : 0)) / questions.length) * 100}
                className="w-32"
              />
              <button
                onClick={() => navigate(-1)}
                aria-label="Exit quiz"
                className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-faint transition-colors hover:bg-paper-deep hover:text-ink"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          <Card className="p-6">
            <h2 className="text-[17px] leading-relaxed font-semibold">{question.prompt}</h2>
            <div className="mt-5 space-y-2.5">
              {question.options.map((opt, i) => {
                const isCorrect = i === question.correct
                const isSelected = selected === i
                return (
                  <button
                    key={i}
                    disabled={answered}
                    onClick={() => choose(i)}
                    className={cn(
                      'flex w-full items-center gap-3.5 rounded-xl border bg-card px-4 py-3.5 text-left text-[14px] font-medium transition-all duration-200',
                      !answered && 'hover:-translate-y-px hover:border-indigo/50 hover:shadow-(--shadow-soft)',
                      answered && isCorrect && 'border-mint bg-mint-soft text-mint-ink',
                      answered && isSelected && !isCorrect && 'border-coral bg-coral-soft text-coral-ink',
                      answered && !isSelected && !isCorrect && 'opacity-45',
                    )}
                  >
                    <span
                      className={cn(
                        'flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11.5px] font-bold',
                        answered && isCorrect
                          ? 'border-mint bg-mint text-white'
                          : answered && isSelected
                            ? 'border-coral bg-coral text-white'
                            : 'border-line-strong text-ink-faint',
                      )}
                    >
                      {answered && isCorrect ? (
                        <Check size={12} strokeWidth={3.5} />
                      ) : answered && isSelected ? (
                        <X size={12} strokeWidth={3.5} />
                      ) : (
                        i + 1
                      )}
                    </span>
                    {opt}
                  </button>
                )
              })}
            </div>

            {answered && (
              <div
                className={cn(
                  'anim-in mt-4 rounded-xl p-4',
                  selected === question.correct ? 'bg-mint-soft' : 'bg-amber-soft',
                )}
              >
                <div
                  className={cn(
                    'flex items-center gap-1.5 text-[13px] font-bold',
                    selected === question.correct ? 'text-mint-ink' : 'text-amber-ink',
                  )}
                >
                  <Lightbulb size={13} />
                  {selected === question.correct ? 'Right — here’s why' : 'Not quite — here’s the idea'}
                </div>
                <p className="mt-1 text-[13.5px] leading-relaxed text-ink-soft">
                  {question.explanation}
                </p>
              </div>
            )}
          </Card>

          {answered && (
            <div className="anim-fade mt-4 flex justify-end">
              <Button onClick={next}>
                {isLast ? 'See results' : 'Next question'} <ChevronRight size={15} />
              </Button>
            </div>
          )}
          <p className="mt-3 text-center text-[11px] text-ink-faint">
            Tip: press 1–4 to answer, Enter to continue
          </p>
        </div>
      )}

      {phase === 'results' && (
        <div className="anim-in">
          <Card className="p-7 text-center">
            <Eyebrow>{mode === 'check' ? 'Mastery check complete' : 'Quiz complete'}</Eyebrow>
            <div className="mt-5 flex justify-center">
              <Ring
                value={(score / questions.length) * 100}
                size={128}
                stroke={10}
                tone={score / questions.length >= 0.66 ? 'mint' : 'amber'}
              >
                <div>
                  <div className="text-[28px] leading-none font-bold tnum">
                    {score}
                    <span className="text-[16px] text-ink-faint">/{questions.length}</span>
                  </div>
                </div>
              </Ring>
            </div>
            <h2 className="mt-4 font-display text-[22px] font-semibold">
              {score === questions.length
                ? 'Flawless, Aditya.'
                : score / questions.length >= 0.66
                  ? 'Nice work, Aditya.'
                  : 'Good effort — almost there.'}
            </h2>
            {topicId === 'precision-recall' && (
              <div className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-mint-soft px-3.5 py-1.5 text-[13px] font-semibold text-mint-ink">
                <TrendingUp size={14} /> Mastery now {masteryOf('precision-recall', 65)}%
              </div>
            )}

            <div className="mx-auto mt-6 grid max-w-md gap-2.5 text-left">
              {strongest != null && strongest.pct === 1 && (
                <div className="flex items-center justify-between rounded-xl bg-mint-soft/70 px-4 py-2.5">
                  <span className="text-[13px] font-semibold text-mint-ink">Strong</span>
                  <span className="text-[13px] text-ink-soft">{strongest.tag}</span>
                </div>
              )}
              {tagStats
                .filter((t) => t.pct < 1 && t.pct >= 0.5 && t.tag !== weakest?.tag)
                .map((t) => (
                  <div key={t.tag} className="flex items-center justify-between rounded-xl bg-sky-soft/70 px-4 py-2.5">
                    <span className="text-[13px] font-semibold text-sky-ink">Improving</span>
                    <span className="text-[13px] text-ink-soft">{t.tag}</span>
                  </div>
                ))}
              {weakest != null && weakest.pct < 1 && (
                <div className="flex items-center justify-between rounded-xl bg-amber-soft/70 px-4 py-2.5">
                  <span className="text-[13px] font-semibold text-amber-ink">Needs practice</span>
                  <span className="text-[13px] text-ink-soft">{weakest.tag}</span>
                </div>
              )}
            </div>

            <p className="mt-5 text-[13px] text-ink-soft">
              <Sparkles size={12} className="mr-1 inline text-violet-ink" />
              {mode === 'check'
                ? 'This result feeds your roadmap — tomorrow starts exactly where you need it to.'
                : 'Your roadmap and knowledge map are updated with this result.'}
            </p>

            <div className="mt-6 flex flex-col justify-center gap-2.5 sm:flex-row">
              {mode === 'practice' && topicId === 'precision-recall' ? (
                <>
                  <Link to="/quiz/precision-recall?mode=check">
                    <Button className="w-full sm:w-auto">
                      <Target size={15} /> Take the mastery check
                    </Button>
                  </Link>
                  <Link to="/">
                    <Button variant="secondary" className="w-full sm:w-auto">
                      Back to Home
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/">
                    <Button className="w-full sm:w-auto">Back to Home</Button>
                  </Link>
                  <Link to="/roadmaps/ml">
                    <Button variant="secondary" className="w-full sm:w-auto">
                      View roadmap
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </Card>
        </div>
      )}
    </Page>
  )
}
