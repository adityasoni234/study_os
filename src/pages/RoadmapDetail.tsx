import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  BookOpen,
  CalendarDays,
  Check,
  ChevronRight,
  Clock,
  GraduationCap,
  ListChecks,
  Lock,
  PenLine,
  RotateCcw,
  Sparkles,
} from 'lucide-react'
import { Page } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, Eyebrow } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ProgressBar, Ring } from '@/components/ui/Progress'
import { Modal } from '@/components/ui/Modal'
import { RoadmapIcon } from '@/lib/icons'
import { getRoadmap } from '@/data/roadmaps'
import { useApp } from '@/state/AppContext'
import { masteryTone, toneSoftBg, toneText } from '@/lib/tones'
import { cn } from '@/lib/utils'
import type { TopicNode, TopicStatus } from '@/types'

function NodeDot({ status }: { status: TopicStatus }) {
  if (status === 'done')
    return (
      <span className="z-10 flex h-6 w-6 items-center justify-center rounded-full bg-mint text-white">
        <Check size={13} strokeWidth={3.5} />
      </span>
    )
  if (status === 'current')
    return (
      <span className="pulse-ring z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 border-indigo bg-card">
        <span className="h-2 w-2 rounded-full bg-indigo" />
      </span>
    )
  if (status === 'review')
    return (
      <span className="z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 border-amber bg-amber-soft">
        <RotateCcw size={11} className="text-amber-ink" strokeWidth={3} />
      </span>
    )
  return (
    <span className="z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 border-dashed border-line-strong bg-paper">
      <Lock size={10} className="text-ink-faint" />
    </span>
  )
}

function statusLabel(status: TopicStatus): { text: string; tone: 'mint' | 'indigo' | 'amber' | 'neutral' } {
  switch (status) {
    case 'done':
      return { text: 'Completed', tone: 'mint' }
    case 'current':
      return { text: 'You are here', tone: 'indigo' }
    case 'review':
      return { text: 'Needs review', tone: 'amber' }
    default:
      return { text: 'Upcoming', tone: 'neutral' }
  }
}

function TopicPanel({ topic, mastery, onNavigate }: { topic: TopicNode; mastery: number; onNavigate: (to: string) => void }) {
  const label = statusLabel(topic.status)
  const locked = topic.status === 'locked'
  const recommended =
    topic.status === 'current'
      ? 'Learn this with your tutor — about ' + topic.minutes + ' minutes at your pace.'
      : topic.status === 'review'
        ? 'A short review session will lift this back above 75%.'
        : topic.status === 'done'
          ? 'Mastered. Revisit any time, or keep momentum going forward.'
          : 'Unlocks after the current topic — no skipping needed, you’ll be there soon.'

  return (
    <div className="anim-pop" key={topic.id}>
      <Badge tone={label.tone}>{label.text}</Badge>
      <h3 className="mt-2.5 text-[18px] leading-snug font-semibold">{topic.title}</h3>
      <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink-soft">{topic.summary}</p>

      <div className="mt-4 flex items-center gap-4 rounded-xl border bg-paper p-3.5">
        <Ring value={mastery} size={54} stroke={5} tone={masteryTone(mastery)}>
          <span className="text-[12px] font-bold tnum">{mastery}%</span>
        </Ring>
        <div>
          <div className="text-[13px] font-semibold">Mastery</div>
          <div className="text-[12px] text-ink-soft">
            <Clock size={11} className="mr-1 inline" />
            {topic.minutes} min estimated
          </div>
        </div>
      </div>

      {topic.note != null && (
        <div className="mt-3 rounded-xl bg-amber-soft/70 px-3.5 py-2.5 text-[12.5px] leading-snug text-amber-ink">
          {topic.note}
        </div>
      )}

      <div className="mt-4">
        <Eyebrow>Recommended</Eyebrow>
        <p className="mt-1 text-[13px] leading-relaxed text-ink-soft">{recommended}</p>
      </div>

      <div className="mt-4 space-y-2">
        <Button
          className="w-full"
          disabled={locked}
          onClick={() => onNavigate(`/tutor/${topic.id}`)}
        >
          <GraduationCap size={16} /> Learn with Tutor
        </Button>
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="secondary"
            disabled={locked}
            onClick={() => onNavigate(`/quiz/${topic.id}`)}
          >
            <PenLine size={14} /> Practice
          </Button>
          <Button
            variant="ghost"
            disabled={locked}
            onClick={() => onNavigate(`/tutor/${topic.id}`)}
          >
            <RotateCcw size={14} /> Review
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function RoadmapDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const roadmap = getRoadmap(id ?? '')
  const { state, masteryOf, roadmapProgress } = useApp()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)

  const allTopics = useMemo(
    () => (roadmap ? roadmap.milestones.flatMap((m) => m.topics) : []),
    [roadmap],
  )

  if (!roadmap) {
    return (
      <Page>
        <div className="py-20 text-center">
          <div className="text-[16px] font-semibold">This roadmap wandered off the map.</div>
          <Link to="/roadmaps" className="mt-2 inline-block text-[13.5px] font-semibold text-indigo-ink">
            ← Back to roadmaps
          </Link>
        </div>
      </Page>
    )
  }

  const progress = roadmapProgress(roadmap.id, roadmap.baseProgress)
  const doneCount = allTopics.filter((t) => t.status === 'done').length
  const selected = allTopics.find((t) => t.id === selectedId) ?? null
  const masteryFor = (t: TopicNode) =>
    t.id === 'precision-recall' ? masteryOf('precision-recall', t.mastery) : t.mastery

  const select = (t: TopicNode) => {
    setSelectedId(t.id)
    if (window.innerWidth < 1024) setSheetOpen(true)
  }

  return (
    <Page>
      <Link
        to="/roadmaps"
        className="mb-4 inline-flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft transition-colors hover:text-ink"
      >
        <ArrowLeft size={15} /> All roadmaps
      </Link>

      <div className="mb-7 flex flex-wrap items-start justify-between gap-5">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <span
              className={cn(
                'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl',
                toneSoftBg[roadmap.tone],
                toneText[roadmap.tone],
              )}
            >
              <RoadmapIcon name={roadmap.icon} size={20} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display text-[24px] leading-tight font-semibold lg:text-[28px]">
                  {roadmap.title}
                </h1>
                <Badge tone={roadmap.tone}>{roadmap.type}</Badge>
              </div>
              <p className="mt-0.5 text-[13.5px] text-ink-soft">{roadmap.goal}</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-[13px] text-ink-soft">
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays size={14} className="text-ink-faint" /> Target: {roadmap.targetDate}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <ListChecks size={14} className="text-ink-faint" /> {doneCount} of {allTopics.length}{' '}
              topics complete
            </span>
          </div>
        </div>

        <div className="flex items-center gap-5">
          <div className="flex flex-col items-center gap-1">
            <Ring value={progress} size={64} stroke={6} tone={roadmap.tone}>
              <span className="text-[13.5px] font-bold tnum">{progress}%</span>
            </Ring>
            <span className="text-[11px] font-medium text-ink-faint">progress</span>
          </div>
          <Button onClick={() => navigate(`/tutor/${roadmap.nextTopicId}`)}>
            Continue learning <ChevronRight size={15} />
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Journey timeline */}
        <div className="min-w-0">
          {roadmap.milestones.map((milestone, mi) => (
            <section key={milestone.id} className={cn(mi > 0 && 'mt-8')}>
              <div className="mb-3 flex items-center gap-2.5">
                <span
                  className={cn(
                    'flex h-7 w-7 items-center justify-center rounded-lg text-[11.5px] font-bold',
                    milestone.status === 'done'
                      ? 'bg-mint-soft text-mint-ink'
                      : milestone.status === 'current'
                        ? 'bg-indigo-soft text-indigo-ink'
                        : 'bg-paper-deep text-ink-faint',
                  )}
                >
                  {milestone.status === 'done' ? <Check size={13} strokeWidth={3} /> : mi + 1}
                </span>
                <h2 className="text-[13px] font-bold tracking-[0.06em] text-ink-soft uppercase">
                  {milestone.title}
                </h2>
                <span className="text-[11.5px] text-ink-faint">
                  {milestone.topics.filter((t) => t.status === 'done').length}/
                  {milestone.topics.length}
                </span>
              </div>

              <ol className="relative ml-3 space-y-3 border-l-2 border-line pl-7">
                {milestone.topics.map((topic) => {
                  const m = masteryFor(topic)
                  const isSelected = selectedId === topic.id
                  return (
                    <li key={topic.id} className="relative">
                      <span className="absolute top-3.5 -left-[41px]">
                        <NodeDot status={topic.status} />
                      </span>
                      <button
                        onClick={() => select(topic)}
                        className={cn(
                          'w-full rounded-xl border bg-card p-4 text-left shadow-(--shadow-soft) transition-all duration-200',
                          'hover:-translate-y-px hover:border-indigo/40 hover:shadow-(--shadow-lift)',
                          isSelected && 'border-indigo ring-2 ring-indigo/15',
                          topic.status === 'locked' && 'opacity-70',
                        )}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="flex items-center gap-2 text-[14.5px] font-semibold">
                            {topic.title}
                            {topic.status === 'current' && (
                              <Badge tone="indigo" className="hidden sm:inline-flex">
                                You are here
                              </Badge>
                            )}
                            {topic.status === 'review' && (
                              <Badge tone="amber" className="hidden sm:inline-flex">
                                Review
                              </Badge>
                            )}
                          </span>
                          {topic.status !== 'locked' && (
                            <span className="text-[12.5px] font-bold text-ink-soft tnum">{m}%</span>
                          )}
                        </div>
                        {topic.status !== 'locked' && (
                          <ProgressBar value={m} tone={masteryTone(m)} className="mt-2.5" />
                        )}
                        <div className="mt-2 line-clamp-1 text-[12.5px] text-ink-soft">
                          {topic.summary}
                        </div>
                        {topic.subtopics != null && topic.status === 'current' && (
                          <div className="mt-3 flex flex-wrap gap-1.5">
                            {topic.subtopics.map((s) => (
                              <span
                                key={s.title}
                                className={cn(
                                  'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11.5px] font-medium',
                                  s.state === 'done' && 'bg-mint-soft text-mint-ink',
                                  s.state === 'current' && 'bg-indigo-soft text-indigo-ink',
                                  s.state === 'next' && 'bg-paper-deep text-ink-faint',
                                )}
                              >
                                {s.state === 'done' && <Check size={10} strokeWidth={3.5} />}
                                {s.state === 'current' && (
                                  <span className="h-1.5 w-1.5 rounded-full bg-indigo" />
                                )}
                                {s.title}
                              </span>
                            ))}
                          </div>
                        )}
                      </button>
                    </li>
                  )
                })}
              </ol>
            </section>
          ))}
        </div>

        {/* Contextual panel (desktop) */}
        <aside className="hidden lg:block">
          <Card className="sticky top-6">
            {selected ? (
              <TopicPanel
                topic={selected}
                mastery={masteryFor(selected)}
                onNavigate={(to) => navigate(to)}
              />
            ) : (
              <div>
                <Eyebrow className="flex items-center gap-1.5 text-violet-ink">
                  <Sparkles size={12} /> Adaptive plan
                </Eyebrow>
                <p className="mt-2 text-[13.5px] leading-relaxed text-ink-soft">
                  {roadmap.adaptedNote ??
                    'This roadmap adapts as you learn — strong quiz results accelerate it, and shaky ones add gentle review stops.'}
                </p>
                <div className="mt-4 space-y-2 border-t pt-4">
                  {(
                    [
                      ['Completed', 'done', 'bg-mint'],
                      ['Current focus', 'current', 'bg-indigo'],
                      ['Needs review', 'review', 'bg-amber'],
                      ['Upcoming', 'locked', 'bg-line-strong'],
                    ] as const
                  ).map(([label, , dot]) => (
                    <div key={label} className="flex items-center gap-2.5 text-[12.5px] text-ink-soft">
                      <span className={cn('h-2.5 w-2.5 rounded-full', dot)} />
                      {label}
                    </div>
                  ))}
                </div>
                <div className="mt-4 border-t pt-4 text-[12.5px] text-ink-soft">
                  <BookOpen size={13} className="mr-1.5 inline text-ink-faint" />
                  Select any topic to see what it covers and jump straight into learning.
                </div>
              </div>
            )}
          </Card>
        </aside>
      </div>

      {/* Mobile bottom sheet */}
      <Modal open={sheetOpen} onClose={() => setSheetOpen(false)} title={undefined}>
        {selected && (
          <TopicPanel
            topic={selected}
            mastery={masteryFor(selected)}
            onNavigate={(to) => {
              setSheetOpen(false)
              navigate(to)
            }}
          />
        )}
      </Modal>
    </Page>
  )
}
