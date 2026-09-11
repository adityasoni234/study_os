import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flame, Globe, LogOut, RotateCcw, ShieldCheck } from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, SectionHeader } from '@/components/ui/Card'
import { Segmented } from '@/components/ui/Segmented'
import { useApp } from '@/state/AppContext'
import { initials } from '@/lib/utils'

export default function Settings() {
  const { state, resetDemo, signOut, toast } = useApp()
  const navigate = useNavigate()
  const [style, setStyle] = useState<'Simple' | 'Visual' | 'Technical'>('Visual')
  const [goal, setGoal] = useState<'15' | '25' | '45'>('25')
  const [confirmReset, setConfirmReset] = useState(false)

  return (
    <Page className="max-w-[720px]">
      <PageHeader title="Settings" sub="Your profile and how your tutor teaches you." />

      <Card className="flex items-center gap-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo to-violet text-[20px] font-bold text-white">
          {initials(state.auth.name)}
        </span>
        <div className="min-w-0 flex-1">
          <div className="text-[16px] font-semibold">{state.auth.name}</div>
          <div className="text-[12.5px] text-ink-soft">Learner · StudyOS</div>
        </div>
        <span className="flex items-center gap-1.5 rounded-full bg-amber-soft px-3 py-1.5 text-[12px] font-semibold text-amber-ink">
          <Flame size={13} /> 12-day streak
        </span>
      </Card>

      <section className="mt-7">
        <SectionHeader title="Learning preferences" />
        <Card className="space-y-5">
          <div>
            <div className="mb-1.5 text-[13.5px] font-semibold">Preferred explanation style</div>
            <p className="mb-2 text-[12px] text-ink-faint">
              Your tutor adapts anyway — this sets the starting point.
            </p>
            <Segmented
              options={[
                { value: 'Simple', label: 'Simple first' },
                { value: 'Visual', label: 'Visual first' },
                { value: 'Technical', label: 'Technical first' },
              ]}
              value={style}
              onChange={(v) => {
                setStyle(v)
                toast('Preference saved', `New sessions will start ${v.toLowerCase()}-first.`, 'mint')
              }}
            />
          </div>
          <div>
            <div className="mb-2 text-[13.5px] font-semibold">Daily learning goal</div>
            <Segmented
              options={[
                { value: '15', label: '15 min' },
                { value: '25', label: '25 min' },
                { value: '45', label: '45 min' },
              ]}
              value={goal}
              onChange={(v) => {
                setGoal(v)
                toast('Goal updated', `Missions will aim for about ${v} minutes a day.`, 'mint')
              }}
            />
          </div>
        </Card>
      </section>

      <section className="mt-7">
        <SectionHeader title="Data" />
        <Card className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-[13.5px] font-semibold">Reset demo data</div>
            <div className="text-[12.5px] text-ink-soft">
              Returns mastery, missions and saved items to their starting state.
            </div>
          </div>
          {confirmReset ? (
            <div className="flex gap-2">
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  resetDemo()
                  setConfirmReset(false)
                  toast('Fresh start', 'Everything is back to the beginning.', 'indigo')
                }}
              >
                Yes, reset
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setConfirmReset(false)}>
                Keep my progress
              </Button>
            </div>
          ) : (
            <Button variant="secondary" size="sm" onClick={() => setConfirmReset(true)}>
              <RotateCcw size={13} /> Reset
            </Button>
          )}
        </Card>
        <Card className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-[13.5px] font-semibold">Sign out</div>
            <div className="text-[12.5px] text-ink-soft">
              Your progress stays saved on this device.
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              signOut()
              navigate('/welcome')
            }}
          >
            <LogOut size={13} /> Sign out
          </Button>
        </Card>
      </section>

      <section className="mt-7">
        <SectionHeader title="About StudyOS" />
        <Card className="space-y-3 text-[13px] leading-relaxed text-ink-soft">
          <div className="flex items-start gap-2.5">
            <Globe size={15} className="mt-0.5 shrink-0 text-indigo-ink" />
            <span>
              StudyOS is built for <strong className="font-semibold text-ink">UN SDG 4 — Quality Education</strong>:
              inclusive, personalised learning with a path to real-world opportunity.
            </span>
          </div>
          <div className="flex items-start gap-2.5">
            <ShieldCheck size={15} className="mt-0.5 shrink-0 text-mint-ink" />
            <span>
              Answers cite your sources wherever possible, uncertainty is admitted honestly, and
              wellbeing support is a companion — never a substitute for professional care.
            </span>
          </div>
          <div className="border-t pt-3 text-[11.5px] text-ink-faint">
            StudyOS prototype · v1.0 · “Learn anything. Grow every day.”
          </div>
        </Card>
      </section>
    </Page>
  )
}
