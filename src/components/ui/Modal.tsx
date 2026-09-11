import { useEffect, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { IconButton } from './Button'

export function Modal({
  open,
  onClose,
  children,
  title,
  wide = false,
  sheetOnMobile = true,
}: {
  open: boolean
  onClose: () => void
  children: ReactNode
  title?: string
  wide?: boolean
  sheetOnMobile?: boolean
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <div
      className={cn(
        'fixed inset-0 z-50 flex justify-center',
        sheetOnMobile ? 'items-end sm:items-center' : 'items-center',
      )}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <button
        aria-label="Close"
        className="anim-fade absolute inset-0 cursor-default bg-ink/25 backdrop-blur-[2px]"
        onClick={onClose}
      />
      <div
        className={cn(
          'anim-pop relative max-h-[88dvh] w-full overflow-y-auto bg-card shadow-(--shadow-lift)',
          sheetOnMobile
            ? 'rounded-t-2xl sm:rounded-2xl'
            : 'rounded-2xl',
          wide ? 'sm:max-w-2xl' : 'sm:max-w-lg',
          'border',
        )}
      >
        {title != null && (
          <div className="sticky top-0 z-10 flex items-center justify-between border-b bg-card/95 px-5 py-3.5 backdrop-blur">
            <h2 className="text-[15.5px] font-semibold">{title}</h2>
            <IconButton label="Close" onClick={onClose}>
              <X size={17} />
            </IconButton>
          </div>
        )}
        <div className="p-5">{children}</div>
      </div>
    </div>,
    document.body,
  )
}
