export interface Dimension {
  id: string
  label: string
  value: number
  delta: number
  tone: 'indigo' | 'sky' | 'amber' | 'mint' | 'violet'
}

export const dimensions: Dimension[] = [
  { id: 'learning', label: 'Learning', value: 78, delta: 4, tone: 'indigo' },
  { id: 'skills', label: 'Skills', value: 71, delta: 2, tone: 'sky' },
  { id: 'goals', label: 'Goals', value: 63, delta: 3, tone: 'amber' },
  { id: 'wellbeing', label: 'Wellbeing', value: 74, delta: 1, tone: 'mint' },
  { id: 'inner', label: 'Inner Growth', value: 48, delta: 5, tone: 'violet' },
]

export const weekMinutes = [
  { day: 'Mon', minutes: 45 },
  { day: 'Tue', minutes: 60 },
  { day: 'Wed', minutes: 30 },
  { day: 'Thu', minutes: 55 },
  { day: 'Fri', minutes: 25 },
  { day: 'Sat', minutes: 40 },
  { day: 'Sun', minutes: 0 },
]

export interface KnowledgeTopic {
  id: string
  title: string
  masteryKey?: string
  mastery: number
  tutorId?: string
}

export interface KnowledgeArea {
  id: string
  title: string
  icon: string
  tone: 'indigo' | 'sky' | 'mint' | 'violet'
  topics: KnowledgeTopic[]
}

export const knowledgeMap: KnowledgeArea[] = [
  {
    id: 'ml',
    title: 'Machine Learning',
    icon: 'brain',
    tone: 'indigo',
    topics: [
      { id: 'regression', title: 'Regression', mastery: 92, tutorId: 'linear-regression' },
      { id: 'confusion', title: 'Confusion Matrix', mastery: 88, tutorId: 'confusion-matrix' },
      {
        id: 'precision-recall',
        title: 'Precision & Recall',
        mastery: 65,
        masteryKey: 'precision-recall',
        tutorId: 'precision-recall',
      },
      { id: 'logistic', title: 'Logistic Regression', mastery: 68, tutorId: 'logistic-regression' },
      { id: 'optimization', title: 'Optimization', mastery: 52, tutorId: 'gradient-descent' },
      { id: 'neural', title: 'Neural Networks', mastery: 41, tutorId: 'perceptrons' },
    ],
  },
  {
    id: 'python',
    title: 'Python',
    icon: 'code',
    tone: 'sky',
    topics: [
      { id: 'syntax', title: 'Syntax & Idioms', mastery: 95, tutorId: 'py-syntax' },
      { id: 'data-structures', title: 'Data Structures', mastery: 92, tutorId: 'py-ds' },
      { id: 'decorators', title: 'Decorators & Generators', mastery: 74, tutorId: 'decorators' },
    ],
  },
  {
    id: 'career-skills',
    title: 'Career Skills',
    icon: 'rocket',
    tone: 'violet',
    topics: [
      { id: 'communication', title: 'Structured Communication', mastery: 55, tutorId: 'structured-answers' },
      { id: 'portfolio', title: 'Portfolio Building', mastery: 30, tutorId: 'portfolio-1' },
    ],
  },
]
