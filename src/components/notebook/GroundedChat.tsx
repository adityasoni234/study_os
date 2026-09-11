import { useEffect, useRef, useState } from 'react'
import { Send, Sparkles } from 'lucide-react'
import type { TutorBlock } from '@/types'
import { notebookAnswers } from '@/data/notebook'
import { Blocks } from '@/components/tutor/blocks'
import { cn, uid } from '@/lib/utils'

interface NbMsg {
  id: string
  role: 'user' | 'ai'
  text?: string
  blocks?: TutorBlock[]
  offerGeneral?: boolean
}

const seed: NbMsg[] = [
  { id: 'nb-1', role: 'user', text: 'What’s the difference between precision and recall?' },
  {
    id: 'nb-2',
    role: 'ai',
    blocks: notebookAnswers[0].blocks,
  },
]

const generalAnswer: TutorBlock[] = [
  {
    kind: 'p',
    text: 'From general knowledge, then (no citation for this one): the short answer is that it depends on the cost of each kind of error in your specific situation. If you add a source that covers this, I’ll ground the answer properly and cite the exact passage.',
  },
]

export function GroundedChat() {
  const [messages, setMessages] = useState<NbMsg[]>(seed)
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  const send = (text: string) => {
    const t = text.trim()
    if (!t) return
    setMessages((m) => [...m, { id: uid('nb'), role: 'user', text: t }])
    setInput('')
    setTyping(true)
    window.setTimeout(() => {
      setTyping(false)
      const lower = t.toLowerCase()
      const match = notebookAnswers.find((a) => a.keywords.some((k) => lower.includes(k)))
      if (match) {
        setMessages((m) => [...m, { id: uid('nb'), role: 'ai', blocks: match.blocks }])
      } else {
        setMessages((m) => [
          ...m,
          {
            id: uid('nb'),
            role: 'ai',
            blocks: [
              {
                kind: 'p',
                text: 'I searched your four sources and couldn’t find this covered — so I won’t guess and pretend it’s in your notes. Want a general-knowledge answer instead, or shall we keep strictly to your sources?',
              },
            ],
            offerGeneral: true,
          },
        ])
      }
    }, 1400)
  }

  const answerGenerally = () => {
    setTyping(true)
    window.setTimeout(() => {
      setTyping(false)
      setMessages((m) => [...m, { id: uid('nb'), role: 'ai', blocks: generalAnswer }])
    }, 1000)
  }

  const suggestions = ['Explain gradient descent', 'What is the F1 score?', 'Summarize ROC curves']

  return (
    <div className="flex h-[540px] flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <div key={m.id} className="anim-in">
            {m.role === 'user' ? (
              <div className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl rounded-tr-md bg-indigo px-4 py-2.5 text-[13.5px] text-white">
                  {m.text}
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-2.5">
                <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-violet text-white">
                  <Sparkles size={12} />
                </span>
                <div className="max-w-[88%] rounded-2xl rounded-tl-md border bg-card p-3.5 shadow-(--shadow-soft)">
                  {m.blocks != null && <Blocks blocks={m.blocks} />}
                  {m.offerGeneral === true && i === messages.length - 1 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button
                        onClick={answerGenerally}
                        className="rounded-full border border-indigo bg-indigo px-3 py-1.5 text-[12.5px] font-medium text-white transition-colors hover:bg-indigo-deep"
                      >
                        Answer generally
                      </button>
                      <button
                        onClick={() =>
                          setMessages((mm) => [
                            ...mm,
                            {
                              id: uid('nb'),
                              role: 'ai',
                              blocks: [
                                {
                                  kind: 'p',
                                  text: 'Staying grounded in your sources, then. Ask me anything from Unit 3, the StatQuest video, the scikit-learn guide, or your lecture notes.',
                                },
                              ],
                            },
                          ])
                        }
                        className="rounded-full border bg-card px-3 py-1.5 text-[12.5px] font-medium text-ink-soft transition-colors hover:border-indigo/50 hover:text-indigo-ink"
                      >
                        Keep to my sources
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        {typing && (
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-violet text-white">
              <Sparkles size={12} />
            </span>
            <div className="flex items-center gap-2 rounded-2xl rounded-tl-md border bg-card px-3.5 py-2.5">
              <span className="flex gap-1">
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo" />
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo [animation-delay:0.15s]" />
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo [animation-delay:0.3s]" />
              </span>
              <span className="text-[12px] text-ink-faint">Searching your sources…</span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t p-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border bg-card px-2.5 py-1 text-[11.5px] font-medium text-ink-soft transition-colors hover:border-indigo/50 hover:text-indigo-ink"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send(input)}
            placeholder="Ask across your sources…"
            aria-label="Ask your sources"
            className="h-10 min-w-0 flex-1 rounded-xl border bg-paper px-3.5 text-[13.5px] outline-none transition-colors focus:border-indigo"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim()}
            aria-label="Send"
            className={cn(
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo text-white transition-all hover:bg-indigo-deep active:scale-95 disabled:opacity-40',
            )}
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  )
}
