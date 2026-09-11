import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bookmark, Check, Flower2, PenLine, Plus, RefreshCw, Sparkles, Wind } from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, Eyebrow, SectionHeader } from '@/components/ui/Card'
import { wisdomEntries } from '@/data/wisdom'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'

export default function InnerGrowth() {
  const [entryIndex, setEntryIndex] = useState(0)
  const [reflecting, setReflecting] = useState(false)
  const [reflection, setReflection] = useState('')
  const [gratitudeInput, setGratitudeInput] = useState('')
  const [savedEntry, setSavedEntry] = useState(false)
  const { state, addReflection, addGratitude, toast } = useApp()
  const entry = wisdomEntries[entryIndex % wisdomEntries.length]

  const saveReflection = () => {
    if (!reflection.trim()) return
    addReflection({ mood: '🪷', moodLabel: 'Reflection', note: reflection.trim() })
    setReflection('')
    setReflecting(false)
    toast('Reflection kept', 'Saved quietly to your journal.', 'mint')
  }

  const todayGratitude = state.gratitude.slice(0, 3)

  return (
    <Page className="max-w-[860px]">
      <PageHeader
        title="Inner Growth"
        sub="A quiet, optional space — a verse, a pause, a little gratitude. Explore or skip freely."
      />

      {/* Wisdom card */}
      <Card className="relative overflow-hidden p-7 lg:p-9">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-40 opacity-60"
          style={{
            background:
              'linear-gradient(180deg, var(--color-violet-soft) 0%, rgba(242,238,253,0) 100%)',
          }}
        />
        <div className="relative">
          <div className="flex items-center justify-between">
            <Eyebrow className="flex items-center gap-1.5 text-violet-ink">
              <Flower2 size={13} /> Today’s reflection
            </Eyebrow>
            <button
              onClick={() => {
                setEntryIndex((i) => i + 1)
                setSavedEntry(false)
              }}
              className="flex items-center gap-1.5 text-[12px] font-semibold text-ink-faint transition-colors hover:text-ink"
            >
              <RefreshCw size={12} /> Another verse
            </button>
          </div>

          <div key={entry.id} className="anim-fade">
            <p className="mt-6 text-center font-display text-[24px] leading-relaxed text-ink lg:text-[27px]">
              {entry.original}
            </p>
            <p className="mt-2 text-center text-[13.5px] text-ink-faint italic">
              {entry.transliteration}
            </p>

            <div className="mx-auto mt-6 max-w-md border-t pt-5 text-center">
              <div className="text-[11px] font-bold tracking-[0.1em] text-ink-faint uppercase">
                Meaning
              </div>
              <p className="mt-1.5 text-[15.5px] leading-relaxed font-medium text-ink">
                “{entry.translation}”
              </p>
              <div className="mt-2 text-[11.5px] text-ink-faint">
                {entry.source} · {entry.sourceNote}
              </div>
            </div>

            <div className="mx-auto mt-5 max-w-md rounded-xl bg-violet-soft/50 p-4">
              <div className="flex items-center justify-center gap-1.5 text-[11px] font-bold tracking-wide text-violet-ink uppercase">
                <Sparkles size={11} /> A thought from your companion · AI reflection
              </div>
              <p className="mt-1.5 text-center text-[13.5px] leading-relaxed text-ink-soft">
                {entry.reflection}
              </p>
            </div>

            <p className="mt-5 text-center text-[14.5px] leading-relaxed font-medium text-ink">
              {entry.question}
            </p>

            <div className="mt-5 flex justify-center gap-2.5">
              <Button size="sm" variant="violet" onClick={() => setReflecting((r) => !r)}>
                <PenLine size={13} /> Reflect
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  setSavedEntry(true)
                  toast('Verse saved', 'You can revisit it from your journal.', 'violet')
                }}
              >
                {savedEntry ? <Check size={13} /> : <Bookmark size={13} />}
                {savedEntry ? 'Saved' : 'Save'}
              </Button>
            </div>

            {reflecting && (
              <div className="anim-in mx-auto mt-5 max-w-md">
                <textarea
                  value={reflection}
                  onChange={(e) => setReflection(e.target.value)}
                  rows={3}
                  placeholder="Write whatever comes — nobody is grading this."
                  className="w-full resize-none rounded-xl border bg-paper px-4 py-3 text-[14px] outline-none transition-colors focus:border-violet"
                />
                <div className="mt-2 flex justify-end">
                  <Button size="sm" onClick={saveReflection} disabled={!reflection.trim()}>
                    Keep this
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {/* Gratitude */}
        <Card>
          <SectionHeader title="Gratitude — three small things" className="mb-3" />
          <div className="flex items-center gap-2">
            <input
              value={gratitudeInput}
              onChange={(e) => setGratitudeInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && gratitudeInput.trim()) {
                  addGratitude(gratitudeInput.trim())
                  setGratitudeInput('')
                }
              }}
              placeholder="Today I’m grateful for…"
              aria-label="Add gratitude"
              className="h-10 min-w-0 flex-1 rounded-xl border bg-paper px-3.5 text-[13.5px] outline-none transition-colors focus:border-mint"
            />
            <button
              onClick={() => {
                if (!gratitudeInput.trim()) return
                addGratitude(gratitudeInput.trim())
                setGratitudeInput('')
              }}
              aria-label="Add"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-mint text-white transition-all hover:bg-[#0e8069] active:scale-95"
            >
              <Plus size={16} />
            </button>
          </div>
          {todayGratitude.length > 0 ? (
            <ul className="mt-3.5 space-y-2">
              {todayGratitude.map((g) => (
                <li
                  key={g.id}
                  className="anim-in flex items-start gap-2.5 rounded-xl bg-mint-soft/60 px-3.5 py-2.5 text-[13.5px] leading-relaxed text-ink"
                >
                  <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-mint" />
                  {g.text}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3.5 text-[12.5px] leading-relaxed text-ink-faint">
              Small counts: a good chai, a concept that clicked, a friend’s message.
            </p>
          )}
        </Card>

        {/* Guided pause + journal snapshot */}
        <div className="space-y-4">
          <Link to="/reset" className="block">
            <Card hover className="flex items-center gap-4 bg-sky-soft/40">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-card text-sky-ink shadow-(--shadow-soft)">
                <Wind size={19} />
              </span>
              <div className="flex-1">
                <div className="text-[14.5px] font-semibold">Guided pause</div>
                <div className="text-[12.5px] text-ink-soft">2 or 5 quiet minutes of breathing</div>
              </div>
            </Card>
          </Link>
          <Card>
            <SectionHeader title="Recent reflections" className="mb-3" />
            {state.reflections.length === 0 ? (
              <p className="text-[12.5px] leading-relaxed text-ink-faint">
                Reflections you write here and in Wellbeing gather in one quiet journal.
              </p>
            ) : (
              <ul className="space-y-2">
                {state.reflections.slice(0, 3).map((r) => (
                  <li key={r.id} className="flex items-start gap-2.5 text-[13px] leading-relaxed">
                    <span className="text-[15px]">{r.mood}</span>
                    <span className="min-w-0 flex-1 truncate text-ink-soft">
                      {r.note !== '' ? r.note : `Felt ${r.moodLabel.toLowerCase()}`}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <div className="flex items-center justify-center gap-1.5">
            {[1, 1, 1, 1, 0, 0, 0].map((done, i) => (
              <span
                key={i}
                className={cn('h-2 w-2 rounded-full', done === 1 ? 'bg-violet' : 'bg-line-strong')}
              />
            ))}
            <span className="ml-2 text-[11.5px] font-medium text-ink-faint">
              4 quiet minutes this week
            </span>
          </div>
        </div>
      </div>

      <p className="mt-8 text-center text-[11px] leading-relaxed text-ink-faint">
        Verses are authentic classical texts with common English renderings; the reflection is
        AI-written and labeled as such. This space is optional and belongs to you.
      </p>
    </Page>
  )
}
