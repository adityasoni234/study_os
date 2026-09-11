import { Fragment, useState } from 'react'
import { FileText, Lightbulb, Sparkles, Youtube } from 'lucide-react'
import type { TutorBlock } from '@/types'
import { citations } from '@/data/notebook'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { toneSoftBg, toneText } from '@/lib/tones'
import { cn, rich } from '@/lib/utils'
import { Link } from 'react-router-dom'

/** Colors TP/FP/FN/TN tokens inside formulas. */
function Formula({ expression }: { expression: string }) {
  const parts = expression.split(/(TP|FP|FN|TN)/g)
  return (
    <span className="font-semibold tracking-wide">
      {parts.map((p, i) => {
        const cls =
          p === 'TP'
            ? 'text-mint-ink'
            : p === 'FP'
              ? 'text-amber-ink'
              : p === 'FN'
                ? 'text-coral-ink'
                : p === 'TN'
                  ? 'text-ink-faint'
                  : ''
        return cls ? (
          <span key={i} className={cls}>
            {p}
          </span>
        ) : (
          <Fragment key={i}>{p}</Fragment>
        )
      })}
    </span>
  )
}

function ConfusionTable({ variant }: { variant: 'confusion' | 'precision-col' | 'recall-row' }) {
  const highlightCol = variant === 'precision-col'
  const highlightRow = variant === 'recall-row'
  const cell = 'px-3 py-2 text-center text-[12.5px] font-semibold rounded-lg'
  return (
    <div className="my-1">
      {variant !== 'confusion' && (
        <div className="mb-1.5 text-[11.5px] font-semibold tracking-wide text-ink-faint uppercase">
          {highlightCol ? 'Precision lives in the “predicted positive” column' : 'Recall lives in the “actual positive” row'}
        </div>
      )}
      <div className="inline-grid grid-cols-[auto_1fr_1fr] gap-1 rounded-xl border bg-paper p-2.5">
        <div />
        <div className={cn('px-2 text-center text-[11px] font-bold text-ink-faint uppercase', highlightCol && 'text-indigo-ink')}>
          Predicted +
        </div>
        <div className="px-2 text-center text-[11px] font-bold text-ink-faint uppercase">Predicted −</div>

        <div className={cn('flex items-center pr-2 text-[11px] font-bold text-ink-faint uppercase', highlightRow && 'text-mint-ink')}>
          Actual +
        </div>
        <div className={cn(cell, 'bg-mint-soft text-mint-ink', (highlightCol || highlightRow) && 'ring-2 ring-mint/40')}>
          TP
        </div>
        <div className={cn(cell, 'bg-coral-soft text-coral-ink', highlightRow && 'ring-2 ring-mint/40')}>FN</div>

        <div className="flex items-center pr-2 text-[11px] font-bold text-ink-faint uppercase">Actual −</div>
        <div className={cn(cell, 'bg-amber-soft text-amber-ink', highlightCol && 'ring-2 ring-indigo/30')}>FP</div>
        <div className={cn(cell, 'bg-paper-deep text-ink-faint')}>TN</div>
      </div>
    </div>
  )
}

export function CitationChip({
  label,
  sourceId,
}: {
  label: string
  sourceId?: string
}) {
  const [open, setOpen] = useState(false)
  const info = sourceId ? citations[sourceId] : undefined
  const isVideo = label.toLowerCase().includes('statquest')
  return (
    <>
      <button
        onClick={() => info && setOpen(true)}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full border bg-paper px-2.5 py-1 text-[11.5px] font-medium text-ink-soft',
          'transition-all duration-150 hover:border-indigo/50 hover:text-indigo-ink',
        )}
      >
        {isVideo ? <Youtube size={11} className="text-coral" /> : <FileText size={11} />}
        {label}
      </button>
      {info && (
        <Modal open={open} onClose={() => setOpen(false)} title={info.title}>
          <p className="text-[14px] leading-relaxed text-ink-soft">
            {info.excerpt.split(info.highlight).map((part, i, arr) => (
              <Fragment key={i}>
                {part}
                {i < arr.length - 1 && (
                  <mark className="rounded bg-indigo-soft px-0.5 text-indigo-ink">
                    {info.highlight}
                  </mark>
                )}
              </Fragment>
            ))}
          </p>
          <div className="mt-4 flex justify-end">
            <Link to="/notebook" onClick={() => setOpen(false)}>
              <Button variant="soft" size="sm">
                Open in Notebook
              </Button>
            </Link>
          </div>
        </Modal>
      )}
    </>
  )
}

export function BlockRenderer({ block }: { block: TutorBlock }) {
  switch (block.kind) {
    case 'p':
      return <p className="text-[14.5px] leading-[1.7] text-ink">{rich(block.text)}</p>

    case 'callout':
      return (
        <div className={cn('rounded-xl p-3.5', toneSoftBg[block.tone])}>
          <div className={cn('text-[13px] leading-snug font-semibold', toneText[block.tone])}>
            {block.title}
          </div>
          <p className="mt-1 text-[13.5px] leading-relaxed text-ink-soft">{rich(block.text)}</p>
          {block.formula != null && (
            <div className="mt-2 inline-block rounded-lg bg-card/80 px-3 py-1.5 text-[13px]">
              <Formula expression={block.formula} />
            </div>
          )}
        </div>
      )

    case 'formula':
      return (
        <div className="flex items-center gap-3 rounded-xl border bg-paper px-4 py-2.5">
          <span className="text-[11px] font-bold tracking-wide text-ink-faint uppercase">
            {block.label}
          </span>
          <span className="text-[14px]">
            <Formula expression={block.expression} />
          </span>
        </div>
      )

    case 'table':
      return <ConfusionTable variant={block.variant} />

    case 'example':
      return (
        <div className="rounded-xl border border-sky-soft bg-sky-soft/40 p-3.5">
          <div className="flex items-center gap-1.5 text-[12.5px] font-semibold text-sky-ink">
            <Lightbulb size={13} /> {block.title}
          </div>
          <p className="mt-1.5 text-[13.5px] leading-relaxed whitespace-pre-line text-ink-soft">
            {rich(block.text)}
          </p>
        </div>
      )

    case 'tip':
      return (
        <div className="flex items-start gap-2.5 rounded-xl bg-violet-soft/70 p-3.5">
          <Sparkles size={14} className="mt-0.5 shrink-0 text-violet-ink" />
          <p className="text-[13.5px] leading-relaxed text-violet-ink">{rich(block.text)}</p>
        </div>
      )

    case 'code':
      return (
        <pre className="overflow-x-auto rounded-xl bg-ink p-3.5 text-[12px] leading-relaxed text-[#E8E6F5]">
          <code>{block.code}</code>
        </pre>
      )

    case 'cite':
      return <CitationChip label={block.label} sourceId={block.sourceId} />

    default:
      return null
  }
}

export function Blocks({ blocks }: { blocks: TutorBlock[] }) {
  // Group consecutive cite blocks onto one row.
  const grouped: (TutorBlock | TutorBlock[])[] = []
  for (const b of blocks) {
    const last = grouped[grouped.length - 1]
    if (b.kind === 'cite' && Array.isArray(last) && last[0]?.kind === 'cite') {
      last.push(b)
    } else if (b.kind === 'cite') {
      grouped.push([b])
    } else {
      grouped.push(b)
    }
  }
  return (
    <div className="space-y-3">
      {grouped.map((g, i) =>
        Array.isArray(g) ? (
          <div key={i} className="flex flex-wrap gap-1.5">
            {g.map((c, j) => (
              <BlockRenderer key={j} block={c} />
            ))}
          </div>
        ) : (
          <BlockRenderer key={i} block={g} />
        ),
      )}
    </div>
  )
}
