import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle,
  Bookmark,
  CalendarDays,
  Check,
  ExternalLink,
  MapPin,
  Radar,
  Users,
} from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Ring } from '@/components/ui/Progress'
import { PillTabs } from '@/components/ui/Tabs'
import { EmptyState } from '@/components/ui/EmptyState'
import { opportunities } from '@/data/opportunities'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'
import type { Opportunity } from '@/types'

const tabs = [
  { id: 'best', label: 'Best match' },
  { id: 'closing', label: 'Closing soon' },
  { id: 'new', label: 'New' },
  { id: 'saved', label: 'Saved' },
]

function OpportunityCard({ opp }: { opp: Opportunity }) {
  const { state, toggleSaved, toast } = useApp()
  const saved = state.saved.includes(opp.id)
  const urgent = opp.daysLeft != null && opp.daysLeft <= 10

  return (
    <Card hover={false} className="transition-shadow duration-200 hover:shadow-(--shadow-lift)">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={opp.tone}>{opp.type}</Badge>
            {urgent && (
              <Badge tone="amber">
                <CalendarDays size={10} /> {opp.daysLeft} days left
              </Badge>
            )}
          </div>
          <h3 className="mt-2.5 text-[16px] leading-snug font-semibold">{opp.title}</h3>
          <div className="mt-0.5 text-[12.5px] font-medium text-ink-soft">{opp.org}</div>
          <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">{opp.blurb}</p>

          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[12px] text-ink-soft">
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays size={12.5} className="text-ink-faint" /> {opp.deadline}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <MapPin size={12.5} className="text-ink-faint" /> {opp.mode}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Users size={12.5} className="text-ink-faint" /> {opp.eligibility}
            </span>
          </div>

          <div className="mt-3">
            <div className="mb-1.5 text-[11px] font-bold tracking-[0.08em] text-ink-faint uppercase">
              Why it matches you
            </div>
            <div className="flex flex-wrap gap-1.5">
              {opp.matches.map((m) => (
                <span
                  key={m.label}
                  className={cn(
                    'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11.5px] font-medium',
                    m.ok ? 'bg-mint-soft text-mint-ink' : 'bg-amber-soft text-amber-ink',
                  )}
                >
                  {m.ok ? <Check size={11} strokeWidth={3} /> : <AlertCircle size={11} />}
                  {m.label}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-row items-center gap-3 sm:flex-col sm:items-end">
          <div className="flex flex-col items-center">
            <Ring value={opp.match} size={62} stroke={6} tone={opp.match >= 85 ? 'mint' : 'indigo'}>
              <span className="text-[13px] font-bold tnum">{opp.match}%</span>
            </Ring>
            <span className="mt-1 text-[10.5px] font-semibold text-ink-faint">match</span>
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t pt-3.5">
        <span className="inline-flex items-center gap-1.5 text-[11.5px] text-ink-faint">
          Source: <span className="font-semibold text-ink-soft">{opp.source}</span>
          <ExternalLink size={11} />
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              toggleSaved(opp.id)
              if (!saved) toast('Saved', 'Find it any time in the Saved tab.', 'indigo')
            }}
            aria-pressed={saved}
            aria-label={saved ? 'Remove from saved' : 'Save opportunity'}
            className={cn(
              'flex h-9 w-9 items-center justify-center rounded-[10px] border transition-all',
              saved
                ? 'border-indigo bg-indigo-soft text-indigo-ink'
                : 'text-ink-faint hover:border-indigo/40 hover:text-indigo-ink',
            )}
          >
            <Bookmark size={15} fill={saved ? 'currentColor' : 'none'} />
          </button>
          <Button
            variant="secondary"
            size="md"
            onClick={() => toast('Opening source', `In the full release this opens ${opp.source} in a new tab.`, 'indigo')}
          >
            View
          </Button>
          {opp.id === 'hackathon-ai-ed' ? (
            <Link to={`/opportunities/${opp.id}/prepare`}>
              <Button size="md">
                <Radar size={14} /> Prepare me
              </Button>
            </Link>
          ) : (
            <Link to={`/opportunities/${opp.id}/prepare`}>
              <Button size="md" variant="soft">
                <Radar size={14} /> Prepare me
              </Button>
            </Link>
          )}
        </div>
      </div>
    </Card>
  )
}

export default function Opportunities() {
  const [tab, setTab] = useState('best')
  const { state } = useApp()

  const list = useMemo(() => {
    switch (tab) {
      case 'closing':
        return [...opportunities].sort(
          (a, b) => (a.daysLeft ?? 999) - (b.daysLeft ?? 999),
        )
      case 'new':
        return [...opportunities].slice(0, 3)
      case 'saved':
        return opportunities.filter((o) => state.saved.includes(o.id))
      default:
        return [...opportunities].sort((a, b) => b.match - a.match)
    }
  }, [tab, state.saved])

  return (
    <Page>
      <PageHeader
        title="Opportunity Radar"
        sub="Real-world opportunities matched to what you’re learning right now — with a plan to get you ready."
      />

      <PillTabs tabs={tabs} active={tab} onChange={setTab} className="mb-5" />

      {list.length === 0 ? (
        <EmptyState
          icon={<Bookmark size={20} />}
          title="Nothing saved yet"
          desc="Tap the bookmark on any opportunity and it will wait for you here."
        />
      ) : (
        <div className="space-y-4">
          {list.map((opp, i) => (
            <div key={opp.id} className={cn('anim-in', `anim-d-${Math.min(i + 1, 5)}`)}>
              <OpportunityCard opp={opp} />
            </div>
          ))}
        </div>
      )}

      <p className="mt-6 text-center text-[11.5px] text-ink-faint">
        Matches are based on your roadmaps, mastery and goals · always verify details on the official source
      </p>
    </Page>
  )
}
