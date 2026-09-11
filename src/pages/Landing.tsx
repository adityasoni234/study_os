import { Link, Navigate } from 'react-router-dom'
import {
  ArrowRight,
  BookOpen,
  Check,
  Clock,
  FileText,
  Flower2,
  Globe,
  GraduationCap,
  HeartHandshake,
  Map,
  PenLine,
  Radar,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react'
import { Logo } from '@/lib/icons'
import { Button } from '@/components/ui/Button'
import { Ring } from '@/components/ui/Progress'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'

const features = [
  {
    icon: GraduationCap,
    tone: 'bg-indigo-soft text-indigo-ink',
    title: 'A tutor that teaches, not just answers',
    desc: 'Explains at your level, checks understanding with real questions, and re-teaches gently when you slip — until it sticks.',
  },
  {
    icon: Map,
    tone: 'bg-violet-soft text-violet-ink',
    title: 'Roadmaps that reshape themselves',
    desc: 'Any goal becomes a guided path. Strong results accelerate it; shaky ones add review stops — automatically.',
  },
  {
    icon: BookOpen,
    tone: 'bg-sky-soft text-sky-ink',
    title: 'A notebook that reads your materials',
    desc: 'PDFs, videos, notes — every answer grounded in your sources, with citations you can open and verify.',
  },
  {
    icon: PenLine,
    tone: 'bg-mint-soft text-mint-ink',
    title: 'Practice that becomes mastery',
    desc: 'Quizzes, flashcards and mastery checks tuned to your weak spots. Every result updates your map.',
  },
  {
    icon: Radar,
    tone: 'bg-amber-soft text-amber-ink',
    title: 'Learning that leads somewhere',
    desc: 'Hackathons, internships, scholarships — matched to what you know, with a day-by-day plan to get ready.',
  },
  {
    icon: HeartHandshake,
    tone: 'bg-coral-soft text-coral-ink',
    title: 'Support for the human behind the grades',
    desc: 'Breathing resets, honest planning help, reflection — and an optional quiet space for inner growth.',
  },
]

const steps = [
  { title: 'Learn', desc: 'Your tutor explains it your way' },
  { title: 'Practice', desc: 'Questions with instant, kind feedback' },
  { title: 'Master', desc: 'Mastery updates your roadmap' },
  { title: 'Grow', desc: 'Progress across every dimension' },
  { title: 'Act', desc: 'Real opportunities, matched to you' },
]

function HeroPreview() {
  return (
    <div className="relative mx-auto mt-14 max-w-3xl">
      <div
        aria-hidden
        className="absolute -inset-x-20 -top-16 -bottom-10 rounded-full opacity-70 blur-2xl"
        style={{
          background:
            'radial-gradient(closest-side, #EDEDFB 0%, #F2EEFD66 55%, transparent 100%)',
        }}
      />
      {/* App frame */}
      <div className="relative rounded-2xl border bg-card p-2 shadow-(--shadow-lift)">
        <div className="flex items-center gap-1.5 px-3 py-2">
          <span className="h-2.5 w-2.5 rounded-full bg-coral/50" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber/50" />
          <span className="h-2.5 w-2.5 rounded-full bg-mint/50" />
        </div>
        <div className="flex gap-3 rounded-xl bg-paper p-4">
          {/* mini sidebar */}
          <div className="hidden w-32 shrink-0 flex-col gap-1 rounded-lg border bg-card/70 p-2 sm:flex">
            <div className="mb-1 flex items-center gap-1.5 px-1.5 py-1">
              <Logo size={16} />
              <span className="text-[10px] font-bold">StudyOS</span>
            </div>
            {['Home', 'Roadmaps', '1:1 Tutor', 'Notebook', 'Growth'].map((item, i) => (
              <div
                key={item}
                className={cn(
                  'rounded-md px-2 py-1 text-[9.5px] font-medium',
                  i === 0 ? 'bg-indigo-soft text-indigo-ink' : 'text-ink-faint',
                )}
              >
                {item}
              </div>
            ))}
          </div>
          {/* mini mission card */}
          <div className="min-w-0 flex-1 rounded-lg border bg-card p-4 text-left shadow-(--shadow-soft)">
            <div className="flex items-center gap-1.5 text-[9px] font-bold tracking-[0.1em] text-indigo-ink uppercase">
              <Target size={10} /> Today’s mission
            </div>
            <div className="mt-1.5 font-display text-[17px] leading-tight font-semibold">
              Precision &amp; Recall
            </div>
            <div className="mt-0.5 flex items-center gap-1.5 text-[10px] text-ink-faint">
              Machine Learning · <Clock size={9} /> 25 min
            </div>
            <div className="mt-3 space-y-1.5">
              {[
                { label: 'Learn the concept', done: true },
                { label: 'Practice 5 questions', done: true },
                { label: 'Mastery check', done: false },
              ].map((s) => (
                <div key={s.label} className="flex items-center gap-2">
                  <span
                    className={cn(
                      'flex h-3.5 w-3.5 items-center justify-center rounded-full border-[1.5px]',
                      s.done ? 'border-mint bg-mint text-white' : 'border-indigo',
                    )}
                  >
                    {s.done && <Check size={8} strokeWidth={4} />}
                  </span>
                  <span
                    className={cn(
                      'text-[10.5px]',
                      s.done ? 'text-ink-faint line-through' : 'font-medium',
                    )}
                  >
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-3 inline-flex h-7 items-center gap-1 rounded-lg bg-indigo px-2.5 text-[10px] font-semibold text-white">
              Continue Learning <ArrowRight size={10} />
            </div>
          </div>
          {/* mini right rail */}
          <div className="hidden w-36 shrink-0 flex-col gap-2 md:flex">
            <div className="rounded-lg border bg-card p-2.5 shadow-(--shadow-soft)">
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-bold text-ink-soft">Mastery</span>
                <Ring value={72} size={26} stroke={3.5} tone="mint" />
              </div>
              <div className="mt-1 text-[9.5px] text-ink-faint">65% → 72% today</div>
            </div>
            <div className="rounded-lg border bg-card p-2.5 shadow-(--shadow-soft)">
              <div className="text-[9px] font-bold text-ink-soft">Roadmap</div>
              <div className="mt-1.5 space-y-1">
                {[
                  ['Foundations', 'bg-mint'],
                  ['Classification', 'bg-indigo'],
                  ['Neural Nets', 'bg-line-strong'],
                ].map(([label, dot]) => (
                  <div key={label} className="flex items-center gap-1.5">
                    <span className={cn('h-1.5 w-1.5 rounded-full', dot)} />
                    <span className="text-[9.5px] text-ink-soft">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* floating chips */}
      <div className="anim-pop absolute -top-4 -right-2 hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-[11px] font-semibold text-mint-ink shadow-(--shadow-lift) sm:flex">
        <TrendingUp size={12} /> Mastery updated · Roadmap adapted
      </div>
      <div
        className="anim-pop absolute -bottom-4 -left-2 hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-[11px] font-medium text-ink-soft shadow-(--shadow-lift) sm:flex"
        style={{ animationDelay: '0.15s' }}
      >
        <FileText size={11} /> ML Course Notes · Unit 3, p.14
      </div>
      <div
        className="anim-pop absolute right-6 -bottom-5 hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-[11px] font-semibold text-violet-ink shadow-(--shadow-lift) md:flex"
        style={{ animationDelay: '0.3s' }}
      >
        <Radar size={12} /> 94% match · AI Hackathon
      </div>
    </div>
  )
}

export default function Landing() {
  const { state } = useApp()
  if (state.auth.authed) return <Navigate to="/" replace />

  return (
    <div className="min-h-dvh bg-paper">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-line/60 bg-paper/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
          <div className="flex items-center gap-2.5">
            <Logo size={30} />
            <span className="text-[17px] font-bold tracking-tight">StudyOS</span>
          </div>
          <nav className="hidden items-center gap-7 text-[13.5px] font-medium text-ink-soft md:flex">
            <a href="#features" className="transition-colors hover:text-ink">
              Features
            </a>
            <a href="#how" className="transition-colors hover:text-ink">
              How it works
            </a>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/auth">
              <Button variant="ghost">Sign in</Button>
            </Link>
            <Link to="/auth?mode=signup">
              <Button>Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden px-5 pt-16 pb-20 text-center lg:pt-24">
        <div className="anim-in mx-auto max-w-3xl">
          <div className="mx-auto inline-flex items-center gap-1.5 rounded-full border bg-card px-3.5 py-1.5 text-[12px] font-semibold text-ink-soft shadow-(--shadow-soft)">
            <Globe size={12} className="text-indigo" /> Built for SDG 4 · Quality Education
          </div>
          <h1 className="mt-6 font-display text-[40px] leading-[1.08] font-semibold tracking-[-0.015em] sm:text-[52px] lg:text-[60px]">
            Learn anything.
            <br />
            <span className="text-indigo">Grow every day.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-[16px] leading-relaxed text-ink-soft lg:text-[17px]">
            StudyOS is a personal AI learning companion that understands how you learn, guides what
            comes next, helps you truly master it — and connects it all to real-world
            opportunities.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/auth?mode=signup">
              <Button size="lg" className="px-7">
                Start learning free <ArrowRight size={16} />
              </Button>
            </Link>
            <a href="#how">
              <Button size="lg" variant="secondary">
                See how it works
              </Button>
            </a>
          </div>
        </div>

        <div className="anim-in anim-d-2">
          <HeroPreview />
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl scroll-mt-20 px-5 py-16">
        <div className="text-center">
          <div className="text-[12px] font-bold tracking-[0.12em] text-indigo-ink uppercase">
            Simple outside, powerful inside
          </div>
          <h2 className="mt-2 font-display text-[28px] leading-tight font-semibold lg:text-[34px]">
            Everything a learner needs. Nothing they don’t.
          </h2>
        </div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <div
              key={f.title}
              className={cn(
                'anim-in rounded-2xl border bg-card p-5 shadow-(--shadow-soft) transition-all duration-200 hover:-translate-y-1 hover:shadow-(--shadow-lift)',
                `anim-d-${(i % 3) + 1}`,
              )}
            >
              <span className={cn('flex h-11 w-11 items-center justify-center rounded-xl', f.tone)}>
                <f.icon size={20} />
              </span>
              <h3 className="mt-4 text-[15.5px] leading-snug font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-ink-soft">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-5xl scroll-mt-20 px-5 py-16">
        <div className="text-center">
          <div className="text-[12px] font-bold tracking-[0.12em] text-indigo-ink uppercase">
            The loop
          </div>
          <h2 className="mt-2 font-display text-[28px] leading-tight font-semibold lg:text-[34px]">
            One calm cycle, repeated daily
          </h2>
        </div>
        <div className="relative mt-12">
          <div className="absolute top-5 right-[10%] left-[10%] hidden h-px bg-line-strong md:block" />
          <div className="grid gap-8 sm:grid-cols-3 md:grid-cols-5">
            {steps.map((s, i) => (
              <div key={s.title} className="relative flex flex-col items-center text-center">
                <span className="z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 border-indigo bg-card text-[14px] font-bold text-indigo-ink">
                  {i + 1}
                </span>
                <div className="mt-3 text-[15px] font-semibold">{s.title}</div>
                <div className="mt-1 max-w-[160px] text-[12px] leading-relaxed text-ink-soft">
                  {s.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Callout */}
      <section className="mx-auto max-w-5xl px-5 py-16">
        <div
          className="relative overflow-hidden rounded-3xl p-10 text-center text-white lg:p-14"
          style={{ background: 'linear-gradient(135deg, #5B56D6 0%, #7C5CF0 100%)' }}
        >
          <Sparkles size={22} className="mx-auto opacity-90" />
          <h2 className="mx-auto mt-4 max-w-2xl font-display text-[26px] leading-snug font-semibold lg:text-[32px]">
            StudyOS doesn’t just answer questions.
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-[14.5px] leading-relaxed text-white/85">
            It understands how you learn, guides what you learn next, helps you master it, supports
            your wellbeing — and connects your learning to the real world.
          </p>
          <Link to="/auth?mode=signup" className="mt-7 inline-block">
            <Button size="lg" variant="light" className="px-7">
              Begin your journey <ArrowRight size={16} />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t px-5 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <Logo size={22} />
            <span className="text-[14px] font-bold">StudyOS</span>
            <span className="ml-2 text-[12px] text-ink-faint">Learn · Grow · Belong</span>
          </div>
          <div className="flex items-center gap-1.5 text-[12px] text-ink-faint">
            <Flower2 size={12} /> Supporting UN SDG 4 — Quality Education · © 2026 StudyOS
          </div>
        </div>
      </footer>
    </div>
  )
}
