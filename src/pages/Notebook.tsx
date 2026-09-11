import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  ArrowRight,
  BookOpen,
  FileText,
  Globe,
  Headphones,
  Layers,
  Loader2,
  MessageCircle,
  PenLine,
  Plus,
  StickyNote,
  Upload,
  Youtube,
  Zap,
} from 'lucide-react'
import { Page, PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Modal } from '@/components/ui/Modal'
import { UnderlineTabs } from '@/components/ui/Tabs'
import { GroundedChat } from '@/components/notebook/GroundedChat'
import { StudyGuide } from '@/components/notebook/StudyGuide'
import { MindMap } from '@/components/notebook/MindMap'
import { Flashcards } from '@/components/notebook/Flashcards'
import { StudyCast } from '@/components/notebook/StudyCast'
import { initialSources } from '@/data/notebook'
import { useApp } from '@/state/AppContext'
import { cn } from '@/lib/utils'
import type { SourceItem, SourceKind } from '@/types'

const kindMeta: Record<SourceKind, { icon: React.ReactNode; cls: string; label: string }> = {
  pdf: { icon: <FileText size={16} />, cls: 'bg-coral-soft text-coral-ink', label: 'PDF' },
  web: { icon: <Globe size={16} />, cls: 'bg-sky-soft text-sky-ink', label: 'Web' },
  youtube: { icon: <Youtube size={16} />, cls: 'bg-coral-soft text-coral-ink', label: 'YouTube' },
  notes: { icon: <StickyNote size={16} />, cls: 'bg-amber-soft text-amber-ink', label: 'Notes' },
}

function AddSourceModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [kind, setKind] = useState<SourceKind>('pdf')
  const [title, setTitle] = useState('')
  const { addSource, markSourceReady, toast } = useApp()

  const submit = () => {
    const finalTitle =
      title.trim() ||
      (kind === 'pdf'
        ? 'ML Course Notes — Unit 4: Decision Trees'
        : kind === 'youtube'
          ? 'StatQuest — ROC and AUC, Clearly Explained'
          : kind === 'web'
            ? 'scikit-learn — Decision Trees Guide'
            : 'My revision notes — Week 7')
    const id = addSource({
      title: finalTitle,
      kind,
      meta: `${kindMeta[kind].label} · Added just now`,
    })
    onClose()
    setTitle('')
    toast('Understanding your material…', 'This usually takes a few seconds.', 'indigo')
    window.setTimeout(() => {
      markSourceReady(id)
      toast('This source is ready', 'Chat, quiz, flashcards and more are now grounded in it.', 'mint')
    }, 2800)
  }

  return (
    <Modal open={open} onClose={onClose} title="Add a source">
      <div className="grid grid-cols-4 gap-2">
        {(Object.keys(kindMeta) as SourceKind[]).map((k) => (
          <button
            key={k}
            onClick={() => setKind(k)}
            className={cn(
              'flex flex-col items-center gap-1.5 rounded-xl border py-3 text-[12px] font-semibold transition-all',
              kind === k
                ? 'border-indigo bg-indigo-soft text-indigo-ink'
                : 'text-ink-soft hover:border-line-strong',
            )}
          >
            {kindMeta[k].icon}
            {kindMeta[k].label}
          </button>
        ))}
      </div>

      {kind === 'pdf' || kind === 'notes' ? (
        <button
          onClick={submit}
          className="mt-4 flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed border-line-strong bg-paper py-8 transition-colors hover:border-indigo/50 hover:bg-indigo-mist"
        >
          <Upload size={20} className="text-ink-faint" />
          <span className="text-[13.5px] font-semibold">Drop a file here or click to browse</span>
          <span className="text-[11.5px] text-ink-faint">PDF, DOCX, TXT · up to 50 MB</span>
        </button>
      ) : (
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder={kind === 'youtube' ? 'Paste a YouTube link…' : 'Paste a web page URL…'}
          className="mt-4 h-11 w-full rounded-xl border bg-paper px-4 text-[14px] outline-none transition-colors focus:border-indigo"
        />
      )}

      <div className="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={submit}>
          <Plus size={15} /> Add source
        </Button>
      </div>
    </Modal>
  )
}

function SourceCard({ source, active, onClick }: { source: SourceItem; active: boolean; onClick: () => void }) {
  const meta = kindMeta[source.kind]
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex w-full items-start gap-3 rounded-xl border bg-card p-3 text-left transition-all duration-200',
        'hover:border-indigo/40 hover:shadow-(--shadow-soft)',
        active && 'border-indigo ring-2 ring-indigo/15',
      )}
    >
      <span className={cn('flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px]', meta.cls)}>
        {meta.icon}
      </span>
      <span className="min-w-0 flex-1">
        <span className="line-clamp-2 text-[13px] leading-snug font-semibold">{source.title}</span>
        <span className="mt-0.5 block text-[11.5px] text-ink-faint">{source.meta}</span>
        {source.status === 'processing' && (
          <span className="mt-1.5 inline-flex items-center gap-1.5 rounded-full bg-indigo-soft px-2 py-0.5 text-[10.5px] font-semibold text-indigo-ink">
            <Loader2 size={10} className="animate-spin" /> Understanding your material…
          </span>
        )}
      </span>
    </button>
  )
}

const tabs = [
  { id: 'chat', label: 'Chat', icon: <MessageCircle size={14} /> },
  { id: 'guide', label: 'Study Guide', icon: <BookOpen size={14} /> },
  { id: 'map', label: 'Mind Map', icon: <Layers size={14} /> },
  { id: 'quiz', label: 'Quiz', icon: <PenLine size={14} /> },
  { id: 'cards', label: 'Flashcards', icon: <Zap size={14} /> },
  { id: 'cast', label: 'StudyCast', icon: <Headphones size={14} /> },
]

export default function Notebook() {
  const [params, setParams] = useSearchParams()
  const [tab, setTab] = useState(params.get('tab') ?? 'chat')
  const [addOpen, setAddOpen] = useState(false)
  const [activeSource, setActiveSource] = useState<string | null>(null)
  const { state } = useApp()

  useEffect(() => {
    if (params.get('add') === '1') {
      setAddOpen(true)
      params.delete('add')
      setParams(params, { replace: true })
    }
  }, [params, setParams])

  const sources = useMemo(() => [...state.extraSources, ...initialSources], [state.extraSources])

  return (
    <Page>
      <PageHeader
        title="My Notebook"
        sub="Your materials, understood — every source becomes chats, guides, maps, quizzes and more."
        right={
          <Button onClick={() => setAddOpen(true)}>
            <Plus size={16} /> Add Source
          </Button>
        }
      />

      <div className="grid gap-5 lg:grid-cols-[270px_1fr]">
        {/* Sources */}
        <aside>
          <div className="mb-2.5 flex items-center justify-between">
            <span className="text-[11.5px] font-semibold tracking-[0.09em] text-ink-faint uppercase">
              Sources · {sources.length}
            </span>
          </div>
          <div className="flex gap-2.5 overflow-x-auto pb-1 lg:flex-col lg:overflow-visible">
            {sources.map((s) => (
              <div key={s.id} className="w-64 shrink-0 lg:w-auto">
                <SourceCard
                  source={s}
                  active={activeSource === s.id}
                  onClick={() => setActiveSource(activeSource === s.id ? null : s.id)}
                />
              </div>
            ))}
          </div>
          <p className="mt-3 hidden text-[11.5px] leading-relaxed text-ink-faint lg:block">
            Everything on the right is grounded in these sources — with citations you can open.
          </p>
        </aside>

        {/* Workspace */}
        <div className="min-w-0">
          <Card padded={false} className="overflow-hidden">
            <UnderlineTabs tabs={tabs} active={tab} onChange={setTab} className="px-3" />
            <div key={tab} className="anim-fade">
              {tab === 'chat' && <GroundedChat />}
              {tab === 'guide' && <StudyGuide />}
              {tab === 'map' && (
                <div className="p-4">
                  <MindMap />
                </div>
              )}
              {tab === 'quiz' && (
                <div className="flex min-h-[420px] flex-col items-center justify-center p-6 text-center">
                  <span className="flex h-13 w-13 items-center justify-center rounded-2xl bg-indigo-soft text-indigo-ink" style={{ width: 52, height: 52 }}>
                    <PenLine size={22} />
                  </span>
                  <h3 className="mt-4 text-[17px] font-semibold">Quiz yourself on your sources</h3>
                  <p className="mt-1.5 max-w-sm text-[13.5px] leading-relaxed text-ink-soft">
                    Questions are generated from Unit 3 and your notes, tuned to your level — and
                    the results update your roadmap mastery.
                  </p>
                  <Link to="/quiz/precision-recall" className="mt-5">
                    <Button>
                      Start a quiz <ArrowRight size={15} />
                    </Button>
                  </Link>
                </div>
              )}
              {tab === 'cards' && <Flashcards />}
              {tab === 'cast' && <StudyCast />}
            </div>
          </Card>
        </div>
      </div>

      <AddSourceModal open={addOpen} onClose={() => setAddOpen(false)} />
    </Page>
  )
}
