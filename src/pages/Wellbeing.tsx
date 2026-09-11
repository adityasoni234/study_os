import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CalendarDays,
  Check,
  HeartHandshake,
  MessageCircle,
  Send,
  Sparkles,
  Wind,
} from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, SectionHeader } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { useApp } from '@/state/AppContext'
import { cn, uid } from '@/lib/utils'

const moods = [
  { emoji: '😊', label: 'Great' },
  { emoji: '🙂', label: 'Good' },
  { emoji: '😐', label: 'Okay' },
  { emoji: '😔', label: 'Difficult' },
  { emoji: '😣', label: 'Overwhelming' },
]

function PlanHelper() {
  const { state, applyLighterPlan, toast } = useApp()
  return (
    <Card className="anim-in border-indigo-soft">
      <div className="text-[14px] font-semibold">Your week, honestly</div>
      <p className="mt-1 text-[13px] leading-relaxed text-ink-soft">
        Mission topic + 6-day hackathon prep + a review queue. That’s a lot for one week — here’s a
        lighter path that keeps everything on track:
      </p>
      <ul className="mt-3 space-y-2">
        {[
          'Move the mastery check to Saturday morning — your best time, by your history',
          'Split hackathon prep into two 25-minute blocks instead of one long evening',
          'Keep the streak alive on busy days with 5 minutes of flashcards, nothing more',
        ].map((s) => (
          <li key={s} className="flex gap-2.5 text-[13px] leading-relaxed text-ink-soft">
            <CalendarDays size={14} className="mt-[3px] shrink-0 text-indigo-ink" />
            {s}
          </li>
        ))}
      </ul>
      {state.planAdjusted ? (
        <div className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-mint-soft px-3.5 py-1.5 text-[12.5px] font-semibold text-mint-ink">
          <Check size={13} strokeWidth={3} /> Applied — tomorrow is lighter
        </div>
      ) : (
        <Button
          size="sm"
          className="mt-4"
          onClick={() => {
            applyLighterPlan()
            toast('Plan adjusted', 'Tomorrow is lighter. Your streak and deadlines are safe.', 'mint')
          }}
        >
          Apply the lighter plan
        </Button>
      )}
    </Card>
  )
}

interface TalkMsg {
  id: string
  role: 'user' | 'ai'
  text: string
}

const talkResponses: Record<string, string> = {
  'Exams are stressing me out':
    'That makes complete sense — exams compress months of effort into a few hours, and your mind knows the stakes. Two things that genuinely help: first, your preparation is more solid than stress lets you feel (your mastery has climbed steadily for 12 days straight). Second, try studying in 25-minute blocks with real breaks — stress shrinks when the task shrinks. Would a lighter plan for this week help?',
  "I can't focus today":
    'Some days are like that, and forcing it usually backfires. Honest suggestion: do one tiny thing — a 5-minute flashcard run — and then decide. Momentum usually follows action, not the other way round. And if it doesn’t today, that’s okay too; the streak survives a light day.',
  'I feel behind everyone else':
    'That feeling is real, and it’s also not evidence. You’re comparing your inside view with everyone else’s highlight reel. Here’s your actual data: 12-day streak, regression mastered at 92%, and you moved a hard topic up 7 points today. Behind isn’t what that looks like. One steady step at a time is exactly how this works.',
  'Just tired':
    'Then rest is the productive choice tonight. Learning consolidates during sleep — an early night literally helps your mastery. Tomorrow’s mission will be right here, and I’ll keep it light to restart gently.',
}

function SupportChat() {
  const [messages, setMessages] = useState<TalkMsg[]>([
    {
      id: 'w-1',
      role: 'ai',
      text: 'I’m here. What’s on your mind? — I’m a study companion, not a therapist, so for serious distress please reach out to someone you trust or a professional. For everything study-shaped, let’s talk.',
    },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)

  const send = (text: string) => {
    const t = text.trim()
    if (!t) return
    setMessages((m) => [...m, { id: uid('w'), role: 'user', text: t }])
    setInput('')
    setTyping(true)
    window.setTimeout(() => {
      setTyping(false)
      const reply =
        talkResponses[t] ??
        'Thank you for saying that out loud — naming it is genuinely half the work. Whatever this is, it doesn’t change the direction you’re moving. Want to take a two-minute reset together, or would a lighter plan for the week help more?'
      setMessages((m) => [...m, { id: uid('w'), role: 'ai', text: reply }])
    }, 1300)
  }

  const remaining = Object.keys(talkResponses).filter(
    (q) => !messages.some((m) => m.text === q),
  )

  return (
    <Card className="anim-in border-mint-soft p-0">
      <div className="max-h-[380px] space-y-3.5 overflow-y-auto p-4">
        {messages.map((m) => (
          <div key={m.id} className={cn('anim-in flex', m.role === 'user' && 'justify-end')}>
            <div
              className={cn(
                'max-w-[88%] rounded-2xl px-4 py-2.5 text-[13.5px] leading-relaxed',
                m.role === 'user'
                  ? 'rounded-tr-md bg-indigo text-white'
                  : 'rounded-tl-md border bg-paper text-ink',
              )}
            >
              {m.text}
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex items-center gap-2 rounded-2xl rounded-tl-md border bg-paper px-4 py-3" style={{ width: 'fit-content' }}>
            <span className="flex gap-1">
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-mint" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-mint [animation-delay:0.15s]" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-mint [animation-delay:0.3s]" />
            </span>
          </div>
        )}
      </div>
      <div className="border-t p-3">
        {remaining.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-1.5">
            {remaining.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="rounded-full border bg-card px-2.5 py-1 text-[11.5px] font-medium text-ink-soft transition-colors hover:border-mint hover:text-mint-ink"
              >
                {q}
              </button>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send(input)}
            placeholder="Say it how it is…"
            aria-label="Talk to your companion"
            className="h-10 min-w-0 flex-1 rounded-xl border bg-paper px-3.5 text-[13.5px] outline-none transition-colors focus:border-mint"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim()}
            aria-label="Send"
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-mint text-white transition-all hover:bg-[#0e8069] active:scale-95 disabled:opacity-40"
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </Card>
  )
}

export default function Wellbeing() {
  const [mode, setMode] = useState<'none' | 'plan' | 'talk'>('none')
  const [mood, setMood] = useState<string | null>(null)
  const [note, setNote] = useState('')
  const { state, addReflection, toast } = useApp()

  const saveReflection = () => {
    const m = moods.find((x) => x.emoji === mood)
    if (!m) return
    addReflection({ mood: m.emoji, moodLabel: m.label, note: note.trim() })
    setMood(null)
    setNote('')
    toast('Reflection saved', 'Thanks for checking in with yourself.', 'mint')
  }

  return (
    <Page className="max-w-[900px]">
      <PageHeader
        title="Wellbeing"
        sub="Support for how you study — calm, honest, judgment-free. Not therapy, just a companion."
      />

      <div className="grid gap-3 sm:grid-cols-3">
        <Link to="/reset" className="block">
          <Card hover className="flex h-full flex-col items-start gap-3 bg-sky-soft/40">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-card text-sky-ink shadow-(--shadow-soft)">
              <Wind size={18} />
            </span>
            <div>
              <div className="text-[14.5px] font-semibold">I need a reset</div>
              <div className="mt-0.5 text-[12.5px] text-ink-soft">A 2–5 minute breathing pause</div>
            </div>
          </Card>
        </Link>
        <button className="text-left" onClick={() => setMode(mode === 'plan' ? 'none' : 'plan')}>
          <Card hover className={cn('flex h-full flex-col items-start gap-3 bg-indigo-mist', mode === 'plan' && 'border-indigo')}>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-card text-indigo-ink shadow-(--shadow-soft)">
              <CalendarDays size={18} />
            </span>
            <div>
              <div className="text-[14.5px] font-semibold">Help me plan</div>
              <div className="mt-0.5 text-[12.5px] text-ink-soft">When the week feels like too much</div>
            </div>
          </Card>
        </button>
        <button className="text-left" onClick={() => setMode(mode === 'talk' ? 'none' : 'talk')}>
          <Card hover className={cn('flex h-full flex-col items-start gap-3 bg-mint-soft/40', mode === 'talk' && 'border-mint')}>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-card text-mint-ink shadow-(--shadow-soft)">
              <MessageCircle size={18} />
            </span>
            <div>
              <div className="text-[14.5px] font-semibold">I just want to talk</div>
              <div className="mt-0.5 text-[12.5px] text-ink-soft">No agenda, no judgment</div>
            </div>
          </Card>
        </button>
      </div>

      <div className="mt-4">
        {mode === 'plan' && <PlanHelper />}
        {mode === 'talk' && <SupportChat />}
      </div>

      {/* Reflection journal */}
      <section className="mt-9">
        <SectionHeader title="Reflection journal" />
        <Card>
          <div className="text-[14.5px] font-semibold">How did today’s session feel?</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {moods.map((m) => (
              <button
                key={m.emoji}
                onClick={() => setMood(mood === m.emoji ? null : m.emoji)}
                aria-pressed={mood === m.emoji}
                className={cn(
                  'flex items-center gap-2 rounded-full border px-3.5 py-2 text-[13px] font-medium transition-all',
                  mood === m.emoji
                    ? 'border-indigo bg-indigo-soft text-indigo-ink'
                    : 'bg-card text-ink-soft hover:border-line-strong',
                )}
              >
                <span className="text-[16px]">{m.emoji}</span> {m.label}
              </button>
            ))}
          </div>
          {mood != null && (
            <div className="anim-in mt-4">
              <label className="mb-1.5 block text-[13px] font-medium text-ink-soft" htmlFor="refl">
                {mood === '😔' || mood === '😣'
                  ? 'What made it feel that way? (a sentence is plenty)'
                  : 'What worked today? (a sentence is plenty)'}
              </label>
              <textarea
                id="refl"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                className="w-full resize-none rounded-xl border bg-paper px-4 py-3 text-[14px] outline-none transition-colors focus:border-indigo"
                placeholder="Write freely — this stays between us."
              />
              <Button size="sm" className="mt-2.5" onClick={saveReflection}>
                Save reflection
              </Button>
            </div>
          )}
        </Card>

        {state.reflections.length > 0 ? (
          <div className="mt-4 space-y-2.5">
            {state.reflections.slice(0, 4).map((r) => (
              <Card key={r.id} padded={false} className="flex items-start gap-3.5 px-4 py-3.5">
                <span className="text-[20px]">{r.mood}</span>
                <div className="min-w-0 flex-1">
                  <div className="text-[12px] font-semibold text-ink-faint">
                    {new Date(r.date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                    })}{' '}
                    · felt {r.moodLabel.toLowerCase()}
                  </div>
                  {r.note !== '' && (
                    <p className="mt-0.5 text-[13.5px] leading-relaxed text-ink">{r.note}</p>
                  )}
                </div>
              </Card>
            ))}
            <div className="flex items-start gap-2.5 rounded-xl bg-violet-soft/50 px-4 py-3 text-[12.5px] leading-relaxed text-violet-ink">
              <Sparkles size={13} className="mt-0.5 shrink-0" />
              Noticed gently: your sessions before 9pm consistently feel better than late-night
              ones. Tomorrow’s mission is scheduled for the morning.
            </div>
          </div>
        ) : (
          <div className="mt-4">
            <EmptyState
              icon={<HeartHandshake size={19} />}
              title="No reflections yet"
              desc="A one-line check-in after each session helps me schedule your learning when you feel best."
            />
          </div>
        )}
      </section>

      <p className="mt-8 text-center text-[11px] leading-relaxed text-ink-faint">
        StudyOS offers study support, not medical or mental-health care.
        <br />
        If things feel heavy beyond studying, please talk to someone you trust or a professional.
      </p>
    </Page>
  )
}
