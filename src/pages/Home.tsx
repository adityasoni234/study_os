import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  BookOpenCheck,
  CalendarDays,
  Check,
  ChevronRight,
  Clock,
  Flame,
  Globe,
  MessageCircle,
  Play,
  Radar,
  Route,
  Sparkles,
  Target,
  Upload,
  Wind,
} from 'lucide-react'
import { Page } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, Eyebrow, SectionHeader } from '@/components/ui/Card'
import { ProgressBar, Ring } from '@/components/ui/Progress'
import { Badge } from '@/components/ui/Badge'
import { RoadmapIcon } from '@/lib/icons'
import { useApp } from '@/state/AppContext'
import { useAuth } from '@/state/AuthContext'
import { roadmaps } from '@/data/roadmaps'
import { opportunities } from '@/data/opportunities'
import { toneSoftBg, toneText } from '@/lib/tones'
import { cn, firstName, timeGreeting, todayLabel } from '@/lib/utils'

function Journeys() {
  const { state, roadmapProgress } = useApp()
  const visible = [
    ...(state.createdRoadmaps.includes('rag') ? [roadmaps.find((r) => r.id === 'rag')!] : []),
    ...roadmaps.filter((r) => r.id !== 'rag'),
  ].slice(0, 4)

  return (
    <section>
      <SectionHeader
        title="Your journeys"
        action={
          <Link
            to="/roadmaps"
            className="text-[12.5px] font-semibold text-indigo-ink transition-opacity hover:opacity-75"
          >
            See all
          </Link>
        }
      />
      <div className="space-y-2.5">
        {visible.map((r) => {
          const progress = roadmapProgress(r.id, r.baseProgress)
          return (
            <Link key={r.id} to={`/roadmaps/${r.id}`} className="block">
              <Card
                hover
                padded={false}
                className="flex items-center gap-4 px-4 py-3.5"
              >
                <span
                  className={cn(
                    'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl',
                    toneSoftBg[r.tone],
                    toneText[r.tone],
                  )}
                >
                  <RoadmapIcon name={r.icon} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-2">
                    <span className="truncate text-[14.5px] font-semibold">{r.title}</span>
                    {r.isNew && <Badge tone="amber">New</Badge>}
                  </span>
                  <span className="mt-0.5 block truncate text-[12.5px] text-ink-soft">
                    Next: {r.nextAction}
                  </span>
                </span>
                <span className="flex w-28 shrink-0 flex-col items-end gap-1.5">
                  <span className="text-[13px] font-bold tnum">{progress}%</span>
                  <ProgressBar value={progress} tone={r.tone} className="w-full" />
                </span>
                <ChevronRight size={16} className="shrink-0 text-ink-faint" />
              </Card>
            </Link>
          )
        })}
      </div>
    </section>
  )
}

function ContinueAndRecommended() {
  return (
    <section className="grid gap-4 sm:grid-cols-2">
      <div>
        <SectionHeader title="Continue learning" />
        <Link to="/tutor/confusion-matrix" className="block">
          <Card hover className="flex h-[108px] flex-col justify-between">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-[14.5px] font-semibold">Confusion Matrix</div>
                <div className="mt-0.5 text-[12.5px] text-ink-soft">
                  Yesterday · finished at 88%
                </div>
              </div>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-mint-soft text-mint-ink">
                <BookOpenCheck size={15} />
              </span>
            </div>
            <div className="text-[12.5px] font-semibold text-indigo-ink">Revisit session →</div>
          </Card>
        </Link>
      </div>
      <div>
        <SectionHeader title="Recommended for you" />
        <Link to="/tutor/logistic-regression" className="block">
          <Card hover className="flex h-[108px] flex-col justify-between">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-[14.5px] font-semibold">Review Logistic Regression</div>
                <div className="mt-0.5 text-[12.5px] text-ink-soft">
                  Mastery slipped 74% → 68% — 10 minutes brings it back
                </div>
              </div>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-soft text-amber-ink">
                <Flame size={15} />
              </span>
            </div>
            <div className="text-[12.5px] font-semibold text-indigo-ink">Quick review →</div>
          </Card>
        </Link>
      </div>
    </section>
  )
}

function QuickActions() {
  const navigate = useNavigate()
  const actions = [
    { label: 'Start learning', icon: Play, to: '/tutor/precision-recall' },
    { label: 'Upload material', icon: Upload, to: '/notebook?add=1' },
    { label: 'Create roadmap', icon: Route, to: '/roadmaps?create=1' },
    { label: 'Ask tutor', icon: MessageCircle, to: '/tutor' },
  ]
  return (
    <section>
      <SectionHeader title="Quick actions" />
      <div className="grid grid-cols-2 gap-2.5">
        {actions.map((a) => (
          <button
            key={a.label}
            onClick={() => navigate(a.to)}
            className="group flex flex-col items-start gap-2 rounded-xl border bg-card p-3.5 text-left shadow-(--shadow-soft) transition-all duration-200 hover:-translate-y-0.5 hover:border-indigo/35 hover:shadow-(--shadow-lift)"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] bg-indigo-soft text-indigo-ink transition-colors group-hover:bg-indigo group-hover:text-white">
              <a.icon size={15} />
            </span>
            <span className="text-[13px] leading-tight font-semibold">{a.label}</span>
          </button>
        ))}
      </div>
    </section>
  )
}

function OpportunityHighlight() {
  const opp = opportunities[0]
  return (
    <section>
      <SectionHeader
        title="Opportunity highlight"
        action={
          <Link
            to="/opportunities"
            className="text-[12.5px] font-semibold text-indigo-ink transition-opacity hover:opacity-75"
          >
            See all
          </Link>
        }
      />
      <Card hover className="relative">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <Badge tone="violet">{opp.type}</Badge>
            <div className="mt-2 text-[14.5px] leading-snug font-semibold">{opp.title}</div>
            <div className="mt-1 flex items-center gap-2 text-[12.5px] text-ink-soft">
              <CalendarDays size={13} /> Closes {opp.deadline} · {opp.daysLeft} days left
            </div>
          </div>
          <Ring value={opp.match} size={52} stroke={5} tone="mint">
            <span className="text-[11.5px] font-bold tnum">{opp.match}%</span>
          </Ring>
        </div>
        <p className="mt-2.5 text-[12.5px] leading-relaxed text-ink-soft">
          {opp.match}% match with your current learning — Python, ML and GenAI all check out.
        </p>
        <div className="mt-3.5 flex gap-2">
          <Link to={`/opportunities/${opp.id}/prepare`} className="flex-1">
            <Button size="sm" className="w-full">
              <Radar size={13} /> Prepare me
            </Button>
          </Link>
          <Link to="/opportunities">
            <Button size="sm" variant="secondary">
              View
            </Button>
          </Link>
        </div>
      </Card>
    </section>
  )
}

function WellbeingNudge() {
  return (
    <Link to="/wellbeing" className="block">
      <div className="rounded-2xl border border-sky-soft bg-sky-soft/50 p-4 transition-all duration-200 hover:border-sky/40">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-card text-sky-ink shadow-(--shadow-soft)">
            <Wind size={16} />
          </span>
          <div className="min-w-0">
            <div className="text-[13px] leading-snug font-semibold text-sky-ink">
              Long sessions this week
            </div>
            <div className="text-[12px] leading-snug text-ink-soft">
              A 2-minute reset keeps focus fresh →
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default function Home() {
  const { state } = useApp()
  const { user } = useAuth()
  const m = state.mission
  const allDone = m.learn && m.practice && m.check

  const cta = !m.learn
    ? { label: 'Continue Learning', to: '/tutor/precision-recall' }
    : !m.practice
      ? { label: 'Start practice — 5 questions', to: '/quiz/precision-recall' }
      : !m.check
        ? { label: 'Take the mastery check', to: '/quiz/precision-recall?mode=check' }
        : { label: 'Preview tomorrow: ROC Curves', to: '/roadmaps/ml' }

  return (
    <Page>
      <div className="mb-7 flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-[12.5px] font-medium text-ink-faint">{todayLabel()}</div>
          <h1 className="mt-1 font-display text-[25px] leading-tight font-semibold tracking-[-0.01em] sm:text-[28px] lg:text-[32px]">
            {timeGreeting()},{' '}
            <span className="whitespace-nowrap">
              {firstName(user?.name ?? 'Aditya')} <span className="inline-block">👋</span>
            </span>
          </h1>
          <p className="mt-1 text-[14.5px] text-ink-soft">
            {allDone ? 'Today’s mission is done — momentum looks great.' : 'Let’s make today count.'}
          </p>
        </div>
        <div className="hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-[12.5px] font-semibold text-amber-ink shadow-(--shadow-soft) sm:flex">
          <Flame size={13} /> 12-day streak
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="min-w-0 space-y-7">
          {/* Mission card with working CTA */}
          <div className="relative">
            <MissionCardShell ctaLabel={cta.label} ctaTo={cta.to} />
          </div>
          <Journeys />
          <ContinueAndRecommended />
        </div>
        <div className="space-y-6">
          <QuickActions />
          <OpportunityHighlight />
          <WellbeingNudge />
        </div>
      </div>

      <div className="mt-10 flex items-center justify-center gap-1.5 text-[11.5px] text-ink-faint">
        <Globe size={12} /> StudyOS supports UN Sustainable Development Goal 4 — Quality Education
      </div>
    </Page>
  )
}

/** Mission card with the CTA wired in (kept separate for readability). */
function MissionCardShell({ ctaLabel, ctaTo }: { ctaLabel: string; ctaTo: string }) {
  const { state, roadmapProgress } = useApp()
  const m = state.mission
  const stepsDone = [m.learn, m.practice, m.check].filter(Boolean).length
  const allDone = stepsDone === 3

  const steps = [
    { label: 'Learn the concept with your tutor', done: m.learn, minutes: '~12 min' },
    { label: 'Practice 5 questions', done: m.practice, minutes: '~8 min' },
    { label: 'Complete the mastery check', done: m.check, minutes: '~5 min' },
  ]

  return (
    <Card className="relative overflow-hidden p-6 lg:p-7">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full opacity-70"
        style={{
          background:
            'radial-gradient(circle, var(--color-indigo-mist) 0%, rgba(246,246,253,0) 70%)',
        }}
      />
      <div className="relative flex flex-wrap items-start justify-between gap-6">
        <div className="min-w-0 flex-1">
          <Eyebrow className="flex items-center gap-1.5 text-indigo-ink">
            <Target size={13} /> Today’s mission
          </Eyebrow>
          <h2 className="mt-2 font-display text-[24px] leading-tight font-semibold lg:text-[27px]">
            Precision &amp; Recall
          </h2>
          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[13px] font-medium text-ink-soft">
            <span>Machine Learning · Classification Metrics</span>
            <span className="inline-flex items-center gap-1 text-ink-faint">
              <Clock size={13} /> 25 min total
            </span>
          </div>

          <ul className="mt-5 space-y-2.5">
            {steps.map((s, i) => {
              const isNext = !s.done && steps.slice(0, i).every((x) => x.done)
              return (
                <li key={s.label} className="flex items-center gap-3">
                  <span
                    className={cn(
                      'flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-300',
                      s.done
                        ? 'border-mint bg-mint text-white'
                        : isNext
                          ? 'border-indigo bg-card'
                          : 'border-line-strong bg-card',
                    )}
                  >
                    {s.done ? (
                      <Check size={13} strokeWidth={3} />
                    ) : isNext ? (
                      <span className="h-2 w-2 rounded-full bg-indigo" />
                    ) : null}
                  </span>
                  <span
                    className={cn(
                      'flex-1 text-[14px]',
                      s.done ? 'text-ink-faint line-through decoration-line-strong' : 'font-medium',
                    )}
                  >
                    {s.label}
                  </span>
                  <span className="hidden text-[12px] text-ink-faint sm:block">{s.minutes}</span>
                </li>
              )
            })}
          </ul>
        </div>

        <div className="flex flex-col items-center gap-1.5 self-center">
          <Ring value={(stepsDone / 3) * 100} size={76} stroke={7} tone={allDone ? 'mint' : 'indigo'}>
            <span className="text-[15px] font-bold tnum">{stepsDone}/3</span>
          </Ring>
          <span className="text-[11.5px] font-medium text-ink-faint">
            {allDone ? 'Complete' : 'steps done'}
          </span>
        </div>
      </div>

      <div className="relative mt-6">
        <Link to={ctaTo}>
          <Button size="lg" variant={allDone ? 'mint' : 'primary'}>
            {ctaLabel} <ArrowRight size={16} />
          </Button>
        </Link>
      </div>

      <div className="relative mt-4 flex items-start gap-2 rounded-xl bg-violet-soft/70 px-3.5 py-2.5 text-[12.5px] leading-snug text-violet-ink">
        <Sparkles size={14} className="mt-0.5 shrink-0" />
        {allDone ? (
          <span>
            Mission complete — beautifully done. Your Machine Learning roadmap moved to{' '}
            <strong className="font-semibold">{roadmapProgress('ml', 68)}%</strong>, and tomorrow
            starts with ROC curves.
          </span>
        ) : (
          <span>
            Adapted for you — recall questions tripped you up on Tuesday, so today’s session starts
            with a quick recap before new material.
          </span>
        )}
      </div>
    </Card>
  )
}
