import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface Props extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  padded?: boolean
}

export function Card({ hover = false, padded = true, className, children, ...rest }: Props) {
  return (
    <div
      className={cn(
        'rounded-2xl border bg-card shadow-(--shadow-soft)',
        padded && 'p-5',
        hover &&
          'transition-all duration-200 hover:-translate-y-0.5 hover:border-indigo/35 hover:shadow-(--shadow-lift)',
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  )
}

export function Eyebrow({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'text-[11.5px] font-semibold uppercase tracking-[0.09em] text-ink-faint',
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  )
}

export function SectionHeader({
  title,
  action,
  className,
}: {
  title: string
  action?: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('mb-3.5 flex items-center justify-between', className)}>
      <Eyebrow>{title}</Eyebrow>
      {action}
    </div>
  )
}
