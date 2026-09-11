import type { Opportunity, PrepDay } from '@/types'

export const opportunities: Opportunity[] = [
  {
    id: 'hackathon-ai-ed',
    title: 'HackForEd — AI for Education Hackathon',
    org: 'EdTech India Collective',
    type: 'Hackathon',
    tone: 'violet',
    deadline: 'Sep 18',
    daysLeft: 7,
    mode: 'Online',
    match: 94,
    matches: [
      { label: 'Python', ok: true },
      { label: 'Machine Learning', ok: true },
      { label: 'Generative AI', ok: true },
      { label: 'RAG — needs practice', ok: false },
    ],
    eligibility: 'Open to students 18+, teams of 1–4',
    source: 'devfolio.co',
    blurb: 'Build an AI tool that improves how people learn. ₹2L prize pool + incubation support.',
  },
  {
    id: 'kaggle-classification',
    title: 'Binary Classification Challenge',
    org: 'Kaggle Community',
    type: 'Competition',
    tone: 'sky',
    deadline: 'Sep 30',
    daysLeft: 19,
    mode: 'Online',
    match: 88,
    matches: [
      { label: 'Classification', ok: true },
      { label: 'Precision & Recall — your current topic', ok: true },
      { label: 'Feature engineering', ok: false },
    ],
    eligibility: 'Open to everyone, free entry',
    source: 'kaggle.com',
    blurb:
      'A friendly playground competition scored on F1 — a perfect way to apply exactly what you’re learning this week.',
  },
  {
    id: 'research-internship',
    title: 'ML Research Winter Internship',
    org: 'IISc Computational Lab',
    type: 'Research',
    tone: 'indigo',
    deadline: 'Oct 10',
    daysLeft: 29,
    mode: 'Bengaluru · Hybrid',
    match: 76,
    matches: [
      { label: 'Python', ok: true },
      { label: 'Statistics', ok: true },
      { label: 'Neural Networks — not started yet', ok: false },
    ],
    eligibility: 'Undergraduates, 3rd year+',
    source: 'iisc.ac.in',
    blurb:
      'An 8-week mentored research project in applied ML. Strong fit once you reach your Neural Networks milestone.',
  },
  {
    id: 'gsoc-prep',
    title: 'Google Summer of Code — Early Prep',
    org: 'Open Source Community',
    type: 'Open Source',
    tone: 'mint',
    deadline: 'Orgs announced Feb',
    daysLeft: null,
    mode: 'Online',
    match: 81,
    matches: [
      { label: 'Python', ok: true },
      { label: 'Git & GitHub', ok: true },
      { label: 'Sustained contributions', ok: false },
    ],
    eligibility: 'Students & newcomers to open source',
    source: 'summerofcode.withgoogle.com',
    blurb:
      'Successful applicants start contributing months early. Your Python strength makes scikit-learn issues a great entry point.',
  },
  {
    id: 'ai-scholarship',
    title: 'National AI Talent Scholarship',
    org: 'FutureSkills Foundation',
    type: 'Scholarship',
    tone: 'amber',
    deadline: 'Oct 2',
    daysLeft: 21,
    mode: 'Online application',
    match: 72,
    matches: [
      { label: 'Academic record', ok: true },
      { label: 'ML coursework', ok: true },
      { label: 'Project portfolio — in progress', ok: false },
    ],
    eligibility: 'Undergraduate students in India',
    source: 'futureskills.org',
    blurb:
      '₹1L learning grant for promising AI students. Your portfolio project would strengthen the application significantly.',
  },
  {
    id: 'campus-fellowship',
    title: 'Campus AI Builders Fellowship',
    org: 'Builders Collective',
    type: 'Fellowship',
    tone: 'coral',
    deadline: 'Rolling',
    daysLeft: null,
    mode: 'Online + meetups',
    match: 84,
    matches: [
      { label: 'Shipping projects', ok: true },
      { label: 'Community participation', ok: true },
    ],
    eligibility: 'Student builders, any year',
    source: 'builderscollective.dev',
    blurb:
      'A semester-long cohort where students ship one AI product with mentorship from industry engineers.',
  },
]

export function getOpportunity(id: string): Opportunity | undefined {
  return opportunities.find((o) => o.id === id)
}

export const prepPlans: Record<string, PrepDay[]> = {
  'hackathon-ai-ed': [
    {
      day: 1,
      title: 'Understand the problem space',
      minutes: 45,
      tasks: [
        'Read the hackathon brief and judging criteria',
        'Pick a learning problem you personally understand',
        'Sketch your one-line pitch',
      ],
      tutorLink: 'ask',
    },
    {
      day: 2,
      title: 'Learn RAG fundamentals',
      minutes: 60,
      tasks: [
        'Complete "What is RAG?" with your tutor',
        'Understand embeddings at an intuition level',
        'Skim one real RAG example project',
      ],
      tutorLink: 'what-is-rag',
      note: 'RAG is new to you, so this day is lighter everywhere else — take your time here.',
    },
    {
      day: 3,
      title: 'Build the prototype core',
      minutes: 90,
      tasks: [
        'Set up the project skeleton in Python',
        'Wire a minimal retrieval + answer loop',
        'Hard-code one happy-path demo',
      ],
    },
    {
      day: 4,
      title: 'Make it real',
      minutes: 90,
      tasks: [
        'Add your own study materials as sources',
        'Handle two edge cases gracefully',
        'Draft the demo script',
      ],
    },
    {
      day: 5,
      title: 'Polish & practice',
      minutes: 60,
      tasks: [
        'Tighten the UI for the demo path',
        'Rehearse the 3-minute pitch twice',
        'Prepare answers for likely judge questions',
      ],
    },
    {
      day: 6,
      title: 'Submit with margin',
      minutes: 30,
      tasks: [
        'Record the demo video',
        'Write the submission description',
        'Submit before 6pm — never at the deadline',
      ],
    },
  ],
}
