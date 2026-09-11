import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, X } from 'lucide-react'
import { fmtClock } from '@/lib/utils'
import { cn } from '@/lib/utils'

type Phase = 'choose' | 'running' | 'done'
type Breath = 'in' | 'hold' | 'out'

const breathSpec: Record<Breath, { label: string; seconds: number; next: Breath; scale: number }> = {
  in: { label: 'Breathe in…', seconds: 4, next: 'hold', scale: 1.28 },
  hold: { label: 'Hold', seconds: 3, next: 'out', scale: 1.28 },
  out: { label: 'Breathe out…', seconds: 6, next: 'in', scale: 1 },
}

export default function Reset() {
  const [phase, setPhase] = useState<Phase>('choose')
  const [remaining, setRemaining] = useState(0)
  const [breath, setBreath] = useState<Breath>('in')
  const navigate = useNavigate()
  const breathTimer = useRef<number | null>(null)

  // Countdown
  useEffect(() => {
    if (phase !== 'running') return
    const t = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          setPhase('done')
          return 0
        }
        return r - 1
      })
    }, 1000)
    return () => window.clearInterval(t)
  }, [phase])

  // Breathing cycle
  useEffect(() => {
    if (phase !== 'running') return
    const spec = breathSpec[breath]
    breathTimer.current = window.setTimeout(() => setBreath(spec.next), spec.seconds * 1000)
    return () => {
      if (breathTimer.current != null) window.clearTimeout(breathTimer.current)
    }
  }, [phase, breath])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') navigate(-1)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [navigate])

  const start = (minutes: number) => {
    setRemaining(minutes * 60)
    setBreath('in')
    setPhase('running')
  }

  const spec = breathSpec[breath]

  return (
    <div
      className="flex min-h-dvh flex-col items-center justify-center px-6"
      style={{
        background: 'linear-gradient(160deg, #EAF2FB 0%, #F4F1FB 55%, #FAF6EF 100%)',
      }}
    >
      <button
        onClick={() => navigate(-1)}
        aria-label="Leave reset mode"
        className="absolute top-5 right-5 flex h-10 w-10 items-center justify-center rounded-full bg-white/60 text-ink-soft backdrop-blur transition-colors hover:bg-white hover:text-ink"
      >
        <X size={18} />
      </button>

      {phase === 'choose' && (
        <div className="anim-in flex flex-col items-center text-center">
          <h1 className="font-display text-[32px] font-semibold tracking-[-0.01em] text-ink">
            Take a breath.
          </h1>
          <p className="mt-2 max-w-xs text-[14.5px] leading-relaxed text-ink-soft">
            A short pause resets focus better than pushing through ever does.
          </p>
          <div className="mt-8 flex gap-3">
            {[2, 5].map((m) => (
              <button
                key={m}
                onClick={() => start(m)}
                className="flex h-24 w-28 flex-col items-center justify-center rounded-2xl border border-white/80 bg-white/70 shadow-(--shadow-soft) backdrop-blur transition-all duration-200 hover:-translate-y-0.5 hover:bg-white hover:shadow-(--shadow-lift)"
              >
                <span className="text-[24px] font-bold text-ink tnum">{m}</span>
                <span className="text-[12px] font-medium text-ink-soft">minutes</span>
              </button>
            ))}
          </div>
          <button
            onClick={() => navigate(-1)}
            className="mt-8 text-[13px] font-semibold text-ink-faint transition-colors hover:text-ink"
          >
            Not right now
          </button>
        </div>
      )}

      {phase === 'running' && (
        <div className="flex flex-col items-center">
          <div className="text-[13px] font-semibold text-ink-faint tnum">{fmtClock(remaining)}</div>
          <div className="relative mt-10 flex items-center justify-center" style={{ width: 260, height: 260 }}>
            <div className="absolute inset-0 rounded-full bg-white/40" />
            <div
              className={cn('breath-circle absolute rounded-full bg-white/70 backdrop-blur')}
              style={{
                width: 170,
                height: 170,
                transform: `scale(${spec.scale})`,
                transitionDuration: `${spec.seconds}s`,
                boxShadow: '0 20px 60px -20px rgb(91 86 214 / 0.35)',
              }}
            />
            <span className="relative z-10 text-[17px] font-medium text-ink">{spec.label}</span>
          </div>
          <button
            onClick={() => setPhase('done')}
            className="mt-12 text-[13px] font-semibold text-ink-faint transition-colors hover:text-ink"
          >
            End early
          </button>
        </div>
      )}

      {phase === 'done' && (
        <div className="anim-in flex flex-col items-center text-center">
          <span className="text-[36px]">🌿</span>
          <h1 className="mt-3 font-display text-[28px] font-semibold text-ink">Nice pause.</h1>
          <p className="mt-1.5 text-[14.5px] text-ink-soft">Ready when you are — no rush.</p>
          <Link
            to="/"
            className="mt-7 inline-flex h-11 items-center gap-2 rounded-xl bg-indigo px-5 text-[14.5px] font-semibold text-white shadow-(--shadow-lift) transition-all hover:bg-indigo-deep active:scale-[0.98]"
          >
            Return to learning <ArrowRight size={16} />
          </Link>
        </div>
      )}
    </div>
  )
}
