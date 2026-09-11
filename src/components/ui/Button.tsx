import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

type Variant = 'primary' | 'secondary' | 'soft' | 'ghost' | 'violet' | 'mint' | 'danger' | 'light'
type Size = 'sm' | 'md' | 'lg'

const variants: Record<Variant, string> = {
  primary:
    'bg-indigo text-white hover:bg-indigo-deep shadow-[0_1px_2px_rgb(28_30_48/0.12),0_6px_16px_-6px_rgb(91_86_214/0.45)]',
  secondary: 'bg-card text-ink border border-line-strong hover:border-indigo/50 hover:text-indigo-ink',
  soft: 'bg-indigo-soft text-indigo-ink hover:bg-[#e2e1f8]',
  ghost: 'bg-transparent text-ink-soft hover:bg-paper-deep hover:text-ink',
  violet: 'bg-violet text-white hover:bg-[#6c4be0]',
  mint: 'bg-mint text-white hover:bg-[#0e8069]',
  danger: 'bg-coral-soft text-coral-ink hover:bg-[#f7e0dc]',
  /** For use on saturated/dark surfaces. */
  light: 'bg-white text-indigo-ink hover:bg-white/90 shadow-(--shadow-soft)',
}

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3 text-[13px] gap-1.5 rounded-[9px]',
  md: 'h-10 px-4 text-[13.5px] gap-2 rounded-[10px]',
  lg: 'h-11 px-5 text-[14.5px] gap-2 rounded-xl',
}

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  children?: ReactNode
}

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'primary', size = 'md', className, children, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center font-semibold whitespace-nowrap select-none',
        'transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  )
})

export function IconButton({
  label,
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { label: string }) {
  return (
    <button
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-ink-soft',
        'transition-all duration-200 hover:bg-paper-deep hover:text-ink active:scale-95',
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  )
}
