import type { Tone } from '@/types'

export const toneBg: Record<Tone, string> = {
  indigo: 'bg-indigo',
  violet: 'bg-violet',
  mint: 'bg-mint',
  amber: 'bg-amber',
  coral: 'bg-coral',
  sky: 'bg-sky',
  neutral: 'bg-ink-faint',
}

export const toneSoftBg: Record<Tone, string> = {
  indigo: 'bg-indigo-soft',
  violet: 'bg-violet-soft',
  mint: 'bg-mint-soft',
  amber: 'bg-amber-soft',
  coral: 'bg-coral-soft',
  sky: 'bg-sky-soft',
  neutral: 'bg-paper-deep',
}

export const toneText: Record<Tone, string> = {
  indigo: 'text-indigo-ink',
  violet: 'text-violet-ink',
  mint: 'text-mint-ink',
  amber: 'text-amber-ink',
  coral: 'text-coral-ink',
  sky: 'text-sky-ink',
  neutral: 'text-ink-soft',
}

export const toneStroke: Record<Tone, string> = {
  indigo: 'var(--color-indigo)',
  violet: 'var(--color-violet)',
  mint: 'var(--color-mint)',
  amber: 'var(--color-amber)',
  coral: 'var(--color-coral)',
  sky: 'var(--color-sky)',
  neutral: 'var(--color-ink-faint)',
}

export function masteryTone(value: number): Tone {
  if (value >= 80) return 'mint'
  if (value >= 55) return 'indigo'
  if (value > 0) return 'amber'
  return 'neutral'
}
