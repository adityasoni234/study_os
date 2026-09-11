import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CalendarDays,
  Check,
  Clock,
  GraduationCap,
  Play,
  Sparkles,
} from 'lucide-react'
import { Page } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, Eyebrow } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Ring } from '@/components/ui/Progress'
import { getOpportunity, prepPlans } from '@/data/opportunities'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'

const genLines = [
  'Reading the requirements…',
  'Mapping them to your strengths…',
  'Building your 6-day plan…',
]

export default function PrepareMe() {
  const { id = 'hackathon-ai-ed' } = useParams()
  const navigate = useNavigate()
  const opp = getOpportunity(id) ?? getOpportunity('hackathon-ai-ed')!
  const plan = prepPlans[opp.id] ?? prepPlans['hackathon-ai-ed']
  const { state, startPrep, togglePrepTask, toast } = useApp()

  const [loading, setLoading] = useState(!state.prepStarted)
  const [genLine, setGenLine] = useState(0)

  useEffect(() => {
    if (!loading) return
    const t1 = window.setTimeout(() => setGenLine(1), 750)
    const t2 = window.setTimeout(() => setGenLine(2), 1500)
    const t3 = window.setTimeout(() => setLoading(false), 2350)
    return () => [t1, t2, t3].forEach(clearTimeout)
  }, [loading])

  const totalTasks = plan.reduce((a, d) => a + d.tasks.length, 0)
  const doneTasks = plan.reduce(
    (a, d) => a + d.tasks.filter((_, i) => state.prepTasks[`${opp.id}-${d.day}-${i}`]).length,
    0,
  )

  const begin = () => {
    startPrep()
    toast('Preparation started', 'Added to your roadmaps — I’ll pace it alongside your mission.', 'mint')
  }

  if (loading) {
    return (
      <Page className="max-w-[720px]">
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="space-y-3.5">
            {genLines.map((l, i) => (
              <div
                key={l}
                className={cn(
                  'flex items-center gap-3 text-[14.5px] transition-opacity duration-300',
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
      </Page>
    )
  }

  return (
    <Page>
      <Link
        to="/opportunities"
        className="mb-4 inline-flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft transition-colors hover:text-ink"
      >
        <ArrowLeft size={15} /> Opportunity Radar
      </Link>

      <div className="mb-7 flex flex-wrap items-start justify-between gap-5">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={opp.tone}>{opp.type}</Badge>
            {opp.daysLeft != null && (
              <Badge tone="amber">
                <CalendarDays size={10} /> {opp.daysLeft} days remaining
              </Badge>
            )}
          </div>
          <h1 className="mt-2 font-display text-[24px] leading-tight font-semibold lg:text-[28px]">
            {opp.title}
          </h1>
          <p className="mt-1 text-[13.5px] text-ink-soft">
            A day-by-day preparation plan, built around what you already know.
          </p>
        </div>
        {state.prepStarted ? (
          <div className="flex items-center gap-2 rounded-full border border-mint/40 bg-mint-soft px-4 py-2 text-[13px] font-semibold text-mint-ink">
            <Check size={14} strokeWidth={3} /> Preparation active · {doneTasks}/{totalTasks} tasks
          </div>
        ) : (
          <Button size="lg" onClick={begin}>
            <Play size={15} /> Start preparation
          </Button>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        <div className="space-y-3.5">
          {plan.map((day) => {
            const dayDone = day.tasks.every((_, i) => state.prepTasks[`${opp.id}-${day.day}-${i}`])
            return (
              <Card key={day.day} className={cn('transition-colors', dayDone && 'border-mint/40 bg-mint-soft/30')}>
                <div className="flex items-start gap-4">
                  <span
                    className={cn(
                      'flex h-11 w-11 shrink-0 flex-col items-center justify-center rounded-xl text-center',
                      dayDone ? 'bg-mint text-white' : 'bg-indigo-soft text-indigo-ink',
                    )}
                  >
                    {dayDone ? (
                      <Check size={17} strokeWidth={3} />
                    ) : (
                      <>
                        <span className="text-[9px] leading-none font-bold uppercase">Day</span>
                        <span className="text-[16px] leading-tight font-bold tnum">{day.day}</span>
                      </>
                    )}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-[15px] font-semibold">{day.title}</h3>
                      <span className="inline-flex items-center gap-1 text-[11.5px] font-medium text-ink-faint">
                        <Clock size={11.5} /> ~{day.minutes} min
                      </span>
                    </div>
                    <ul className="mt-2.5 space-y-1.5">
                      {day.tasks.map((task, i) => {
                        const key = `${opp.id}-${day.day}-${i}`
                        const checked = state.prepTasks[key] === true
                        return (
                          <li key={key}>
                            <button
                              onClick={() => togglePrepTask(key)}
                              className="group flex w-full items-center gap-2.5 rounded-lg px-1.5 py-1 text-left transition-colors hover:bg-paper-deep/60"
                            >
                              <span
                                className={cn(
                                  'flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-[5px] border-2 transition-all',
                                  checked
                                    ? 'border-mint bg-mint text-white'
                                    : 'border-line-strong group-hover:border-indigo',
                                )}
                              >
                                {checked && <Check size={11} strokeWidth={3.5} />}
                              </span>
                              <span
                                className={cn(
                                  'text-[13.5px]',
                                  checked ? 'text-ink-faint line-through decoration-line-strong' : 'text-ink',
                                )}
                              >
                                {task}
                              </span>
                            </button>
                          </li>
                        )
                      })}
                    </ul>
                    {day.note != null && (
                      <div className="mt-2.5 rounded-lg bg-violet-soft/70 px-3 py-2 text-[12px] leading-snug text-violet-ink">
                        <Sparkles size={11} className="mr-1 inline" /> {day.note}
                      </div>
                    )}
                    {day.tutorLink != null && (
                      <Link
                        to={`/tutor/${day.tutorLink}`}
                        className="mt-2.5 inline-flex items-center gap-1.5 rounded-full border border-indigo/40 bg-indigo-soft px-3 py-1.5 text-[12px] font-semibold text-indigo-ink transition-all hover:bg-indigo hover:text-white"
                      >
                        <GraduationCap size={13} /> Open with Tutor
                      </Link>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>

        <aside className="space-y-4">
          <Card className="text-center">
            <Eyebrow>Readiness today</Eyebrow>
            <div className="mt-3 flex justify-center">
              <Ring value={72 + Math.round((doneTasks / totalTasks) * 25)} size={96} stroke={8} tone="indigo">
                <span className="text-[19px] font-bold tnum">
                  {72 + Math.round((doneTasks / totalTasks) * 25)}%
                </span>
              </Ring>
            </div>
            <p className="mt-3 text-[12.5px] leading-relaxed text-ink-soft">
              Your Python (86%) and ML fundamentals already cover most of Days 1 and 3.
            </p>
          </Card>

          <Card className="border-violet-soft bg-violet-soft/40">
            <div className="flex items-center gap-1.5 text-[12.5px] font-bold text-violet-ink">
              <Sparkles size={13} /> Personalised for you
            </div>
            <p className="mt-1.5 text-[12.5px] leading-relaxed text-ink-soft">
              RAG is the one skill you haven’t met yet, so Day 2 is lighter everywhere else and
              starts with a gentle tutor session. Everything you do here also advances your{' '}
              <strong className="font-semibold text-ink">AI Engineer</strong> roadmap.
            </p>
          </Card>

          {!state.prepStarted && (
            <Button className="w-full" size="lg" onClick={begin}>
              <Play size={15} /> Start preparation
            </Button>
          )}
          {state.prepStarted && (
            <Link to="/tutor/what-is-rag" className="block">
              <Button className="w-full" size="lg" variant="soft">
                <GraduationCap size={15} /> Begin Day 2 with Tutor
              </Button>
            </Link>
          )}
          <button
            onClick={() => toast('Reminders on', 'I’ll nudge you each morning until the deadline.', 'indigo')}
            className="w-full text-center text-[12.5px] font-semibold text-ink-faint transition-colors hover:text-ink"
          >
            + Add daily reminders
          </button>
        </aside>
      </div>
    </Page>
  )
}
