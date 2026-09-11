import { useMemo, useState } from 'react'
import { RotateCcw, Sparkles } from 'lucide-react'
import { flashcards } from '@/data/notebook'
import { Button } from '@/components/ui/Button'
import { ProgressBar } from '@/components/ui/Progress'
import { cn } from '@/lib/utils'

const ratings = [
  { label: 'Again', tone: 'bg-coral-soft text-coral-ink hover:bg-[#f7e0dc]' },
  { label: 'Hard', tone: 'bg-amber-soft text-amber-ink hover:bg-[#f5e9cd]' },
  { label: 'Good', tone: 'bg-sky-soft text-sky-ink hover:bg-[#daebf7]' },
  { label: 'Easy', tone: 'bg-mint-soft text-mint-ink hover:bg-[#d3ede3]' },
]

export function Flashcards() {
  // Weak cards first — the deck adapts to what needs work.
  const deck = useMemo(
    () => [...flashcards.filter((f) => f.weak), ...flashcards.filter((f) => !f.weak)],
    [],
  )
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [counts, setCounts] = useState({ again: 0, good: 0 })
  const [leaving, setLeaving] = useState(false)

  const card = deck[index]
  const done = index >= deck.length

  const rate = (label: string) => {
    setCounts((c) => ({
      again: c.again + (label === 'Again' || label === 'Hard' ? 1 : 0),
      good: c.good + (label === 'Good' || label === 'Easy' ? 1 : 0),
    }))
    setLeaving(true)
    window.setTimeout(() => {
      setFlipped(false)
      setLeaving(false)
      setIndex((i) => i + 1)
    }, 240)
  }

  if (done) {
    return (
      <div className="flex min-h-[420px] flex-col items-center justify-center p-6 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-mint-soft text-mint-ink">
          <Sparkles size={20} />
        </span>
        <h3 className="mt-3 text-[17px] font-semibold">Deck complete</h3>
        <p className="mt-1 max-w-xs text-[13.5px] text-ink-soft">
          {counts.good} solid · {counts.again} to revisit — I’ll bring those back sooner next time.
        </p>
        <Button
          className="mt-5"
          variant="secondary"
          onClick={() => {
            setIndex(0)
            setCounts({ again: 0, good: 0 })
          }}
        >
          <RotateCcw size={14} /> Go again
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center p-6">
      <div className="mb-4 flex w-full max-w-md items-center gap-3">
        <span className="text-[12.5px] font-semibold whitespace-nowrap text-ink-soft tnum">
          Card {index + 1} of {deck.length}
        </span>
        <ProgressBar value={(index / deck.length) * 100} className="flex-1" />
        {card.weak === true && (
          <span className="rounded-full bg-amber-soft px-2 py-0.5 text-[10.5px] font-bold whitespace-nowrap text-amber-ink">
            weak spot
          </span>
        )}
      </div>

      <button
        onClick={() => setFlipped((f) => !f)}
        className={cn(
          'flip-scene w-full max-w-md outline-none transition-all duration-200',
          leaving && 'translate-x-6 opacity-0',
        )}
        aria-label={flipped ? 'Show question' : 'Reveal answer'}
      >
        <div className={cn('flip-inner relative h-[260px] w-full', flipped && 'flipped')}>
          <div className="flip-face absolute inset-0 flex flex-col items-center justify-center rounded-2xl border bg-card p-6 shadow-(--shadow-soft)">
            <span className="mb-3 text-[10.5px] font-bold tracking-[0.12em] text-ink-faint uppercase">
              Concept
            </span>
            <p className="text-center text-[17px] leading-relaxed font-semibold">{card.front}</p>
            <span className="mt-4 text-[11.5px] text-ink-faint">tap to reveal</span>
          </div>
          <div className="flip-face flip-back absolute inset-0 flex flex-col items-center justify-center rounded-2xl border border-indigo-soft bg-indigo-mist p-6">
            <span className="mb-3 text-[10.5px] font-bold tracking-[0.12em] text-indigo-ink uppercase">
              Answer
            </span>
            <p className="text-center text-[14.5px] leading-relaxed whitespace-pre-line text-ink">
              {card.back}
            </p>
          </div>
        </div>
      </button>

      <div
        className={cn(
          'mt-5 grid w-full max-w-md grid-cols-4 gap-2 transition-opacity duration-200',
          flipped ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
      >
        {ratings.map((r) => (
          <button
            key={r.label}
            onClick={() => rate(r.label)}
            className={cn(
              'h-10 rounded-xl text-[13px] font-semibold transition-all active:scale-95',
              r.tone,
            )}
          >
            {r.label}
          </button>
        ))}
      </div>
      <p className="mt-3 text-[11.5px] text-ink-faint">Weak concepts appear first and return sooner</p>
    </div>
  )
}
