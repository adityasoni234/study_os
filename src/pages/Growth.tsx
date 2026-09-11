import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ArrowUpRight,
  ChevronDown,
  Flame,
  GraduationCap,
  PenLine,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { useState } from 'react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Card, SectionHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ProgressBar, Ring } from '@/components/ui/Progress'
import { dimensions, knowledgeMap, weekMinutes } from '@/data/growth'
import { RoadmapIcon } from '@/lib/icons'
import { useApp } from '@/state/AppContext'
import { masteryTone, toneSoftBg, toneText } from '@/lib/tones'
import { cn } from '@/lib/utils'

function Dimensions() {
  const { state } = useApp()
  const learnBoost = (state.mission.learn ? 1 : 0) + (state.mission.practice ? 1 : 0) + (state.mission.check ? 1 : 0)
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      {dimensions.map((d, i) => {
        const value = d.id === 'learning' ? d.value + learnBoost : d.value
        const delta = d.id === 'learning' ? d.delta + learnBoost : d.delta
        return (
          <Card key={d.id} className={cn('anim-in flex flex-col items-center py-5', `anim-d-${i + 1}`)}>
            <Ring value={value} size={72} stroke={6.5} tone={d.tone}>
              <span className="text-[15px] font-bold tnum">{value}%</span>
            </Ring>
            <div className="mt-2.5 text-[13.5px] font-semibold">{d.label}</div>
            <div className="mt-0.5 flex items-center gap-1 text-[11.5px] font-semibold text-mint-ink">
              <ArrowUpRight size={11} /> +{delta} this week
            </div>
          </Card>
        )
      })}
    </div>
  )
}

function Momentum() {
  const max = Math.max(...weekMinutes.map((d) => d.minutes), 1)
  const total = weekMinutes.reduce((a, b) => a + b.minutes, 0)
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-1.5 text-[14.5px] font-semibold">
            Strong momentum <Flame size={15} className="text-amber" />
          </div>
          <div className="mt-0.5 text-[12.5px] text-ink-soft">
            {Math.floor(total / 60)}h {total % 60}m this week · 12-day streak
          </div>
        </div>
      </div>
      <div className="mt-5 flex h-24 items-end justify-between gap-2">
        {weekMinutes.map((d) => (
          <div key={d.day} className="flex flex-1 flex-col items-center gap-1.5">
            <div className="flex h-16 w-full items-end">
              <div
                className={cn(
                  'w-full rounded-md transition-all duration-700',
                  d.minutes > 0 ? 'bg-indigo/80' : 'bg-paper-deep',
                )}
                style={{ height: `${Math.max((d.minutes / max) * 100, 6)}%` }}
                title={`${d.day}: ${d.minutes} min`}
              />
            </div>
            <span className="text-[10.5px] font-semibold text-ink-faint">{d.day}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}

function Insights() {
  const { masteryOf } = useApp()
  const pr = masteryOf('precision-recall', 65)
  const items = [
    {
      label: 'Strongest area',
      title: 'Regression',
      desc: '92% mastery — rock solid for two weeks straight.',
      tone: 'mint' as const,
      action: { label: 'Build on it', to: '/roadmaps/ml' },
    },
    {
      label: 'Recent improvement',
      title: 'Precision & Recall',
      desc: `Up from 65% to ${pr}% ${pr > 65 ? 'after today’s session' : '— today’s mission topic'}.`,
      tone: 'violet' as const,
      action: { label: 'Continue', to: '/tutor/precision-recall' },
    },
    {
      label: 'Needs attention',
      title: 'Neural Networks',
      desc: '41% — it unlocks your Deep Learning milestone next month.',
      tone: 'amber' as const,
      action: { label: 'Gentle start', to: '/tutor/perceptrons' },
    },
  ]
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {items.map((it) => (
        <Card key={it.title} className="flex flex-col">
          <span className={cn('self-start rounded-full px-2.5 py-0.5 text-[11px] font-bold', toneSoftBg[it.tone], toneText[it.tone])}>
            {it.label}
          </span>
          <div className="mt-2.5 text-[15px] font-semibold">{it.title}</div>
          <p className="mt-1 flex-1 text-[12.5px] leading-relaxed text-ink-soft">{it.desc}</p>
          <Link to={it.action.to} className="mt-3 text-[12.5px] font-semibold text-indigo-ink transition-opacity hover:opacity-70">
            {it.action.label} →
          </Link>
        </Card>
      ))}
    </div>
  )
}

function KnowledgeMapSection() {
  const [open, setOpen] = useState<string>('ml')
  const { masteryOf } = useApp()

  return (
    <Card padded={false}>
      {knowledgeMap.map((area) => {
        const isOpen = open === area.id
        const avg = Math.round(
          area.topics.reduce(
            (a, t) => a + (t.masteryKey ? masteryOf(t.masteryKey, t.mastery) : t.mastery),
            0,
          ) / area.topics.length,
        )
        return (
          <div key={area.id} className="border-b last:border-b-0">
            <button
              onClick={() => setOpen(isOpen ? '' : area.id)}
              aria-expanded={isOpen}
              className="flex w-full items-center gap-3.5 px-5 py-4 text-left transition-colors hover:bg-paper-deep/40"
            >
              <span className={cn('flex h-10 w-10 items-center justify-center rounded-xl', toneSoftBg[area.tone], toneText[area.tone])}>
                <RoadmapIcon name={area.icon} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="text-[14.5px] font-semibold">{area.title}</span>
                <span className="ml-2.5 text-[12px] font-medium text-ink-faint tnum">{avg}% average</span>
              </span>
              <ChevronDown size={16} className={cn('text-ink-faint transition-transform duration-300', isOpen && 'rotate-180')} />
            </button>
            <div className={cn('grid transition-all duration-300', isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0')}>
              <div className="overflow-hidden">
                <div className="space-y-1 px-5 pb-4">
                  {area.topics.map((t) => {
                    const value = t.masteryKey ? masteryOf(t.masteryKey, t.mastery) : t.mastery
                    const changed = t.masteryKey != null && value !== t.mastery
                    return (
                      <div key={t.id} className="group flex items-center gap-4 rounded-xl px-3 py-2.5 transition-colors hover:bg-paper-deep/50">
                        <span className="w-44 shrink-0 truncate text-[13.5px] font-medium">
                          {t.title}
                          {changed && (
                            <span className="ml-2 inline-flex items-center gap-0.5 text-[10.5px] font-bold text-mint-ink">
                              <TrendingUp size={10} /> updated
                            </span>
                          )}
                        </span>
                        <ProgressBar value={value} tone={masteryTone(value)} className="flex-1" />
                        <span className="w-10 text-right text-[12.5px] font-bold text-ink-soft tnum">{value}%</span>
                        <span className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                          <Link
                            to={`/tutor/${t.tutorId}`}
                            aria-label={`Learn ${t.title}`}
                            className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-soft text-indigo-ink transition-colors hover:bg-indigo hover:text-white"
                          >
                            <GraduationCap size={13} />
                          </Link>
                          <Link
                            to={`/quiz/${t.tutorId}`}
                            aria-label={`Practice ${t.title}`}
                            className="flex h-7 w-7 items-center justify-center rounded-lg bg-paper-deep text-ink-soft transition-colors hover:bg-ink hover:text-paper"
                          >
                            <PenLine size={13} />
                          </Link>
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </Card>
  )
}

export default function Growth() {
  return (
    <Page>
      <PageHeader
        title="Your Growth"
        sub="A calm look at how you’re moving forward — progress and momentum, never a score."
      />

      <Dimensions />

      <div className="mt-7 grid gap-4 lg:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          <SectionHeader title="This week" className="mb-0" />
          <Momentum />
          <Insights />
        </div>
        <div className="space-y-4">
          <SectionHeader title="Recommended next step" className="mb-0" />
          <Card className="relative overflow-hidden">
            <div
              aria-hidden
              className="pointer-events-none absolute -top-14 -right-14 h-44 w-44 rounded-full opacity-80"
              style={{ background: 'radial-gradient(circle, var(--color-indigo-mist) 0%, transparent 70%)' }}
            />
            <div className="relative">
              <div className="flex items-center gap-1.5 text-[12px] font-bold text-violet-ink">
                <Sparkles size={13} /> Chosen for you
              </div>
              <h3 className="mt-2 text-[16px] leading-snug font-semibold">
                20 minutes on Neural Network basics
              </h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-ink-soft">
                It’s your lowest area (41%) and it unlocks the Deep Learning milestone — plus the
                research internship on your radar asks for it.
              </p>
              <Link to="/tutor/perceptrons" className="mt-4 inline-block">
                <Button size="sm">
                  Start with your tutor <ArrowRight size={14} />
                </Button>
              </Link>
            </div>
          </Card>
          <Card className="bg-paper-deep/50">
            <div className="text-[13px] leading-relaxed text-ink-soft">
              <Sparkles size={12} className="mr-1.5 inline text-violet-ink" />
              Growth here means direction, not grades — every number is just “where next”, never a
              judgment.
            </div>
          </Card>
        </div>
      </div>

      <div className="mt-7">
        <SectionHeader
          title="Knowledge map"
          action={<span className="text-[12px] text-ink-faint">tap a topic → learn or practice</span>}
        />
        <KnowledgeMapSection />
      </div>
    </Page>
  )
}
