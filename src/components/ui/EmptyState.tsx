import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export function EmptyState({
  icon,
  title,
  desc,
  action,
  className,
}: {
  icon: ReactNode
  title: string
  desc?: string
  action?: ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-2xl border border-dashed border-line-strong bg-paper-deep/40 px-6 py-12 text-center',
        className,
      )}
    >
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-card text-ink-faint shadow-(--shadow-soft)">
        {icon}
      </div>
      <div className="text-[15px] font-semibold">{title}</div>
      {desc != null && <p className="mt-1 max-w-sm text-[13.5px] text-ink-soft">{desc}</p>}
      {action != null && <div className="mt-4">{action}</div>}
    </div>
  )
}
