import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChatMsg, InlineQuiz, ScriptChip, ScriptEffect } from '@/types'
import { scriptFor } from '@/data/tutorScript'
import { uid } from '@/lib/utils'

export interface QuizAnswerState {
  selected: number
  correct: boolean
}

/** Returns tutor blocks from the live backend, or null to fall back to the script. */
export type LiveSend = (
  text: string,
) => Promise<{ blocks: ChatMsg['blocks']; chips?: ChatMsg['chips'] } | null>

export function useTutorEngine({
  topicId,
  title,
  initialQuery,
  onEffect,
  onNavigateIntent,
  liveSend,
}: {
  topicId: string
  title: string
  initialQuery?: string
  onEffect: (e: ScriptEffect) => void
  onNavigateIntent: (intent: string) => void
  liveSend?: LiveSend
}) {
  const [messages, setMessages] = useState<ChatMsg[]>([])
  const [typing, setTyping] = useState<string | null>(null)
  const [quizAnswers, setQuizAnswers] = useState<Record<string, QuizAnswerState>>({})
  const script = useRef(scriptFor(topicId, title))
  const started = useRef(false)
  const timers = useRef<number[]>([])

  const later = useCallback((fn: () => void, ms: number) => {
    timers.current.push(window.setTimeout(fn, ms))
  }, [])

  useEffect(() => () => timers.current.forEach(clearTimeout), [])

  const advance = useCallback(
    (nodeId: string) => {
      const node = script.current.nodes[nodeId] ?? script.current.nodes.fallback
      if (!node) return
      setTyping(node.thinking ?? 'Thinking…')
      later(() => {
        setTyping(null)
        setMessages((prev) => [
          ...prev,
          {
            id: uid('msg'),
            role: 'tutor',
            blocks: node.blocks,
            quiz: node.quiz,
            chips: node.chips,
            nodeId: node.id,
          },
        ])
        if (node.effect) onEffect(node.effect)
      }, node.delay ?? 1000)
    },
    [later, onEffect],
  )

  // Kick off the session.
  useEffect(() => {
    if (started.current) return
    started.current = true
    if (initialQuery && initialQuery.trim()) {
      setMessages([{ id: uid('msg'), role: 'student', text: initialQuery.trim() }])
      later(() => advance(script.current.route(initialQuery)), 150)
    } else {
      advance(script.current.entry)
    }
  }, [advance, initialQuery, later])

  const sendChip = useCallback(
    (chip: ScriptChip) => {
      if (chip.to.startsWith('go-')) {
        onNavigateIntent(chip.to)
        return
      }
      setMessages((prev) => [...prev, { id: uid('msg'), role: 'student', text: chip.label }])
      later(() => advance(chip.to), 200)
    },
    [advance, later, onNavigateIntent],
  )

  const sendText = useCallback(
    (text: string) => {
      const t = text.trim()
      if (!t) return
      setMessages((prev) => [...prev, { id: uid('msg'), role: 'student', text: t }])

      const routed = script.current.route(t)
      // Free-text questions the script can't answer well go to the live tutor
      // when a backend is reachable; anything else stays on the scripted path.
      if (liveSend && routed === 'fallback') {
        setTyping('Thinking…')
        void liveSend(t)
          .then((res) => {
            setTyping(null)
            if (!res) {
              advance(routed)
              return
            }
            setMessages((prev) => [
              ...prev,
              { id: uid('msg'), role: 'tutor', blocks: res.blocks, chips: res.chips },
            ])
          })
          .catch(() => {
            setTyping(null)
            advance(routed)
          })
        return
      }

      later(() => advance(routed), 250)
    },
    [advance, later, liveSend],
  )

  const answerQuiz = useCallback(
    (quiz: InlineQuiz, selected: number) => {
      if (quizAnswers[quiz.id]) return
      const correct = selected === quiz.correct
      setQuizAnswers((prev) => ({ ...prev, [quiz.id]: { selected, correct } }))
      later(() => advance(correct ? quiz.onCorrect : quiz.onWrong), 900)
    },
    [advance, later, quizAnswers],
  )

  const jumpTo = useCallback(
    (nodeId: string, studentLabel: string) => {
      setMessages((prev) => [...prev, { id: uid('msg'), role: 'student', text: studentLabel }])
      const target = script.current.nodes[nodeId] ? nodeId : 'fallback'
      later(() => advance(target), 200)
    },
    [advance, later],
  )

  /** Tutor speaks without a student turn (e.g. acknowledging mastery mode). */
  const announce = useCallback(
    (text: string) => {
      setTyping('Thinking…')
      later(() => {
        setTyping(null)
        setMessages((prev) => [
          ...prev,
          { id: uid('msg'), role: 'tutor', blocks: [{ kind: 'p', text }] },
        ])
      }, 800)
    },
    [later],
  )

  return { messages, typing, quizAnswers, sendChip, sendText, answerQuiz, jumpTo, announce }
}
