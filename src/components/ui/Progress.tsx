import type { ReactNode } from 'react'
import type { Tone } from '@/types'
import { toneBg, toneStroke } from '@/lib/tones'
import { cn, clamp } from '@/lib/utils'

export function ProgressBar({
  value,
  tone = 'indigo',
  className,
  trackClassName,
}: {
  value: number
  tone?: Tone
  className?: string
  trackClassName?: string
}) {
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(value)}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn('h-1.5 w-full overflow-hidden rounded-full bg-paper-deep', trackClassName, className)}
    >
      <div
        className={cn('h-full rounded-full transition-all duration-700 ease-out', toneBg[tone])}
        style={{ width: `${clamp(value, 0, 100)}%` }}
      />
    </div>
  )
}

export function Ring({
  value,
  size = 56,
  stroke = 5,
  tone = 'indigo',
  children,
  className,
}: {
  value: number
  size?: number
  stroke?: number
  tone?: Tone
  children?: ReactNode
  className?: string
}) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c * (1 - clamp(value, 0, 100) / 100)
  return (
    <div
      className={cn('relative inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
      role="img"
      aria-label={`${Math.round(value)}%`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-paper-deep)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={toneStroke[tone]}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.9s cubic-bezier(0.22, 1, 0.36, 1)' }}
        />
      </svg>
      {children != null && (
        <div className="absolute inset-0 flex items-center justify-center">{children}</div>
      )}
    </div>
  )
}
