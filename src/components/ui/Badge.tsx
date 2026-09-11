import type { HTMLAttributes, ReactNode } from 'react'
import type { Tone } from '@/types'
import { toneSoftBg, toneText } from '@/lib/tones'
import { cn } from '@/lib/utils'

export function Badge({
  tone = 'neutral',
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11.5px] font-semibold',
        toneSoftBg[tone],
        toneText[tone],
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  )
}

export function MetaChip({
  icon,
  children,
  className,
}: {
  icon?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 text-[12.5px] font-medium text-ink-soft',
        className,
      )}
    >
      {icon}
      {children}
    </span>
  )
}
