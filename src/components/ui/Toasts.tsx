import { CheckCircle2, Info, Sparkles, X } from 'lucide-react'
import { useApp } from '@/state/AppContext'
import { toneSoftBg, toneText } from '@/lib/tones'
import { cn } from '@/lib/utils'

export function Toasts() {
  const { toasts, dismissToast } = useApp()
  if (toasts.length === 0) return null
  return (
    <div className="pointer-events-none fixed right-4 bottom-20 z-[60] flex w-[min(360px,calc(100vw-2rem))] flex-col gap-2 lg:bottom-6">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="anim-toast pointer-events-auto flex items-start gap-3 rounded-xl border bg-card p-3.5 shadow-(--shadow-lift)"
          role="status"
        >
          <span
            className={cn(
              'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full',
              toneSoftBg[t.tone],
              toneText[t.tone],
            )}
          >
            {t.tone === 'mint' ? (
              <CheckCircle2 size={15} />
            ) : t.tone === 'violet' ? (
              <Sparkles size={14} />
            ) : (
              <Info size={14} />
            )}
          </span>
          <div className="min-w-0 flex-1">
            <div className="text-[13.5px] leading-snug font-semibold">{t.title}</div>
            {t.desc != null && (
              <div className="mt-0.5 text-[12.5px] leading-snug text-ink-soft">{t.desc}</div>
            )}
          </div>
          <button
            aria-label="Dismiss"
            onClick={() => dismissToast(t.id)}
            className="rounded-md p-1 text-ink-faint transition-colors hover:bg-paper-deep hover:text-ink"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  )
}
