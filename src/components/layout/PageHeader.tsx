import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export function Page({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('mx-auto w-full max-w-[1400px] px-4 py-6 sm:px-6 lg:px-10 lg:py-9', className)}>
      {children}
    </div>
  )
}

export function PageHeader({
  title,
  sub,
  right,
  className,
}: {
  title: ReactNode
  sub?: ReactNode
  right?: ReactNode
  className?: string
}) {
  return (
    <div className={cn('mb-7 flex flex-wrap items-end justify-between gap-4', className)}>
      <div>
        <h1 className="font-display text-[26px] leading-tight font-semibold tracking-[-0.01em] lg:text-[30px]">
          {title}
        </h1>
        {sub != null && <p className="mt-1.5 max-w-xl text-[14px] text-ink-soft">{sub}</p>}
      </div>
      {right != null && <div className="flex items-center gap-2">{right}</div>}
    </div>
  )
}
