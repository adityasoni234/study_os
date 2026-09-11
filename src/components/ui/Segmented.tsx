import { cn } from '@/lib/utils'

export function Segmented<T extends string>({
  options,
  value,
  onChange,
  className,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (v: T) => void
  className?: string
}) {
  return (
    <div
      role="radiogroup"
      className={cn('inline-flex rounded-[11px] border bg-paper-deep p-1', className)}
    >
      {options.map((o) => {
        const active = o.value === value
        return (
          <button
            key={o.value}
            role="radio"
            aria-checked={active}
            onClick={() => onChange(o.value)}
            className={cn(
              'h-8 rounded-lg px-3.5 text-[13px] font-medium transition-all duration-200',
              active
                ? 'bg-card text-ink shadow-(--shadow-soft)'
                : 'text-ink-soft hover:text-ink',
            )}
          >
            {o.label}
          </button>
        )
      })}
    </div>
  )
}
