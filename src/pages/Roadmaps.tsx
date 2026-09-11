import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import {
  ArrowRight,
  CalendarDays,
  Check,
  Crosshair,
  Plus,
  Sparkles,
} from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ProgressBar } from '@/components/ui/Progress'
import { PillTabs } from '@/components/ui/Tabs'
import { Modal } from '@/components/ui/Modal'
import { Segmented } from '@/components/ui/Segmented'
import { RoadmapIcon } from '@/lib/icons'
import { roadmaps } from '@/data/roadmaps'
import { useApp } from '@/state/AppContext'
import { toneSoftBg, toneText } from '@/lib/tones'
import { cn } from '@/lib/utils'
import type { RoadmapType } from '@/types'

const filters: { id: string; label: string }[] = [
  { id: 'All', label: 'All' },
  { id: 'Subject', label: 'Subjects' },
  { id: 'Topic', label: 'Topics' },
  { id: 'Career', label: 'Careers' },
  { id: 'Exam', label: 'Exams' },
  { id: 'Skill', label: 'Skills' },
  { id: 'Personal', label: 'Personal' },
]

const generationSteps = [
  'Analyzing your goal…',
  'Mapping prerequisites against what you already know…',
  'Sequencing 6 topics across 3 milestones…',
  'Scheduling around your 5 hours a week…',
]

function CreateRoadmapModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [step, setStep] = useState(0)
  const [goal, setGoal] = useState('Master Retrieval-Augmented Generation (RAG)')
  const [type, setType] = useState<RoadmapType>('Topic')
  const [level, setLevel] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner')
  const [hours, setHours] = useState<'2h' | '5h' | '8h'>('5h')
  const [deadline, setDeadline] = useState('Sep 18 — before the hackathon')
  const [genStep, setGenStep] = useState(-1)
  const { createRoadmap, toast } = useApp()
  const navigate = useNavigate()

  useEffect(() => {
    if (step !== 2) return
    setGenStep(0)
    const timers = generationSteps.map((_, i) =>
      window.setTimeout(() => setGenStep(i + 1), 650 * (i + 1)),
    )
    const done = window.setTimeout(() => setStep(3), 650 * generationSteps.length + 500)
    return () => {
      timers.forEach(clearTimeout)
      clearTimeout(done)
    }
  }, [step])

  const finish = () => {
    createRoadmap('rag')
    toast('Roadmap created', 'RAG Systems is ready — sequenced for your Sep 18 deadline.', 'mint')
    onClose()
    setStep(0)
    navigate('/roadmaps/rag')
  }

  return (
    <Modal open={open} onClose={onClose} title="Create a roadmap" wide>
      {step === 0 && (
        <div className="space-y-5">
          <div>
            <label className="mb-1.5 block text-[13px] font-semibold" htmlFor="goal">
              What do you want to achieve?
            </label>
            <input
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="h-11 w-full rounded-xl border bg-paper px-4 text-[14.5px] outline-none transition-colors focus:border-indigo"
              placeholder="e.g. Master RAG, prepare for GATE, become a data analyst…"
            />
          </div>
          <div>
            <div className="mb-1.5 text-[13px] font-semibold">What kind of goal is this?</div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              {(['Subject', 'Topic', 'Career', 'Exam', 'Skill', 'Personal'] as RoadmapType[]).map(
                (t) => (
                  <button
                    key={t}
                    onClick={() => setType(t)}
                    className={cn(
                      'rounded-xl border px-3 py-2.5 text-[13px] font-medium transition-all duration-150',
                      type === t
                        ? 'border-indigo bg-indigo-soft text-indigo-ink'
                        : 'bg-card text-ink-soft hover:border-line-strong',
                    )}
                  >
                    {t}
                  </button>
                ),
              )}
            </div>
          </div>
          <div className="flex justify-end">
            <Button onClick={() => setStep(1)}>
              Continue <ArrowRight size={15} />
            </Button>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-5">
          <div>
            <div className="mb-1.5 text-[13px] font-semibold">Your current level</div>
            <Segmented
              options={[
                { value: 'Beginner', label: 'Beginner' },
                { value: 'Intermediate', label: 'Intermediate' },
                { value: 'Advanced', label: 'Advanced' },
              ]}
              value={level}
              onChange={setLevel}
            />
          </div>
          <div>
            <div className="mb-1.5 text-[13px] font-semibold">Time you can give each week</div>
            <Segmented
              options={[
                { value: '2h', label: '2 hours' },
                { value: '5h', label: '5 hours' },
                { value: '8h', label: '8+ hours' },
              ]}
              value={hours}
              onChange={setHours}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-[13px] font-semibold" htmlFor="deadline">
              Target or deadline <span className="font-normal text-ink-faint">(optional)</span>
            </label>
            <input
              id="deadline"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="h-11 w-full rounded-xl border bg-paper px-4 text-[14.5px] outline-none transition-colors focus:border-indigo"
            />
          </div>
          <div className="rounded-xl bg-violet-soft/60 px-3.5 py-2.5 text-[12.5px] text-violet-ink">
            <Sparkles size={13} className="mr-1.5 inline" />
            I already know your strengths — Python 86%, ML fundamentals 68% — so the plan will skip
            what you’ve mastered.
          </div>
          <div className="flex justify-between">
            <Button variant="ghost" onClick={() => setStep(0)}>
              Back
            </Button>
            <Button onClick={() => setStep(2)}>
              Generate my roadmap <Sparkles size={15} />
            </Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="py-6">
          <div className="mx-auto max-w-sm space-y-3.5">
            {generationSteps.map((s, i) => (
              <div
                key={s}
                className={cn(
                  'flex items-center gap-3 text-[14px] transition-all duration-300',
                  i <= genStep ? 'opacity-100' : 'opacity-30',
                )}
              >
                <span
                  className={cn(
                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full transition-colors',
                    i < genStep
                      ? 'bg-mint text-white'
                      : i === genStep
                        ? 'bg-indigo-soft'
                        : 'bg-paper-deep',
                  )}
                >
                  {i < genStep ? (
                    <Check size={13} strokeWidth={3} />
                  ) : i === genStep ? (
                    <span className="flex gap-0.5">
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo" />
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo [animation-delay:0.15s]" />
                      <span className="typing-dot h-1 w-1 rounded-full bg-indigo [animation-delay:0.3s]" />
                    </span>
                  ) : null}
                </span>
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-mint-soft text-mint-ink">
              <Check size={18} strokeWidth={3} />
            </span>
            <div>
              <div className="text-[15.5px] font-semibold">Your RAG Systems roadmap is ready</div>
              <div className="text-[12.5px] text-ink-soft">
                6 topics · 3 milestones · paced for {deadline || 'your schedule'}
              </div>
            </div>
          </div>
          <div className="space-y-1.5 rounded-xl border bg-paper p-4">
            {['Core Ideas — What is RAG, Embeddings, Vector Search', 'Making It Good — Chunking, Grounding & Citations', 'Build It — a mini RAG app for the hackathon'].map(
              (m, i) => (
                <div key={m} className="flex items-center gap-2.5 text-[13.5px]">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-soft text-[11px] font-bold text-indigo-ink">
                    {i + 1}
                  </span>
                  {m}
                </div>
              ),
            )}
          </div>
          <div className="flex justify-end">
            <Button onClick={finish}>
              Open my roadmap <ArrowRight size={15} />
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}

export default function Roadmaps() {
  const [params, setParams] = useSearchParams()
  const [filter, setFilter] = useState('All')
  const [createOpen, setCreateOpen] = useState(params.get('create') === '1')
  const { state, roadmapProgress } = useApp()

  useEffect(() => {
    if (params.get('create') === '1') {
      setCreateOpen(true)
      params.delete('create')
      setParams(params, { replace: true })
    }
  }, [params, setParams])

  const list = useMemo(() => {
    const base = roadmaps.filter((r) => r.id !== 'rag' || state.createdRoadmaps.includes('rag'))
    const sorted = [...base].sort((a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0))
    return filter === 'All' ? sorted : sorted.filter((r) => r.type === filter)
  }, [filter, state.createdRoadmaps])

  return (
    <Page>
      <PageHeader
        title="My Roadmaps"
        sub="Every goal becomes a guided path — adaptive, paced to your life, and connected to your tutor."
        right={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus size={16} /> Create Roadmap
          </Button>
        }
      />

      <PillTabs tabs={filters} active={filter} onChange={setFilter} className="mb-6" />

      {list.length === 0 ? (
        <div className="flex flex-col items-center rounded-2xl border border-dashed border-line-strong bg-paper-deep/40 px-6 py-14 text-center">
          <div className="text-[15px] font-semibold">Ready to build your learning path?</div>
          <p className="mt-1 text-[13.5px] text-ink-soft">
            No {filter.toLowerCase()} roadmaps yet — describe the goal and I’ll structure the rest.
          </p>
          <Button className="mt-4" onClick={() => setCreateOpen(true)}>
            <Plus size={15} /> Create my roadmap
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {list.map((r) => {
            const progress = roadmapProgress(r.id, r.baseProgress)
            return (
              <Link key={r.id} to={`/roadmaps/${r.id}`} className="block">
                <Card hover className="flex h-full flex-col">
                  <div className="flex items-start justify-between gap-3">
                    <span
                      className={cn(
                        'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl',
                        toneSoftBg[r.tone],
                        toneText[r.tone],
                      )}
                    >
                      <RoadmapIcon name={r.icon} size={20} />
                    </span>
                    <div className="flex items-center gap-1.5">
                      {r.isNew && <Badge tone="amber">New</Badge>}
                      <Badge tone={r.tone}>{r.type}</Badge>
                    </div>
                  </div>
                  <h3 className="mt-3 text-[16.5px] leading-snug font-semibold">{r.title}</h3>
                  <p className="mt-1 line-clamp-1 text-[13px] text-ink-soft">{r.goal}</p>

                  <div className="mt-4 flex items-center gap-3">
                    <ProgressBar value={progress} tone={r.tone} className="flex-1" />
                    <span className="text-[13px] font-bold tnum">{progress}%</span>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t pt-3.5 text-[12.5px] text-ink-soft">
                    <span className="inline-flex items-center gap-1.5">
                      <CalendarDays size={13} className="text-ink-faint" /> {r.targetDate}
                    </span>
                    <span className="inline-flex items-center gap-1.5">
                      <Crosshair size={13} className="text-ink-faint" /> {r.focus}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-[12.5px]">
                    <span className="text-ink-soft">
                      Next: <span className="font-medium text-ink">{r.nextAction}</span>
                    </span>
                    <span className="font-semibold text-indigo-ink">Continue →</span>
                  </div>
                </Card>
              </Link>
            )
          })}
        </div>
      )}

      <CreateRoadmapModal open={createOpen} onClose={() => setCreateOpen(false)} />
    </Page>
  )
}
