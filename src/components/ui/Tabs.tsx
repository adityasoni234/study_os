import { cn } from '@/lib/utils'

export interface TabItem {
  id: string
  label: string
  icon?: React.ReactNode
}

export function PillTabs({
  tabs,
  active,
  onChange,
  className,
}: {
  tabs: TabItem[]
  active: string
  onChange: (id: string) => void
  className?: string
}) {
  return (
    <div
      role="tablist"
      className={cn('flex flex-wrap items-center gap-1.5', className)}
    >
      {tabs.map((t) => {
        const isActive = t.id === active
        return (
          <button
            key={t.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(t.id)}
            className={cn(
              'inline-flex h-8.5 items-center gap-1.5 rounded-full px-3.5 text-[13px] font-medium transition-all duration-200',
              isActive
                ? 'bg-ink text-paper shadow-(--shadow-soft)'
                : 'text-ink-soft hover:bg-paper-deep hover:text-ink',
            )}
          >
            {t.icon}
            {t.label}
          </button>
        )
      })}
    </div>
  )
}

export function UnderlineTabs({
  tabs,
  active,
  onChange,
  className,
}: {
  tabs: TabItem[]
  active: string
  onChange: (id: string) => void
  className?: string
}) {
  return (
    <div role="tablist" className={cn('flex items-center gap-1 overflow-x-auto border-b', className)}>
      {tabs.map((t) => {
        const isActive = t.id === active
        return (
          <button
            key={t.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(t.id)}
            className={cn(
              'relative inline-flex h-10 shrink-0 items-center gap-1.5 px-3 text-[13.5px] font-medium transition-colors duration-200',
              isActive ? 'text-indigo-ink' : 'text-ink-soft hover:text-ink',
            )}
          >
            {t.icon}
            {t.label}
            <span
              className={cn(
                'absolute inset-x-2 -bottom-px h-0.5 rounded-full transition-all duration-200',
                isActive ? 'bg-indigo' : 'bg-transparent',
              )}
            />
          </button>
        )
      })}
    </div>
  )
}
