import type { ScriptNode } from '@/types'

/**
 * Scripted tutor conversations. The UI treats these as if they came from the
 * AI backend — the engine adds thinking delays, supports branching on quiz
 * answers, and fires mastery effects.
 */

const prNodes: ScriptNode[] = [
  {
    id: 'intro',
    delay: 1100,
    blocks: [
      {
        kind: 'p',
        text: 'Welcome back, Aditya 👋 — last session you worked through the **confusion matrix** and finished at 88%. Solid. Today is **Precision & Recall**: the two questions every classifier has to answer.',
      },
      {
        kind: 'p',
        text: 'This is the exact next step on your Machine Learning roadmap, and it took about 25 minutes for learners at your level. Ready?',
      },
    ],
    chips: [
      { label: "Let's go", to: 'core', primary: true },
      { label: 'Quick recap of the confusion matrix first', to: 'recap' },
    ],
  },
  {
    id: 'recap',
    delay: 900,
    blocks: [
      { kind: 'p', text: 'Thirty seconds, then. Every prediction a classifier makes lands in one of four buckets:' },
      { kind: 'table', variant: 'confusion' },
      {
        kind: 'p',
        text: 'Every metric we meet today is just arithmetic on these four numbers. That’s the whole trick — hold onto it.',
      },
    ],
    chips: [{ label: 'Got it — continue', to: 'core', primary: true }],
  },
  {
    id: 'core',
    delay: 1400,
    blocks: [
      { kind: 'p', text: 'The cleanest way to keep these two ideas apart is to hold them as **questions**, not formulas.' },
      {
        kind: 'callout',
        tone: 'indigo',
        title: 'Precision — “When I raised my hand, how often was I right?”',
        text: 'Of everything the model flagged as positive, how many actually were positive.',
        formula: 'Precision = TP / (TP + FP)',
      },
      {
        kind: 'callout',
        tone: 'mint',
        title: 'Recall — “Of everything I was meant to catch, how much did I catch?”',
        text: 'Of all the real positives out there, how many the model actually found.',
        formula: 'Recall = TP / (TP + FN)',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.14', sourceId: 'unit3-p14' },
      {
        kind: 'p',
        text: 'The tension between them is the interesting part: push one up and the other usually slips. Which one you protect depends on **what each kind of mistake costs**.',
      },
      {
        kind: 'p',
        text: 'I think you’ve got the definitions — the real test is applying them under pressure. That’s where most people slip. Want to try one?',
      },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Explain simpler', to: 'simpler' },
      { label: 'Give me an analogy', to: 'analogy' },
      { label: 'Real-world example', to: 'real-world' },
      { label: 'Go deeper', to: 'deeper' },
    ],
  },
  {
    id: 'simpler',
    delay: 1000,
    blocks: [
      { kind: 'p', text: 'Simplest version. You’re fishing with a net:' },
      {
        kind: 'example',
        title: 'The fishing net',
        text: '**Precision** — of everything in your net, how much is actually fish (and not boots)?\n**Recall** — of all the fish in the lake, how many ended up in your net?\n\nA huge wide net catches every fish — plus a lot of boots. High recall, low precision. A tiny careful net catches only fish — but misses most of them. High precision, low recall.',
      },
      { kind: 'p', text: 'That trade-off **is** the topic. Everything else is bookkeeping.' },
    ],
    chips: [
      { label: 'That clicked — test me ✏️', to: 'quiz1', primary: true },
      { label: 'One more angle', to: 'analogy' },
    ],
  },
  {
    id: 'analogy',
    delay: 1000,
    blocks: [
      {
        kind: 'example',
        title: 'Airport security',
        text: 'Flag **every** passenger for extra screening → you’ll never miss a threat (perfect recall), but nearly every alarm is false (terrible precision), and the queue riots.\n\nFlag only the most certain cases → almost every alarm is real (great precision), but things slip through (poor recall).',
      },
      {
        kind: 'tip',
        text: 'Memory hook: **Precision = don’t cry wolf. Recall = don’t miss the wolf.**',
      },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Show a real-world example', to: 'real-world' },
    ],
  },
  {
    id: 'real-world',
    delay: 1100,
    blocks: [
      { kind: 'p', text: 'Three systems you use, three different priorities:' },
      {
        kind: 'example',
        title: 'Where each metric rules',
        text: '**Spam filter** → precision. A false alarm buries a real email — users forgive missed spam far more easily.\n**Disease screening** → recall. A miss is a sick patient sent home; a false alarm is just one more test.\n**YouTube recommendations** → precision-ish. Bad suggestions erode trust; missing one good video costs almost nothing.',
      },
      { kind: 'p', text: 'Notice the pattern: ask **“which mistake is expensive?”** and the metric picks itself.' },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Go deeper', to: 'deeper' },
    ],
  },
  {
    id: 'deeper',
    delay: 1300,
    thinking: 'Taking a closer look…',
    blocks: [
      {
        kind: 'p',
        text: 'Deeper cut. Your classifier doesn’t output “yes/no” — it outputs a **probability**, and you choose a threshold. Slide the threshold up and you flag fewer, surer cases: precision rises, recall falls. Slide it down, the reverse. Precision and recall are two ends of one dial.',
      },
      {
        kind: 'p',
        text: 'When you need a single number that respects both, use **F1 — the harmonic mean**:',
      },
      { kind: 'formula', label: 'F1 score', expression: 'F1 = 2 · (P · R) / (P + R)' },
      {
        kind: 'p',
        text: 'Why harmonic, not average? Because it **punishes imbalance**: precision 0.9 with recall 0.1 averages to 0.5, but F1 gives a brutal 0.18 — which is the honest answer.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.15', sourceId: 'unit3-p15' },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Back to basics', to: 'simpler' },
    ],
  },
  {
    id: 'visual',
    delay: 1100,
    blocks: [
      { kind: 'p', text: 'Look at where each metric **lives** in the confusion matrix:' },
      { kind: 'table', variant: 'precision-col' },
      { kind: 'table', variant: 'recall-row' },
      {
        kind: 'p',
        text: '**Precision reads down a column** — the world of the model’s positive calls. **Recall reads across a row** — the world of actual positives. Same table, two directions.',
      },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Explain with code', to: 'with-code' },
    ],
  },
  {
    id: 'mathematical',
    delay: 1200,
    blocks: [
      { kind: 'p', text: 'Formally, with the four counts TP, FP, FN, TN:' },
      { kind: 'formula', label: 'Precision', expression: 'P = TP / (TP + FP)' },
      { kind: 'formula', label: 'Recall (sensitivity)', expression: 'R = TP / (TP + FN)' },
      { kind: 'formula', label: 'F1', expression: 'F1 = 2PR / (P + R)' },
      {
        kind: 'p',
        text: 'And the trap: **accuracy = (TP + TN) / total** looks reasonable but collapses on imbalance. With 99% negatives, the constant model “always negative” scores 99% accuracy with recall exactly 0.',
      },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Make it intuitive again', to: 'simpler' },
    ],
  },
  {
    id: 'technical',
    delay: 1100,
    blocks: [
      {
        kind: 'p',
        text: 'In practice you’ll rarely compute these by hand. In scikit-learn: `precision_score`, `recall_score`, and `classification_report` give you everything per class. The threshold lives in you, though — `predict_proba` plus your own cut-off is how you actually trade precision against recall in production.',
      },
    ],
    chips: [
      { label: 'Show me the code', to: 'with-code', primary: true },
      { label: 'Test me ✏️', to: 'quiz1' },
    ],
  },
  {
    id: 'with-code',
    delay: 1200,
    blocks: [
      { kind: 'p', text: 'Here’s the whole idea in six honest lines:' },
      {
        kind: 'code',
        code: `from sklearn.metrics import precision_score, recall_score

y_true = [1, 1, 1, 0, 0, 0, 1, 0]
y_pred = [1, 0, 1, 0, 1, 0, 1, 0]

print(precision_score(y_true, y_pred))  # 0.75 — of 4 flags, 3 right
print(recall_score(y_true, y_pred))     # 0.75 — of 4 positives, caught 3`,
      },
      { kind: 'p', text: 'Try changing one prediction and predicting how both numbers move — that’s the fastest way to make it stick.' },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Back to the concept', to: 'core' },
    ],
  },
  {
    id: 'quiz1',
    delay: 900,
    blocks: [
      { kind: 'p', text: 'Here’s a real-world call to make. Take your time — the reasoning matters more than the answer.' },
    ],
    quiz: {
      id: 'q1',
      question:
        'A hospital screens 1,000 patients for a rare disease. Missing a sick patient is dangerous; a false alarm just means one extra test. Which metric should the model maximise?',
      options: ['Precision', 'Recall', 'Accuracy', 'Specificity'],
      correct: 1,
      onCorrect: 'nice1',
      onWrong: 'adapt1',
    },
  },
  {
    id: 'adapt1',
    delay: 1600,
    thinking: 'Taking a closer look at your reasoning…',
    blocks: [
      {
        kind: 'p',
        text: 'You’re close — and honestly, this is **the** classic mix-up, so you’re in good company. Let’s untangle it properly.',
      },
      {
        kind: 'p',
        text: 'The dangerous mistake here is **missing a sick patient** — that’s a **false negative**. Now, which metric has false negatives in its denominator? Recall: TP / (TP + **FN**). Precision worries about false **alarms** — and here a false alarm is just one extra test. Cheap.',
      },
      {
        kind: 'tip',
        text: 'Keep this hook: **Precision = don’t cry wolf. Recall = don’t miss the wolf.** In a hospital, missing the wolf is what hurts.',
      },
      { kind: 'p', text: 'Let’s flip the scenario and see if it clicks from the other side:' },
    ],
    quiz: {
      id: 'q2',
      question:
        'Your spam filter keeps sending real, important emails to the spam folder. Users are furious. Which metric is too low?',
      options: ['Recall', 'Precision', 'Accuracy', 'F1 score'],
      correct: 1,
      onCorrect: 'mastery',
      onWrong: 'reveal',
    },
  },
  {
    id: 'nice1',
    delay: 1000,
    blocks: [
      {
        kind: 'p',
        text: 'Exactly — a missed sick patient is a **false negative**, and recall is the metric that punishes false negatives. You reasoned from the cost of the mistake, which is precisely the skill.',
      },
      { kind: 'p', text: 'Let’s make sure the reverse direction is just as solid:' },
    ],
    quiz: {
      id: 'q2b',
      question:
        'Your spam filter keeps sending real, important emails to the spam folder. Users are furious. Which metric is too low?',
      options: ['Recall', 'Precision', 'Accuracy', 'F1 score'],
      correct: 1,
      onCorrect: 'mastery',
      onWrong: 'reveal',
    },
  },
  {
    id: 'reveal',
    delay: 1500,
    thinking: 'Let’s approach it differently…',
    blocks: [
      { kind: 'p', text: 'No stress — let’s walk it through together, slowly.' },
      {
        kind: 'p',
        text: 'A real email marked as spam is a **false positive** — the filter “raised its hand” and was wrong. Wrong positive calls are exactly what **precision** measures: TP / (TP + **FP**). So angry users ⇒ precision is too low.',
      },
      {
        kind: 'p',
        text: 'You’ve now seen both directions: hospital ⇒ protect **recall** (don’t miss), spam ⇒ protect **precision** (don’t cry wolf). That contrast is the whole concept — and you got there by working through it, which beats getting it instantly.',
      },
    ],
    effect: 'learn-partial',
    chips: [
      { label: 'Practice 5 questions', to: 'go-practice', primary: true },
      { label: 'Finish for today', to: 'finish' },
    ],
  },
  {
    id: 'mastery',
    delay: 1200,
    blocks: [
      {
        kind: 'p',
        text: 'That’s it — you just separated the two ideas most students blur together. **Precision guards against false alarms; recall guards against misses.** 🎉',
      },
      {
        kind: 'p',
        text: 'I’ve updated your roadmap: **Precision & Recall is now at 72%**, and the first step of today’s mission is done. One good practice run and this is locked in.',
      },
    ],
    effect: 'learn-complete',
    chips: [
      { label: 'Practice 5 questions', to: 'go-practice', primary: true },
      { label: 'Finish for today', to: 'finish' },
    ],
  },
  {
    id: 'finish',
    delay: 900,
    blocks: [
      {
        kind: 'p',
        text: 'Great session. Tomorrow we build on this with **ROC curves** — which are really just precision-recall thinking drawn as a picture. You’ll recognise everything. 🌱',
      },
    ],
    effect: 'session-done',
    chips: [{ label: 'Back to Home', to: 'go-home', primary: true }],
  },
  {
    id: 'fallback',
    delay: 1100,
    blocks: [
      {
        kind: 'p',
        text: 'Good question — here’s the way I’d hold onto it. Precision and recall are answers to two different worries: **“can I trust the model’s yes?”** (precision) and **“is the model finding everything?”** (recall). Any question about them usually resolves by asking which mistake — false alarm or miss — is expensive in your scenario.',
      },
      { kind: 'p', text: 'Want to pressure-test that with a quick question, or see it from another angle?' },
    ],
    chips: [
      { label: 'Test me ✏️', to: 'quiz1', primary: true },
      { label: 'Give me an analogy', to: 'analogy' },
      { label: 'Go deeper', to: 'deeper' },
    ],
  },
]

/* ---------- RAG topic (used by hackathon prep) ---------- */

const ragNodes: ScriptNode[] = [
  {
    id: 'intro',
    delay: 1100,
    blocks: [
      {
        kind: 'p',
        text: 'New territory, Aditya — **Retrieval-Augmented Generation**. I added this topic because the hackathon you’re preparing for needs it, and it builds neatly on what you already know.',
      },
      {
        kind: 'p',
        text: 'One sentence first: **RAG lets an AI look things up before it answers** — instead of relying only on what it memorised in training.',
      },
    ],
    chips: [
      { label: 'Why does that matter?', to: 'why', primary: true },
      { label: 'How does it work?', to: 'how' },
    ],
  },
  {
    id: 'why',
    delay: 1200,
    blocks: [
      {
        kind: 'example',
        title: 'The open-book exam',
        text: 'A plain language model answers from memory — a **closed-book exam**. Impressive, but it can misremember, and it knows nothing about *your* documents.\n\nRAG turns it into an **open-book exam**: before answering, the system retrieves the most relevant passages from a knowledge base, hands them to the model, and asks it to answer *grounded in those passages* — with citations.',
      },
      {
        kind: 'p',
        text: 'That’s why RAG matters for your hackathon: an education tool that cites real course material is trustworthy in a way a memory-only chatbot can’t be. (It’s also exactly how the Notebook in a product like this would work.)',
      },
    ],
    chips: [
      { label: 'How does it work under the hood?', to: 'how', primary: true },
      { label: 'Quick check ✏️', to: 'rag-quiz' },
    ],
  },
  {
    id: 'how',
    delay: 1300,
    blocks: [
      { kind: 'p', text: 'Four steps, every time:' },
      {
        kind: 'example',
        title: 'The RAG pipeline',
        text: '**1 · Chunk** — split documents into passages.\n**2 · Embed** — turn each passage into a vector that captures its meaning.\n**3 · Retrieve** — when a question arrives, embed it too and find the nearest passages.\n**4 · Generate** — give the model the question *plus* those passages and ask for a grounded, cited answer.',
      },
      {
        kind: 'p',
        text: 'Most of the craft is in steps 1 and 3 — chunking well and retrieving the *right* passages. The generation step is the easy part these days.',
      },
    ],
    chips: [
      { label: 'Quick check ✏️', to: 'rag-quiz', primary: true },
      { label: 'Why does RAG matter again?', to: 'why' },
    ],
  },
  {
    id: 'rag-quiz',
    delay: 900,
    blocks: [{ kind: 'p', text: 'Quick check to anchor it:' }],
    quiz: {
      id: 'rq1',
      question: 'What is the main problem RAG solves compared to a plain language model?',
      options: [
        'It makes the model answer from relevant retrieved sources instead of memory alone',
        'It makes the model run faster',
        'It removes the need for any training',
        'It compresses the model to fit on a phone',
      ],
      correct: 0,
      onCorrect: 'rag-win',
      onWrong: 'rag-retry',
    },
  },
  {
    id: 'rag-retry',
    delay: 1200,
    thinking: 'Let’s approach it differently…',
    blocks: [
      {
        kind: 'p',
        text: 'Close — think back to the open-book exam. The point isn’t speed or size: it’s that the model gets to **look at real, relevant sources before answering**, which makes answers current, grounded and citable.',
      },
    ],
    chips: [{ label: 'Got it — continue', to: 'rag-win', primary: true }],
  },
  {
    id: 'rag-win',
    delay: 1000,
    blocks: [
      {
        kind: 'p',
        text: 'That’s the core of RAG — you’re ahead of schedule on Day 2 of your prep plan. Next session we’ll build intuition for **embeddings**, the geometry that makes retrieval work.',
      },
    ],
    chips: [
      { label: 'Back to my prep plan', to: 'go-prep', primary: true },
      { label: 'Finish for today', to: 'go-home' },
    ],
  },
  {
    id: 'fallback',
    delay: 1000,
    blocks: [
      {
        kind: 'p',
        text: 'Good thread to pull. The honest one-liner: **RAG = retrieve relevant passages, then generate an answer grounded in them.** Everything else — chunking, embeddings, vector search — exists to make that retrieval step good.',
      },
    ],
    chips: [
      { label: 'Walk me through the pipeline', to: 'how', primary: true },
      { label: 'Quick check ✏️', to: 'rag-quiz' },
    ],
  },
]

/* ---------- Ad-hoc "ask me anything" topics ---------- */

const askNodes: ScriptNode[] = [
  {
    id: 'gradient-descent',
    delay: 1300,
    blocks: [
      {
        kind: 'p',
        text: 'Picture standing on a foggy hillside trying to reach the valley. You can’t see far — but you can feel the slope under your feet. So you take a small step downhill. Then again. That’s **gradient descent**.',
      },
      {
        kind: 'p',
        text: 'The “hill” is the **loss function** (how wrong the model is), the “position” is the model’s parameters, and the step size is the **learning rate**. Too big a step and you overshoot the valley; too small and you crawl forever.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.22', sourceId: 'unit3-p22' },
    ],
    chips: [
      { label: 'Test me on this ✏️', to: 'ask-quiz-gd', primary: true },
      { label: 'Explain simpler', to: 'gd-simpler' },
    ],
  },
  {
    id: 'gd-simpler',
    delay: 900,
    blocks: [
      {
        kind: 'example',
        title: 'Even simpler',
        text: 'Hot-and-cold, the children’s game. The model guesses, the loss says “colder!”, and gradient descent tells it exactly which direction is “warmer” — then it shuffles that way a little. Thousands of shuffles later: warm.',
      },
    ],
    chips: [{ label: 'Test me ✏️', to: 'ask-quiz-gd', primary: true }],
  },
  {
    id: 'ask-quiz-gd',
    delay: 800,
    blocks: [{ kind: 'p', text: 'Quick check:' }],
    quiz: {
      id: 'gdq',
      question: 'A learning rate that is far too large will most likely cause…',
      options: [
        'The loss to bounce around or diverge instead of settling',
        'Slower but perfectly safe convergence',
        'The model to use fewer parameters',
        'Nothing — learning rate barely matters',
      ],
      correct: 0,
      onCorrect: 'ask-win',
      onWrong: 'ask-gentle',
    },
  },
  {
    id: 'overfitting',
    delay: 1300,
    blocks: [
      {
        kind: 'p',
        text: '**Overfitting** is memorising instead of learning. A student who memorises last year’s exam answers aces the practice test — and collapses on the real one, because they learned *those answers*, not the subject.',
      },
      {
        kind: 'p',
        text: 'Models do the same: spectacular on training data, poor on new data. The telltale sign is that gap. The cures: more data, simpler models, regularisation, early stopping.',
      },
      { kind: 'cite', label: 'ML Course Notes · Unit 3, p.31', sourceId: 'unit3-p31' },
    ],
    chips: [
      { label: 'Quick check ✏️', to: 'ask-quiz-of', primary: true },
      { label: 'How do I detect it?', to: 'of-detect' },
    ],
  },
  {
    id: 'of-detect',
    delay: 1000,
    blocks: [
      {
        kind: 'p',
        text: 'Watch two curves during training: loss on the **training set** and on a **validation set** the model never trains on. When training loss keeps falling but validation loss turns and rises — that fork in the road is overfitting beginning, and it’s your cue to stop or regularise.',
      },
    ],
    chips: [{ label: 'Quick check ✏️', to: 'ask-quiz-of', primary: true }],
  },
  {
    id: 'ask-quiz-of',
    delay: 800,
    blocks: [{ kind: 'p', text: 'Quick check:' }],
    quiz: {
      id: 'ofq',
      question: 'Which of these is the classic signature of overfitting?',
      options: [
        'Great training performance, poor performance on unseen data',
        'Poor performance everywhere',
        'Identical training and test performance',
        'A very small model',
      ],
      correct: 0,
      onCorrect: 'ask-win',
      onWrong: 'ask-gentle',
    },
  },
  {
    id: 'neural-networks',
    delay: 1300,
    blocks: [
      {
        kind: 'p',
        text: 'A **neural network** is layers of tiny, simple decisions stacked into something expressive. Each neuron does one humble thing: weigh its inputs, add them up, and pass the result through a small non-linearity.',
      },
      {
        kind: 'p',
        text: 'The magic is depth: early layers learn simple patterns (edges, in images), later layers combine them into concepts (whiskers → cat). Training is just gradient descent adjusting all those weights at once, using **backpropagation** to figure out each weight’s share of the blame for the error.',
      },
      {
        kind: 'p',
        text: 'Heads up: this is your **Neural Networks milestone** on the Machine Learning roadmap — we’ll do it properly there, with practice.',
      },
    ],
    chips: [
      { label: 'Sounds good — back to today’s topic', to: 'ask-redirect', primary: true },
      { label: 'One more question', to: 'ask-open' },
    ],
  },
  {
    id: 'ask-gentle',
    delay: 1100,
    thinking: 'Let’s approach it differently…',
    blocks: [
      {
        kind: 'p',
        text: 'Almost — and the miss tells me exactly which part to firm up. Read the explanation once more, and notice the key contrast; then it usually locks in for good.',
      },
    ],
    chips: [
      { label: 'Got it — continue', to: 'ask-win', primary: true },
    ],
  },
  {
    id: 'ask-win',
    delay: 900,
    blocks: [
      {
        kind: 'p',
        text: 'Nicely done. I’ve noted this in your learning history — it’ll shape what I suggest next. Anything else on your mind, or back to your mission?',
      },
    ],
    chips: [
      { label: 'Back to today’s mission', to: 'go-mission', primary: true },
      { label: 'Ask something else', to: 'ask-open' },
    ],
  },
  {
    id: 'ask-open',
    delay: 700,
    blocks: [{ kind: 'p', text: 'Go ahead — ask me anything. Big or small, I’ll meet you where you are.' }],
  },
  {
    id: 'ask-redirect',
    delay: 800,
    blocks: [
      {
        kind: 'p',
        text: 'Good instinct. Today’s mission is **Precision & Recall** — 25 focused minutes and it’s done. Shall we?',
      },
    ],
    chips: [{ label: 'Take me there', to: 'go-pr', primary: true }],
  },
  {
    id: 'fallback',
    delay: 1400,
    thinking: 'Thinking about the best way in…',
    blocks: [
      {
        kind: 'p',
        text: 'Here’s how I’d approach that. First I’d anchor it to something you already know well — your fundamentals in Python and statistics are strong, so we’d build from there. Then we’d test the understanding with one or two applied questions, because that’s where real gaps show up.',
      },
      {
        kind: 'p',
        text: 'If this is a topic you want to learn properly, the best move is a small roadmap — I can sequence it, schedule it around your week, and track mastery as we go.',
      },
    ],
    chips: [
      { label: 'Create a roadmap for it', to: 'go-create', primary: true },
      { label: 'Just explore for now', to: 'ask-open' },
    ],
  },
]

/* ---------- Generic per-topic sessions (review topics etc.) ---------- */

function genericNodes(title: string): ScriptNode[] {
  return [
    {
      id: 'intro',
      delay: 1100,
      blocks: [
        {
          kind: 'p',
          text: `Let's spend some time on **${title}**. I'll start from what you already know, check understanding as we go, and adapt if anything feels shaky. Where would you like to begin?`,
        },
      ],
      chips: [
        { label: 'Give me the core idea', to: 'core', primary: true },
        { label: 'Quiz me first to find gaps', to: 'go-quiz' },
      ],
    },
    {
      id: 'core',
      delay: 1300,
      blocks: [
        {
          kind: 'p',
          text: `The way to learn **${title}** efficiently: one core mental model, one worked example, then immediate practice. Based on your recent sessions, you learn fastest with a concrete example first — so that's how I'll teach it.`,
        },
        {
          kind: 'p',
          text: 'In the full product this session streams from the AI tutor. For this prototype, the fully-scripted experience lives in **Precision & Recall** — today’s mission topic. Want to jump there?',
        },
      ],
      chips: [
        { label: 'Go to Precision & Recall', to: 'go-pr', primary: true },
        { label: 'Practice this topic instead', to: 'go-quiz' },
      ],
    },
    {
      id: 'fallback',
      delay: 1000,
      blocks: [
        {
          kind: 'p',
          text: 'Good question. Let me anchor us first: the fully-interactive tutoring demo lives in **Precision & Recall**, your current mission topic — the adaptive loop there shows exactly how I teach.',
        },
      ],
      chips: [{ label: 'Take me there', to: 'go-pr', primary: true }],
    },
  ]
}

/* ---------- Script registry ---------- */

export interface TutorScript {
  nodes: Record<string, ScriptNode>
  entry: string
  /** Maps free text to a node id. */
  route: (text: string) => string
}

function toMap(nodes: ScriptNode[]): Record<string, ScriptNode> {
  return Object.fromEntries(nodes.map((n) => [n.id, n]))
}

const prRoute = (text: string): string => {
  const t = text.toLowerCase()
  if (/(simpl|easier|confus|lost)/.test(t)) return 'simpler'
  if (/analog/.test(t)) return 'analogy'
  if (/(real|world|example)/.test(t)) return 'real-world'
  if (/(deep|more|advanced|f1|threshold)/.test(t)) return 'deeper'
  if (/(visual|picture|diagram|see)/.test(t)) return 'visual'
  if (/(math|formula|equation)/.test(t)) return 'mathematical'
  if (/(code|python|sklearn)/.test(t)) return 'with-code'
  if (/(test|quiz|question|practice)/.test(t)) return 'quiz1'
  return 'fallback'
}

const askRoute = (text: string): string => {
  const t = text.toLowerCase()
  if (/(gradient|descent|learning rate)/.test(t)) return 'gradient-descent'
  if (/overfit/.test(t)) return 'overfitting'
  if (/(neural|deep learning|network)/.test(t)) return 'neural-networks'
  if (/(rag|retrieval)/.test(t)) return 'gradient-descent' // rag has own topic; nudge via fallback
  if (/(precision|recall)/.test(t)) return 'ask-redirect'
  return 'fallback'
}

const ragRoute = (text: string): string => {
  const t = text.toLowerCase()
  if (/(how|work|pipeline|step)/.test(t)) return 'how'
  if (/(why|matter|point)/.test(t)) return 'why'
  if (/(test|quiz|check)/.test(t)) return 'rag-quiz'
  return 'fallback'
}

export function scriptFor(topicId: string, title: string): TutorScript {
  if (topicId === 'precision-recall') {
    return { nodes: toMap(prNodes), entry: 'intro', route: prRoute }
  }
  if (topicId === 'what-is-rag') {
    return { nodes: toMap(ragNodes), entry: 'intro', route: ragRoute }
  }
  if (topicId === 'ask') {
    return { nodes: toMap(askNodes), entry: 'ask-open', route: askRoute }
  }
  const g = genericNodes(title)
  return {
    nodes: toMap(g),
    entry: 'intro',
    route: () => 'fallback',
  }
}
