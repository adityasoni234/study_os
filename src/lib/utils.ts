import type { ReactNode } from 'react'
import { createElement, Fragment } from 'react'

export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ')
}

export function timeGreeting(): string {
  const h = new Date().getHours()
  if (h < 5) return 'Working late'
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export function todayLabel(): string {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })
}

let idCounter = 0
export function uid(prefix = 'id'): string {
  idCounter += 1
  return `${prefix}-${Date.now().toString(36)}-${idCounter}`
}

/** Renders "**bold**" spans inside plain script text. */
export function rich(text: string): ReactNode {
  const parts = text.split('**')
  if (parts.length === 1) return text
  return createElement(
    Fragment,
    null,
    ...parts.map((part, i) =>
      i % 2 === 1
        ? createElement('strong', { key: i, className: 'font-semibold text-ink' }, part)
        : createElement(Fragment, { key: i }, part),
    ),
  )
}

export function firstName(full: string): string {
  return (full.trim() || 'Aditya').split(/\s+/)[0]
}

export function initials(full: string): string {
  const parts = (full.trim() || 'Aditya').split(/\s+/).slice(0, 2)
  return parts.map((p) => p[0]?.toUpperCase() ?? '').join('')
}

export function clamp(n: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, n))
}

export function fmtClock(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = Math.floor(totalSeconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
