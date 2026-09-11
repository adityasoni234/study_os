import { useEffect, useRef, useState } from 'react'
import { Headphones, Pause, Play } from 'lucide-react'
import { studycastLines } from '@/data/notebook'
import { Button } from '@/components/ui/Button'
import { Segmented } from '@/components/ui/Segmented'
import { cn, fmtClock } from '@/lib/utils'

type Phase = 'setup' | 'generating' | 'player'

export function StudyCast() {
  const [phase, setPhase] = useState<Phase>('setup')
  const [length, setLength] = useState<'5' | '10' | '15'>('5')
  const [genLine, setGenLine] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [time, setTime] = useState(0)
  const duration = Number(length) * 60
  const interval = useRef<number | null>(null)

  useEffect(() => {
    if (phase !== 'generating') return
    const t1 = window.setTimeout(() => setGenLine(1), 900)
    const t2 = window.setTimeout(() => setGenLine(2), 1800)
    const t3 = window.setTimeout(() => {
      setPhase('player')
      setPlaying(true)
    }, 2700)
    return () => [t1, t2, t3].forEach(clearTimeout)
  }, [phase])

  useEffect(() => {
    if (playing) {
      interval.current = window.setInterval(() => {
        setTime((t) => {
          if (t + 1 >= duration) {
            setPlaying(false)
            return duration
          }
          return t + 1
        })
      }, 1000)
    }
    return () => {
      if (interval.current != null) window.clearInterval(interval.current)
    }
  }, [playing, duration])

  const activeLine = Math.min(Math.floor(time / 7), studycastLines.length - 1)

  if (phase === 'setup') {
    return (
      <div className="flex min-h-[420px] flex-col items-center justify-center p-6 text-center">
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-soft text-violet-ink">
          <Headphones size={24} />
        </span>
        <h3 className="mt-4 text-[18px] font-semibold">Create a StudyCast</h3>
        <p className="mt-1.5 max-w-sm text-[13.5px] leading-relaxed text-ink-soft">
          I’ll turn Unit 3 into an easy-to-listen conversation between two hosts — perfect for a
          walk or a commute.
        </p>
        <div className="mt-5">
          <Segmented
            options={[
              { value: '5', label: '5 min' },
              { value: '10', label: '10 min' },
              { value: '15', label: '15 min' },
            ]}
            value={length}
            onChange={setLength}
          />
        </div>
        <Button className="mt-5" variant="violet" onClick={() => setPhase('generating')}>
          <Headphones size={15} /> Create StudyCast
        </Button>
      </div>
    )
  }

  if (phase === 'generating') {
    const lines = [
      'Reading your material…',
      'Writing the conversation…',
      'Recording the two voices…',
    ]
    return (
      <div className="flex min-h-[420px] items-center justify-center p-6">
        <div className="space-y-3.5">
          {lines.map((l, i) => (
            <div
              key={l}
              className={cn(
                'flex items-center gap-3 text-[14px] transition-opacity duration-300',
                i <= genLine ? 'opacity-100' : 'opacity-25',
              )}
            >
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-violet-soft">
                {i < genLine ? (
                  <span className="text-[12px] font-bold text-violet-ink">✓</span>
                ) : (
                  <span className="flex gap-0.5">
                    <span className="typing-dot h-1 w-1 rounded-full bg-violet" />
                    <span className="typing-dot h-1 w-1 rounded-full bg-violet [animation-delay:0.15s]" />
                    <span className="typing-dot h-1 w-1 rounded-full bg-violet [animation-delay:0.3s]" />
                  </span>
                )}
              </span>
              {l}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-5">
      <div className="rounded-2xl border bg-gradient-to-br from-violet-soft/60 to-indigo-mist p-5">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setPlaying((p) => !p)}
            aria-label={playing ? 'Pause' : 'Play'}
            className="flex h-13 w-13 shrink-0 items-center justify-center rounded-full bg-violet text-white shadow-(--shadow-lift) transition-all hover:bg-[#6c4be0] active:scale-95"
            style={{ width: 52, height: 52 }}
          >
            {playing ? <Pause size={20} /> : <Play size={20} className="ml-0.5" />}
          </button>
          <div className="min-w-0 flex-1">
            <div className="text-[14.5px] font-semibold">Model Evaluation — the friendly version</div>
            <div className="text-[12px] text-ink-soft">
              From Unit 3 · {length} min episode
            </div>
            <div className="mt-2.5 flex items-center gap-2.5">
              <span className="text-[11px] font-semibold text-ink-faint tnum">{fmtClock(time)}</span>
              <button
                aria-label="Seek"
                className="group relative h-4 flex-1 cursor-pointer"
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  const frac = (e.clientX - rect.left) / rect.width
                  setTime(Math.floor(frac * duration))
                }}
              >
                <span className="absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-card" />
                <span
                  className="absolute top-1/2 left-0 h-1.5 -translate-y-1/2 rounded-full bg-violet transition-all"
                  style={{ width: `${(time / duration) * 100}%` }}
                />
              </button>
              <span className="text-[11px] font-semibold text-ink-faint tnum">
                {fmtClock(duration)}
              </span>
            </div>
          </div>
          {/* Equalizer */}
          <div className="hidden h-8 items-end gap-[3px] sm:flex" aria-hidden>
            {[0.9, 0.5, 1, 0.65, 0.8].map((h, i) => (
              <span
                key={i}
                className={cn('w-[3.5px] rounded-full bg-violet', playing && 'eq-bar')}
                style={{
                  height: `${h * 30}px`,
                  animationDelay: `${i * 0.13}s`,
                  ...(playing ? {} : { transform: 'scaleY(0.35)', transformOrigin: 'bottom' }),
                }}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4">
        <div className="mb-2 text-[11.5px] font-bold tracking-[0.09em] text-ink-faint uppercase">
          Transcript
        </div>
        <div className="max-h-[260px] space-y-2 overflow-y-auto pr-1">
          {studycastLines.map((line, i) => (
            <div
              key={i}
              className={cn(
                'flex gap-3 rounded-xl px-3.5 py-2.5 transition-all duration-300',
                i === activeLine && playing ? 'bg-violet-soft/70' : i <= activeLine ? 'opacity-90' : 'opacity-45',
              )}
            >
              <span
                className={cn(
                  'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10.5px] font-bold',
                  line.speaker === 'A' ? 'bg-violet text-white' : 'bg-sky text-white',
                )}
              >
                {line.speaker}
              </span>
              <p className="text-[13px] leading-relaxed text-ink-soft">{line.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
