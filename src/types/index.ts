export type Tone = 'indigo' | 'violet' | 'mint' | 'amber' | 'coral' | 'sky' | 'neutral'

export type RoadmapType = 'Subject' | 'Topic' | 'Career' | 'Exam' | 'Skill' | 'Personal'

export type TopicStatus = 'done' | 'current' | 'locked' | 'review'

export interface Subtopic {
  title: string
  state: 'done' | 'current' | 'next'
}

export interface TopicNode {
  id: string
  title: string
  status: TopicStatus
  mastery: number
  minutes: number
  summary: string
  subtopics?: Subtopic[]
  note?: string
}

export interface Milestone {
  id: string
  title: string
  status: 'done' | 'current' | 'locked'
  topics: TopicNode[]
}

export interface Roadmap {
  id: string
  title: string
  type: RoadmapType
  tone: Tone
  icon: string
  goal: string
  targetDate: string
  baseProgress: number
  focus: string
  nextAction: string
  nextTopicId: string
  adaptedNote?: string
  milestones: Milestone[]
  isNew?: boolean
}

export interface QuizQuestion {
  id: string
  prompt: string
  options: string[]
  correct: number
  explanation: string
  tag: string
}

export interface QuizRecord {
  id: string
  topicId: string
  topicTitle: string
  mode: 'practice' | 'check'
  score: number
  total: number
  weakTags: string[]
  date: string
}

export interface MatchReason {
  label: string
  ok: boolean
}

export interface Opportunity {
  id: string
  title: string
  org: string
  type: string
  tone: Tone
  deadline: string
  daysLeft: number | null
  mode: string
  match: number
  matches: MatchReason[]
  eligibility: string
  source: string
  blurb: string
}

export interface PrepDay {
  day: number
  title: string
  minutes: number
  tasks: string[]
  tutorLink?: string
  note?: string
}

export type SourceKind = 'pdf' | 'web' | 'youtube' | 'notes'

export interface SourceItem {
  id: string
  title: string
  kind: SourceKind
  meta: string
  status: 'ready' | 'processing'
}

export interface Reflection {
  id: string
  mood: string
  moodLabel: string
  note: string
  date: string
}

export interface GratitudeEntry {
  id: string
  text: string
  date: string
}

/* ---------- Tutor script types ---------- */

export type TutorBlock =
  | { kind: 'p'; text: string }
  | { kind: 'callout'; title: string; text: string; tone: Tone; formula?: string }
  | { kind: 'formula'; label: string; expression: string }
  | { kind: 'table'; variant: 'confusion' | 'precision-col' | 'recall-row' }
  | { kind: 'example'; title: string; text: string }
  | { kind: 'tip'; text: string }
  | { kind: 'code'; code: string }
  | { kind: 'cite'; label: string; sourceId?: string }

export interface InlineQuiz {
  id: string
  question: string
  options: string[]
  correct: number
  onCorrect: string
  onWrong: string
}

export interface ScriptChip {
  label: string
  to: string
  primary?: boolean
}

export type ScriptEffect = 'learn-complete' | 'learn-partial' | 'session-done'

export interface ScriptNode {
  id: string
  thinking?: string
  delay?: number
  blocks: TutorBlock[]
  quiz?: InlineQuiz
  chips?: ScriptChip[]
  effect?: ScriptEffect
}

export interface ChatMsg {
  id: string
  role: 'tutor' | 'student'
  text?: string
  blocks?: TutorBlock[]
  quiz?: InlineQuiz
  chips?: ScriptChip[]
  nodeId?: string
}
