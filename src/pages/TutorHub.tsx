import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  ChevronRight,
  Clock,
  GraduationCap,
  RotateCcw,
  Send,
  Sparkles,
  Target,
} from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Card, SectionHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Ring } from '@/components/ui/Progress'
import { useApp } from '@/state/AppContext'
import { masteryTone } from '@/lib/tones'

const suggestions = [
  'Explain gradient descent simply',
  'What is overfitting?',
  'How do neural networks learn?',
]

const recentSessions = [
  { id: 'confusion-matrix', title: 'Confusion Matrix', when: 'Yesterday', result: 'Finished at 88%' },
  { id: 'linear-regression', title: 'Linear Regression', when: 'Monday', result: 'Mastered · 92%' },
  { id: 'stats', title: 'Statistics Essentials', when: 'Last week', result: 'Mastered · 88%' },
]

export default function TutorHub() {
  const [question, setQuestion] = useState('')
  const navigate = useNavigate()
  const { masteryOf } = useApp()
  const prMastery = masteryOf('precision-recall', 65)

  const ask = (q: string) => {
    if (!q.trim()) return
    navigate(`/tutor/ask?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <Page>
      <PageHeader
        title="1:1 Tutor"
        sub="A personal teacher who explains, questions, adapts to your level — and remembers how you learn."
      />

      {/* Ask anything */}
      <Card className="relative overflow-hidden p-6">
        <div
          aria-hidden
          className="pointer-events-none absolute -top-20 -right-20 h-60 w-60 rounded-full opacity-70"
          style={{
            background: 'radial-gradient(circle, var(--color-violet-soft) 0%, rgba(242,238,253,0) 70%)',
          }}
        />
        <div className="relative">
          <div className="flex items-center gap-2 text-[13px] font-semibold text-violet-ink">
            <Sparkles size={14} /> Ask me anything
          </div>
          <div className="mt-3 flex items-center gap-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && ask(question)}
              placeholder="What would you like to understand today?"
              aria-label="Ask your tutor"
              className="h-12 min-w-0 flex-1 rounded-xl border bg-paper px-4 text-[14.5px] outline-none transition-colors focus:border-indigo"
            />
            <button
              onClick={() => ask(question)}
              disabled={!question.trim()}
              aria-label="Ask"
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo text-white transition-all hover:bg-indigo-deep active:scale-95 disabled:opacity-40"
            >
              <Send size={17} />
            </button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => ask(s)}
                className="rounded-full border bg-card px-3 py-1.5 text-[12.5px] font-medium text-ink-soft transition-all hover:border-indigo/50 hover:text-indigo-ink"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </Card>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section>
          <SectionHeader title="Pick up where you left off" />
          <div className="space-y-3">
            <Link to="/tutor/precision-recall" className="block">
              <Card hover className="flex items-center gap-4">
                <Ring value={prMastery} size={52} stroke={5} tone={masteryTone(prMastery)}>
                  <span className="text-[11.5px] font-bold tnum">{prMastery}%</span>
                </Ring>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[15px] font-semibold">Precision &amp; Recall</span>
                    <Badge tone="indigo">
                      <Target size={10} /> Mission
                    </Badge>
                  </div>
                  <div className="mt-0.5 flex items-center gap-1.5 text-[12.5px] text-ink-soft">
                    <Clock size={12} /> ~12 min to finish the concept
                  </div>
                </div>
                <ArrowRight size={17} className="shrink-0 text-indigo-ink" />
              </Card>
            </Link>
            <Link to="/tutor/logistic-regression" className="block">
              <Card hover className="flex items-center gap-4">
                <Ring value={68} size={52} stroke={5} tone="amber">
                  <span className="text-[11.5px] font-bold tnum">68%</span>
                </Ring>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[15px] font-semibold">Logistic Regression</span>
                    <Badge tone="amber">
                      <RotateCcw size={10} /> Review
                    </Badge>
                  </div>
                  <div className="mt-0.5 text-[12.5px] text-ink-soft">
                    Slipping since last week — 10 minutes brings it back
                  </div>
                </div>
                <ArrowRight size={17} className="shrink-0 text-indigo-ink" />
              </Card>
            </Link>
          </div>
        </section>

        <section>
          <SectionHeader title="Recent sessions" />
          <Card padded={false} className="divide-y">
            {recentSessions.map((s) => (
              <Link
                key={s.id}
                to={`/tutor/${s.id}`}
                className="flex items-center gap-3.5 px-4 py-3.5 transition-colors first:rounded-t-2xl last:rounded-b-2xl hover:bg-paper-deep/50"
              >
                <span className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-indigo-soft text-indigo-ink">
                  <GraduationCap size={16} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-[14px] font-semibold">{s.title}</span>
                  <span className="block text-[12px] text-ink-faint">
                    {s.when} · {s.result}
                  </span>
                </span>
                <ChevronRight size={15} className="text-ink-faint" />
              </Link>
            ))}
          </Card>
          <p className="mt-3 px-1 text-[12px] leading-relaxed text-ink-faint">
            <Sparkles size={11} className="mr-1 inline text-violet-ink" />
            I adapt each session to your level, your pace, and the explanation styles that have
            worked for you before.
          </p>
        </section>
      </div>
    </Page>
  )
}
