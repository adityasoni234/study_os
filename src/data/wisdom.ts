export interface WisdomEntry {
  id: string
  original: string
  transliteration: string
  translation: string
  source: string
  sourceNote: string
  reflection: string
  question: string
}

/**
 * All verses are authentic, widely-cited classical texts.
 * Source text, translation and AI reflection are labeled separately in the UI.
 */
export const wisdomEntries: WisdomEntry[] = [
  {
    id: 'gita-2-47',
    original: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।',
    transliteration: 'karmaṇy-evādhikāras te mā phaleṣu kadācana',
    translation: 'You have a right to your actions alone, never to their fruits.',
    source: 'Bhagavad Gita 2.47',
    sourceNote: 'Classical text · common English rendering',
    reflection:
      'Study sessions go better when the goal is “sit with this for 25 minutes”, not “be brilliant today”. The effort is yours; the outcome follows on its own schedule.',
    question: 'Where in your learning could you focus more on the process and less on the outcome?',
  },
  {
    id: 'vidya',
    original: 'विद्या ददाति विनयम्',
    transliteration: 'vidyā dadāti vinayam',
    translation: 'Knowledge gives humility.',
    source: 'Hitopadesha',
    sourceNote: 'Classical Sanskrit maxim · common English rendering',
    reflection:
      'The more you genuinely learn, the more comfortable “I don’t know yet” becomes. Getting a question wrong today was knowledge doing its quiet work.',
    question: 'What is one thing you understand less well than you assumed a month ago — and why is noticing that a win?',
  },
  {
    id: 'gita-6-5',
    original: 'उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।',
    transliteration: 'uddhared ātmanātmānaṁ nātmānam avasādayet',
    translation: 'Lift yourself up by your own self; do not let yourself fall.',
    source: 'Bhagavad Gita 6.5',
    sourceNote: 'Classical text · common English rendering',
    reflection:
      'On the days motivation is missing, the smallest self-kept promise — one page, one problem — is how you lift yourself. Tiny, repeated, yours.',
    question: 'What is the smallest promise you could keep to yourself today?',
  },
]
