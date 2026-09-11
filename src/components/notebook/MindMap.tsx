import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, PenLine } from 'lucide-react'
import { mindNodes, type MindNode } from '@/data/notebook'
import { useApp } from '@/state/AppContext'
import { Button } from '@/components/ui/Button'
import { masteryTone, toneStroke } from '@/lib/tones'
import { cn } from '@/lib/utils'

function nodeWidth(n: MindNode): number {
  const base = n.kind === 'center' ? 13 : 11
  return Math.max(n.label.length * (base * 0.62) + 34, 90)
}

export function MindMap() {
  const [selectedId, setSelectedId] = useState<string | null>('pr')
  const navigate = useNavigate()
  const { masteryOf } = useApp()

  const nodes = useMemo(
    () =>
      mindNodes.map((n) =>
        n.id === 'pr' ? { ...n, mastery: masteryOf('precision-recall', n.mastery ?? 65) } : n,
      ),
    [masteryOf],
  )

  const byId = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes])
  const selected = selectedId ? byId.get(selectedId) : undefined

  return (
    <div>
      <div className="overflow-x-auto">
        <svg
          viewBox="0 0 860 540"
          className="h-auto w-full min-w-[640px]"
          role="img"
          aria-label="Concept map of Machine Learning topics"
        >
          {/* Edges */}
          {nodes
            .filter((n) => n.parent != null)
            .map((n) => {
              const p = byId.get(n.parent!)!
              const mx = (n.x + p.x) / 2
              const my = (n.y + p.y) / 2
              return (
                <path
                  key={`e-${n.id}`}
                  d={`M ${p.x} ${p.y} Q ${mx} ${my - 18} ${n.x} ${n.y}`}
                  fill="none"
                  stroke="var(--color-line-strong)"
                  strokeWidth={1.5}
                  opacity={0.8}
                />
              )
            })}

          {/* Nodes */}
          {nodes.map((n, i) => {
            const w = nodeWidth(n)
            const h = n.kind === 'center' ? 44 : n.kind === 'branch' ? 36 : 32
            const isSelected = selectedId === n.id
            const stroke =
              n.kind === 'leaf' && n.mastery != null
                ? toneStroke[masteryTone(n.mastery)]
                : toneStroke[n.tone === 'neutral' ? 'neutral' : n.tone]
            return (
              <g
                key={n.id}
                transform={`translate(${n.x - w / 2}, ${n.y - h / 2})`}
                onClick={() => setSelectedId(n.id)}
                className="cursor-pointer"
                style={{ animation: `fade-up 0.5s ${i * 0.04}s cubic-bezier(0.22,1,0.36,1) both` }}
              >
                <rect
                  width={w}
                  height={h}
                  rx={h / 2}
                  fill={n.kind === 'center' ? 'var(--color-indigo)' : 'var(--color-card)'}
                  stroke={n.kind === 'center' ? 'none' : stroke}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  style={{
                    filter: isSelected
                      ? 'drop-shadow(0 4px 10px rgb(91 86 214 / 0.3))'
                      : 'drop-shadow(0 1px 3px rgb(28 30 48 / 0.08))',
                    transition: 'stroke-width 0.15s',
                  }}
                />
                <text
                  x={w / 2}
                  y={h / 2 + 1}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={n.kind === 'center' ? 14 : n.kind === 'branch' ? 12.5 : 11.5}
                  fontWeight={n.kind === 'leaf' ? 600 : 700}
                  fill={n.kind === 'center' ? '#fff' : 'var(--color-ink)'}
                >
                  {n.label}
                </text>
                {n.kind === 'leaf' && n.mastery != null && n.mastery > 0 && (
                  <circle cx={w - 4} cy={4} r={5.5} fill={stroke} stroke="var(--color-card)" strokeWidth={2} />
                )}
              </g>
            )
          })}
        </svg>
      </div>

      {/* Selected node detail */}
      {selected != null && selected.kind === 'leaf' && (
        <div key={selected.id} className="anim-pop mt-2 flex flex-wrap items-center gap-4 rounded-xl border bg-paper p-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2.5">
              <span className="text-[14.5px] font-semibold">{selected.label}</span>
              {selected.mastery != null && selected.mastery > 0 ? (
                <span
                  className={cn(
                    'rounded-full px-2 py-0.5 text-[11px] font-bold tnum',
                    masteryTone(selected.mastery) === 'mint'
                      ? 'bg-mint-soft text-mint-ink'
                      : masteryTone(selected.mastery) === 'indigo'
                        ? 'bg-indigo-soft text-indigo-ink'
                        : 'bg-amber-soft text-amber-ink',
                  )}
                >
                  {selected.mastery}% mastery
                </span>
              ) : (
                <span className="rounded-full bg-paper-deep px-2 py-0.5 text-[11px] font-bold text-ink-faint">
                  Not started
                </span>
              )}
            </div>
            <p className="mt-1 text-[12.5px] text-ink-soft">{selected.summary}</p>
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={() => navigate(`/tutor/${selected.topicId}`)}>
              <GraduationCap size={13} /> Learn
            </Button>
            <Button size="sm" variant="secondary" onClick={() => navigate(`/quiz/${selected.topicId}`)}>
              <PenLine size={13} /> Practice
            </Button>
          </div>
        </div>
      )}
      <p className="mt-3 text-center text-[11.5px] text-ink-faint">
        Built from your sources · colors show mastery — mint mastered, indigo learning, amber needs work
      </p>
    </div>
  )
}
