import { useState, type ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Collapse({
  title,
  icon,
  defaultOpen = false,
  children,
  subtitle,
}: {
  title: string
  icon?: ReactNode
  subtitle?: string
  defaultOpen?: boolean
  children: ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="overflow-hidden rounded-xl border bg-card">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3.5 text-left transition-colors hover:bg-paper-deep/50"
      >
        {icon != null && (
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[10px] bg-indigo-soft text-indigo-ink">
            {icon}
          </span>
        )}
        <span className="min-w-0 flex-1">
          <span className="block text-[14.5px] font-semibold">{title}</span>
          {subtitle != null && (
            <span className="block truncate text-[12.5px] text-ink-faint">{subtitle}</span>
          )}
        </span>
        <ChevronDown
          size={17}
          className={cn('shrink-0 text-ink-faint transition-transform duration-300', open && 'rotate-180')}
        />
      </button>
      <div
        className={cn(
          'grid transition-all duration-300 ease-out',
          open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
        )}
      >
        <div className="overflow-hidden">
          <div className="border-t px-4 py-4">{children}</div>
        </div>
      </div>
    </div>
  )
}
