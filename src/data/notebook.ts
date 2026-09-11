import type { SourceItem, TutorBlock } from '@/types'

export const initialSources: SourceItem[] = [
  {
    id: 'src-unit3',
    title: 'ML Course Notes — Unit 3: Model Evaluation',
    kind: 'pdf',
    meta: 'PDF · 42 pages · Added Monday',
    status: 'ready',
  },
  {
    id: 'src-statquest',
    title: 'StatQuest — Precision & Recall, Clearly Explained',
    kind: 'youtube',
    meta: 'YouTube · 9 min · Added Monday',
    status: 'ready',
  },
  {
    id: 'src-sklearn',
    title: 'scikit-learn — Metrics & Scoring Guide',
    kind: 'web',
    meta: 'Web · scikit-learn.org · Added Tuesday',
    status: 'ready',
  },
  {
    id: 'src-lecture',
    title: 'My lecture notes — Week 6',
    kind: 'notes',
    meta: 'Notes · 3 pages · Added yesterday',
    status: 'ready',
  },
]

export interface CitationInfo {
  label: string
  title: string
  excerpt: string
  highlight: string
}

export const citations: Record<string, CitationInfo> = {
  'unit3-p14': {
    label: 'ML Course Notes · Unit 3, p.14',
    title: 'ML Course Notes — Unit 3: Model Evaluation, page 14',
    excerpt:
      'When a classifier makes a positive prediction, we can ask two different questions about its quality. Precision measures the fraction of positive predictions that were actually correct — TP / (TP + FP). Recall measures the fraction of actual positives that the model successfully identified — TP / (TP + FN). These two metrics are in tension: raising the decision threshold typically increases precision while decreasing recall.',
    highlight:
      'Precision measures the fraction of positive predictions that were actually correct — TP / (TP + FP). Recall measures the fraction of actual positives that the model successfully identified — TP / (TP + FN).',
  },
  'unit3-p15': {
    label: 'ML Course Notes · Unit 3, p.15',
    title: 'ML Course Notes — Unit 3: Model Evaluation, page 15',
    excerpt:
      'The F1 score is the harmonic mean of precision and recall: F1 = 2PR / (P + R). Unlike the arithmetic mean, the harmonic mean punishes imbalance — a model with precision 0.9 but recall 0.1 gets an F1 of only 0.18, not 0.5. This makes F1 a useful single-number summary when both kinds of error matter.',
    highlight:
      'The harmonic mean punishes imbalance — a model with precision 0.9 but recall 0.1 gets an F1 of only 0.18, not 0.5.',
  },
  'unit3-p18': {
    label: 'ML Course Notes · Unit 3, p.18',
    title: 'ML Course Notes — Unit 3: Model Evaluation, page 18',
    excerpt:
      'The ROC curve plots the true positive rate against the false positive rate at every possible threshold. A model with no skill follows the diagonal; better models bow toward the top-left corner. The area under the curve (AUC) summarises this across all thresholds.',
    highlight:
      'The ROC curve plots the true positive rate against the false positive rate at every possible threshold.',
  },
  'unit3-p22': {
    label: 'ML Course Notes · Unit 3, p.22',
    title: 'ML Course Notes — Unit 3: Model Evaluation, page 22',
    excerpt:
      'Gradient descent updates model parameters in the direction that reduces the loss. At each step, we compute the gradient of the loss with respect to the parameters and move a small step — the learning rate — in the opposite direction. Too large a learning rate overshoots; too small, and training crawls.',
    highlight:
      'Gradient descent updates model parameters in the direction that reduces the loss.',
  },
  'unit3-p31': {
    label: 'ML Course Notes · Unit 3, p.31',
    title: 'ML Course Notes — Unit 3: Model Evaluation, page 31',
    excerpt:
      'Overfitting occurs when a model learns patterns specific to the training data that do not generalise. The telltale signature is a large gap between training and validation performance. Remedies include more data, regularisation, early stopping, and simpler models.',
    highlight:
      'The telltale signature is a large gap between training and validation performance.',
  },
  'statquest-412': {
    label: 'StatQuest · 04:12',
    title: 'StatQuest — Precision & Recall, Clearly Explained (04:12)',
    excerpt:
      '“…so precision tells you how much you can trust a positive result, and recall tells you how good the model is at finding all the positives. Which one matters more depends entirely on the cost of each kind of mistake…”',
    highlight:
      'precision tells you how much you can trust a positive result, and recall tells you how good the model is at finding all the positives',
  },
}

export interface NotebookAnswer {
  keywords: string[]
  blocks: TutorBlock[]
}

export const notebookAnswers: NotebookAnswer[] = [
  {
    keywords: ['precision', 'recall', 'difference'],
    blocks: [
      {
        kind: 'p',
        text: 'Your notes frame it as two different questions. **Precision**: of everything the model flagged positive, how many were right — TP / (TP + FP). **Recall**: of all real positives, how many did it catch — TP / (TP + FN).',
      },
      {
        kind: 'p',
        text: 'They trade off against each other: a stricter threshold raises precision but lowers recall. Which one to protect depends on the cost of each mistake.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.14', sourceId: 'unit3-p14' },
      { kind: 'cite', label: 'StatQuest · 04:12', sourceId: 'statquest-412' },
    ],
  },
  {
    keywords: ['gradient', 'descent'],
    blocks: [
      {
        kind: 'p',
        text: 'Gradient descent updates model parameters in the direction that reduces the loss. Each step follows the negative gradient, scaled by the learning rate — too large overshoots, too small crawls.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.22', sourceId: 'unit3-p22' },
    ],
  },
  {
    keywords: ['overfit'],
    blocks: [
      {
        kind: 'p',
        text: 'Overfitting is when the model memorises training-specific patterns that don’t generalise. Your notes call the signature “a large gap between training and validation performance”, and list more data, regularisation, early stopping and simpler models as remedies.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.31', sourceId: 'unit3-p31' },
    ],
  },
  {
    keywords: ['f1', 'harmonic'],
    blocks: [
      {
        kind: 'p',
        text: 'F1 is the harmonic mean of precision and recall: **F1 = 2PR / (P + R)**. The harmonic mean punishes imbalance — precision 0.9 with recall 0.1 gives F1 ≈ 0.18, not 0.5 — so F1 only looks good when both are solid.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.15', sourceId: 'unit3-p15' },
    ],
  },
  {
    keywords: ['roc', 'auc', 'curve'],
    blocks: [
      {
        kind: 'p',
        text: 'The ROC curve plots true positive rate against false positive rate across every threshold — no-skill models follow the diagonal, better ones bow toward the top-left. AUC summarises the whole curve in one number.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.18', sourceId: 'unit3-p18' },
    ],
  },
]

/* ---------- Mind map ---------- */

export interface MindNode {
  id: string
  label: string
  x: number
  y: number
  kind: 'center' | 'branch' | 'leaf'
  tone: 'indigo' | 'mint' | 'amber' | 'sky' | 'violet' | 'neutral'
  mastery?: number
  parent?: string
  summary?: string
  topicId?: string
}

export const mindNodes: MindNode[] = [
  { id: 'ml', label: 'Machine Learning', x: 430, y: 265, kind: 'center', tone: 'indigo' },

  { id: 'sup', label: 'Supervised Learning', x: 205, y: 140, kind: 'branch', tone: 'sky', parent: 'ml' },
  { id: 'reg', label: 'Regression', x: 90, y: 62, kind: 'leaf', tone: 'mint', mastery: 92, parent: 'sup', summary: 'Predicting continuous values by fitting functions to data.', topicId: 'linear-regression' },
  { id: 'cls', label: 'Classification', x: 60, y: 205, kind: 'leaf', tone: 'indigo', mastery: 65, parent: 'sup', summary: 'Predicting categories — and measuring how well you do it.', topicId: 'precision-recall' },

  { id: 'unsup', label: 'Unsupervised Learning', x: 210, y: 402, kind: 'branch', tone: 'violet', parent: 'ml' },
  { id: 'clu', label: 'Clustering', x: 78, y: 350, kind: 'leaf', tone: 'neutral', mastery: 0, parent: 'unsup', summary: 'Finding natural groups without labels.', topicId: 'clustering' },
  { id: 'dim', label: 'Dimensionality Reduction', x: 122, y: 470, kind: 'leaf', tone: 'neutral', mastery: 0, parent: 'unsup', summary: 'Compressing features while keeping structure.', topicId: 'dim-reduction' },

  { id: 'eval', label: 'Model Evaluation', x: 655, y: 138, kind: 'branch', tone: 'mint', parent: 'ml' },
  { id: 'cm', label: 'Confusion Matrix', x: 782, y: 58, kind: 'leaf', tone: 'mint', mastery: 88, parent: 'eval', summary: 'The 2×2 table every classification metric is built from.', topicId: 'confusion-matrix' },
  { id: 'pr', label: 'Precision & Recall', x: 788, y: 158, kind: 'leaf', tone: 'indigo', mastery: 65, parent: 'eval', summary: 'False alarms vs. misses — today’s mission topic.', topicId: 'precision-recall' },
  { id: 'roc', label: 'ROC Curves', x: 775, y: 248, kind: 'leaf', tone: 'amber', mastery: 12, parent: 'eval', summary: 'Precision-recall thinking drawn as a picture. Up next.', topicId: 'roc-curves' },

  { id: 'opt', label: 'Optimization', x: 640, y: 400, kind: 'branch', tone: 'amber', parent: 'ml' },
  { id: 'gd', label: 'Gradient Descent', x: 790, y: 352, kind: 'leaf', tone: 'mint', mastery: 84, parent: 'opt', summary: 'Following the loss downhill, one small step at a time.', topicId: 'gradient-descent' },
  { id: 'reg2', label: 'Regularization', x: 772, y: 462, kind: 'leaf', tone: 'amber', mastery: 46, parent: 'opt', summary: 'Keeping models simple enough to generalise.', topicId: 'regularization' },
]

/* ---------- Flashcards ---------- */

export interface Flashcard {
  id: string
  front: string
  back: string
  weak?: boolean
}

export const flashcards: Flashcard[] = [
  {
    id: 'f1',
    front: 'Precision — what question does it answer?',
    back: 'Of everything the model flagged as positive, how many actually were?\n\nPrecision = TP / (TP + FP)',
    weak: true,
  },
  {
    id: 'f2',
    front: 'Recall — what question does it answer?',
    back: 'Of all the real positives, how many did the model catch?\n\nRecall = TP / (TP + FN)',
    weak: true,
  },
  {
    id: 'f3',
    front: 'Which error type does recall punish?',
    back: 'False negatives — the positives the model missed. “Don’t miss the wolf.”',
    weak: true,
  },
  {
    id: 'f4',
    front: 'Which error type does precision punish?',
    back: 'False positives — the false alarms. “Don’t cry wolf.”',
  },
  {
    id: 'f5',
    front: 'F1 score — formula and why harmonic mean?',
    back: 'F1 = 2PR / (P + R).\n\nThe harmonic mean stays low unless both precision and recall are high — imbalance is punished.',
  },
  {
    id: 'f6',
    front: 'Why can 99% accuracy be misleading?',
    back: 'On imbalanced data, always predicting the majority class scores high accuracy while catching zero positives (recall = 0).',
  },
  {
    id: 'f7',
    front: 'Raise the decision threshold → what happens?',
    back: 'The model flags fewer, surer cases: precision typically rises, recall falls.',
  },
  {
    id: 'f8',
    front: 'Disease screening: optimise which metric?',
    back: 'Recall — a missed sick patient (false negative) is far costlier than an extra follow-up test (false positive).',
  },
]

/* ---------- Study guide ---------- */

export interface GuideSection {
  id: string
  title: string
  icon: string
  defaultOpen?: boolean
}

export const studycastLines: { speaker: 'A' | 'B'; text: string }[] = [
  { speaker: 'A', text: 'Okay, Unit 3 — model evaluation. Big question: your classifier says “positive”. Do you trust it?' },
  { speaker: 'B', text: 'That’s literally precision! Of everything it flagged, how much was right. TP over TP plus FP.' },
  { speaker: 'A', text: 'And the mirror question — of everything it should have caught, how much did it actually catch?' },
  { speaker: 'B', text: 'Recall. TP over TP plus FN. The two are in tension — squeeze one, the other slips.' },
  { speaker: 'A', text: 'My favourite bit from the notes: the 99% accuracy trap. Predict “no disease” for everyone…' },
  { speaker: 'B', text: '…99% accurate, zero patients helped. Recall is exactly zero. That’s why accuracy alone lies.' },
  { speaker: 'A', text: 'So when do you protect precision, and when recall?' },
  { speaker: 'B', text: 'Cost of the mistake. Missing a sick patient? Protect recall. Spamming users with false alarms? Protect precision.' },
  { speaker: 'A', text: 'And if you need one number for both — F1, the harmonic mean. Harsh on imbalance, on purpose.' },
  { speaker: 'B', text: 'Next episode: ROC curves — this whole trade-off, drawn as a picture. See you there.' },
]
