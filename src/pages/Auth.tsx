import { useState } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  Lock,
  Mail,
  Sparkles,
  User,
} from 'lucide-react'
import { Logo } from '@/lib/icons'
import { Button } from '@/components/ui/Button'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'

const promises = [
  'A tutor that adapts to your level',
  'Roadmaps that reshape as you learn',
  'Real opportunities, matched to you',
]

export default function Auth() {
  const [params] = useSearchParams()
  const [mode, setMode] = useState<'signin' | 'signup'>(
    params.get('mode') === 'signup' ? 'signup' : 'signin',
  )
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { state, signIn, toast } = useApp()
  const navigate = useNavigate()

  if (state.auth.authed) return <Navigate to="/" replace />

  const finish = (displayName: string) => {
    signIn(displayName)
    const first = (displayName.trim() || 'Aditya').split(' ')[0]
    toast(`Welcome, ${first} 🌱`, 'Your learning space is ready.', 'mint')
    navigate('/')
  }

  const submit = () => {
    setError(null)
    if (mode === 'signup' && name.trim().length < 2) {
      setError('Tell us your name — it makes the tutor friendlier.')
      return
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError('That email doesn’t look quite right.')
      return
    }
    if (password.length < 6) {
      setError('Passwords need at least 6 characters.')
      return
    }
    finish(mode === 'signup' ? name : email.split('@')[0].replace(/[._-]/g, ' '))
  }

  return (
    <div className="flex min-h-dvh bg-paper">
      {/* Brand panel */}
      <aside
        className="relative hidden w-[46%] flex-col justify-between overflow-hidden p-10 text-white lg:flex"
        style={{ background: 'linear-gradient(150deg, #5B56D6 0%, #6E55E4 55%, #7C5CF0 100%)' }}
      >
        <div
          aria-hidden
          className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-white/10 blur-2xl"
        />
        <Link to="/welcome" className="relative flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
            <Logo size={24} />
          </span>
          <span className="text-[17px] font-bold tracking-tight">StudyOS</span>
        </Link>

        <div className="relative max-w-md">
          <h1 className="font-display text-[34px] leading-[1.15] font-semibold">
            Someone intelligent, in your corner, every day.
          </h1>
          <ul className="mt-7 space-y-3.5">
            {promises.map((p) => (
              <li key={p} className="flex items-center gap-3 text-[14.5px] text-white/90">
                <span
                  className="flex shrink-0 items-center justify-center rounded-full bg-white/20"
                  style={{ width: 22, height: 22 }}
                >
                  <Check size={12} strokeWidth={3} />
                </span>
                {p}
              </li>
            ))}
          </ul>
        </div>

        <div className="relative text-[12.5px] leading-relaxed text-white/70">
          “विद्या ददाति विनयम्” — knowledge gives humility.
          <span className="block text-white/50">Hitopadesha · classical text</span>
        </div>
      </aside>

      {/* Form */}
      <main className="flex flex-1 flex-col items-center justify-center px-5 py-10">
        <div className="anim-in w-full max-w-[400px]">
          <Link
            to="/welcome"
            className="mb-6 inline-flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft transition-colors hover:text-ink"
          >
            <ArrowLeft size={14} /> Back
          </Link>

          <div className="mb-6 flex items-center gap-2.5 lg:hidden">
            <Logo size={30} />
            <span className="text-[17px] font-bold">StudyOS</span>
          </div>

          <h2 className="font-display text-[26px] leading-tight font-semibold">
            {mode === 'signin' ? 'Welcome back' : 'Begin your journey'}
          </h2>
          <p className="mt-1 text-[13.5px] text-ink-soft">
            {mode === 'signin'
              ? 'Your roadmap kept your place while you were away.'
              : 'Two minutes from now, you’ll have a personal tutor.'}
          </p>

          {/* Mode switch */}
          <div className="mt-6 grid grid-cols-2 rounded-[11px] border bg-paper-deep p-1">
            {(['signin', 'signup'] as const).map((m) => (
              <button
                key={m}
                onClick={() => {
                  setMode(m)
                  setError(null)
                }}
                aria-pressed={mode === m}
                className={cn(
                  'h-9 rounded-lg text-[13.5px] font-semibold transition-all duration-200',
                  mode === m ? 'bg-card shadow-(--shadow-soft)' : 'text-ink-soft hover:text-ink',
                )}
              >
                {m === 'signin' ? 'Sign in' : 'Create account'}
              </button>
            ))}
          </div>

          <div className="mt-5 space-y-3.5">
            {mode === 'signup' && (
              <div className="anim-in">
                <label htmlFor="name" className="mb-1.5 block text-[12.5px] font-semibold">
                  Name
                </label>
                <div className="flex h-11 items-center gap-2.5 rounded-xl border bg-card px-3.5 transition-colors focus-within:border-indigo">
                  <User size={15} className="shrink-0 text-ink-faint" />
                  <input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="What should your tutor call you?"
                    className="h-full min-w-0 flex-1 bg-transparent text-[14px] outline-none placeholder:text-ink-faint"
                  />
                </div>
              </div>
            )}
            <div>
              <label htmlFor="email" className="mb-1.5 block text-[12.5px] font-semibold">
                Email
              </label>
              <div className="flex h-11 items-center gap-2.5 rounded-xl border bg-card px-3.5 transition-colors focus-within:border-indigo">
                <Mail size={15} className="shrink-0 text-ink-faint" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="h-full min-w-0 flex-1 bg-transparent text-[14px] outline-none placeholder:text-ink-faint"
                />
              </div>
            </div>
            <div>
              <label htmlFor="password" className="mb-1.5 block text-[12.5px] font-semibold">
                Password
              </label>
              <div className="flex h-11 items-center gap-2.5 rounded-xl border bg-card px-3.5 transition-colors focus-within:border-indigo">
                <Lock size={15} className="shrink-0 text-ink-faint" />
                <input
                  id="password"
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && submit()}
                  placeholder={mode === 'signup' ? 'At least 6 characters' : 'Your password'}
                  className="h-full min-w-0 flex-1 bg-transparent text-[14px] outline-none placeholder:text-ink-faint"
                />
                <button
                  onClick={() => setShowPw((s) => !s)}
                  aria-label={showPw ? 'Hide password' : 'Show password'}
                  className="text-ink-faint transition-colors hover:text-ink"
                >
                  {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            {error != null && (
              <p className="anim-in rounded-lg bg-coral-soft px-3.5 py-2 text-[12.5px] font-medium text-coral-ink">
                {error}
              </p>
            )}

            <Button size="lg" className="w-full" onClick={submit}>
              {mode === 'signin' ? 'Sign in' : 'Create my account'} <ArrowRight size={15} />
            </Button>

            <div className="flex items-center gap-3 py-1">
              <span className="h-px flex-1 bg-line" />
              <span className="text-[11.5px] font-medium text-ink-faint">or</span>
              <span className="h-px flex-1 bg-line" />
            </div>

            <Button
              size="lg"
              variant="soft"
              className="w-full"
              onClick={() => finish('Aditya')}
            >
              <Sparkles size={15} /> Continue as demo learner
            </Button>
            <button
              onClick={() =>
                toast('Single sign-on', 'Google and Apple sign-in arrive with the full release.', 'indigo')
              }
              className="h-11 w-full rounded-xl border bg-card text-[13.5px] font-semibold text-ink-soft transition-all hover:border-line-strong hover:text-ink"
            >
              Continue with Google
            </button>
          </div>

          <p className="mt-6 text-center text-[11px] leading-relaxed text-ink-faint">
            Prototype build — your details stay in this browser only.
            <br />
            By continuing you agree to learn something new today.
          </p>
        </div>
      </main>
    </div>
  )
}
