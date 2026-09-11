import type { QuizQuestion } from '@/types'

export const quizBank: Record<string, QuizQuestion[]> = {
  'precision-recall': [
    {
      id: 'pr-1',
      prompt: 'Precision answers which question?',
      options: [
        'Of everything the model flagged as positive, how many actually were?',
        'Of all the real positives, how many did the model catch?',
        'How many predictions were correct overall?',
        'How balanced are the two classes in the dataset?',
      ],
      correct: 0,
      explanation:
        'Precision looks only at the model’s positive predictions and asks how many were right: TP / (TP + FP). The second option describes recall.',
      tag: 'Definitions',
    },
    {
      id: 'pr-2',
      prompt:
        'A spam filter marks 50 emails as spam. 40 of them really are spam. What is its precision?',
      options: ['80%', '40%', '90%', 'Not enough information'],
      correct: 0,
      explanation:
        'Precision = TP / (TP + FP) = 40 / 50 = 80%. You don’t need the false negatives for precision — that’s recall’s job.',
      tag: 'Applications',
    },
    {
      id: 'pr-3',
      prompt:
        'You’re building a screening model for a serious disease. Missing a sick patient is far worse than an extra follow-up test. Which metric should you prioritise?',
      options: ['Recall', 'Precision', 'Accuracy', 'Specificity'],
      correct: 0,
      explanation:
        'A missed sick patient is a false negative, and recall = TP / (TP + FN) is exactly the metric that punishes false negatives.',
      tag: 'Applications',
    },
    {
      id: 'pr-4',
      prompt: 'A model has high precision but low recall. What is it doing?',
      options: [
        'Being conservative — few false alarms, but it misses many real positives',
        'Being aggressive — flagging everything it can',
        'Performing perfectly on both classes',
        'Overfitting to the negative class',
      ],
      correct: 0,
      explanation:
        'High precision means its positive calls are trustworthy; low recall means it makes those calls rarely and misses many true positives. A cautious model.',
      tag: 'Concepts',
    },
    {
      id: 'pr-5',
      prompt: 'When is the F1 score most useful?',
      options: [
        'When you need one number balancing precision and recall on imbalanced data',
        'When the dataset is perfectly balanced',
        'When false positives don’t matter at all',
        'When you want to measure training speed',
      ],
      correct: 0,
      explanation:
        'F1 is the harmonic mean of precision and recall. It stays low unless both are reasonably high, which makes it a good single summary on imbalanced problems.',
      tag: 'Definitions',
    },
  ],
  'precision-recall-check': [
    {
      id: 'prc-1',
      prompt:
        'A fraud model reviews 1,000 transactions: 20 are fraud. It flags 25, of which 15 are truly fraud. What is its recall?',
      options: ['75%', '60%', '15%', '83%'],
      correct: 0,
      explanation:
        'Recall = TP / (TP + FN) = 15 / 20 = 75%. It caught 15 of the 20 real frauds. (Precision here would be 15/25 = 60%.)',
      tag: 'Applications',
    },
    {
      id: 'prc-2',
      prompt:
        'You raise a classifier’s decision threshold from 0.5 to 0.9. What typically happens?',
      options: [
        'Precision rises, recall falls',
        'Recall rises, precision falls',
        'Both rise together',
        'Neither changes',
      ],
      correct: 0,
      explanation:
        'A stricter threshold means the model only flags cases it’s very sure about — fewer false alarms (higher precision) but more misses (lower recall).',
      tag: 'Concepts',
    },
    {
      id: 'prc-3',
      prompt:
        'A dataset is 99% negative. A model that predicts “negative” for everything scores 99% accuracy. What does this show?',
      options: [
        'Accuracy can hide total failure on the class you care about',
        'The model is production-ready',
        'Precision must also be 99%',
        'Recall must also be 99%',
      ],
      correct: 0,
      explanation:
        'Its recall on the positive class is 0% — it never catches a single positive. This is exactly why precision and recall exist.',
      tag: 'Concepts',
    },
  ],
  generic: [
    {
      id: 'g-1',
      prompt: 'What does a confusion matrix show?',
      options: [
        'How predictions break down into true/false positives and negatives',
        'The training loss over time',
        'The correlation between features',
        'The model’s architecture',
      ],
      correct: 0,
      explanation:
        'It’s a 2×2 (or larger) table of predicted vs. actual classes — the raw counts every classification metric is built from.',
      tag: 'Definitions',
    },
    {
      id: 'g-2',
      prompt: 'Which of these is a sign of overfitting?',
      options: [
        'Great performance on training data, poor performance on new data',
        'Poor performance on both training and test data',
        'Identical performance everywhere',
        'A small model size',
      ],
      correct: 0,
      explanation:
        'Overfitting means the model memorised the training set instead of learning patterns that generalise.',
      tag: 'Concepts',
    },
    {
      id: 'g-3',
      prompt: 'Gradient descent updates parameters in the direction that…',
      options: [
        'Reduces the loss function',
        'Increases the learning rate',
        'Maximises the number of features',
        'Balances the classes',
      ],
      correct: 0,
      explanation:
        'It follows the negative gradient of the loss — the steepest downhill direction — taking small steps toward lower error.',
      tag: 'Definitions',
    },
    {
      id: 'g-4',
      prompt: 'Why do we hold out a test set?',
      options: [
        'To estimate how the model performs on data it has never seen',
        'To speed up training',
        'To increase the dataset size',
        'To tune the model on it repeatedly',
      ],
      correct: 0,
      explanation:
        'The test set simulates the real world. Touching it during training quietly turns it into training data.',
      tag: 'Concepts',
    },
    {
      id: 'g-5',
      prompt: 'A learning rate that is far too large usually causes…',
      options: [
        'The loss to bounce around or diverge instead of settling',
        'Perfectly smooth convergence',
        'Slower but safer training',
        'No effect at all',
      ],
      correct: 0,
      explanation:
        'Huge steps overshoot the minimum, so the loss oscillates or explodes. Too small, and training crawls.',
      tag: 'Applications',
    },
  ],
}

export function questionsFor(topicId: string, mode: 'practice' | 'check'): QuizQuestion[] {
  if (mode === 'check') {
    return quizBank[`${topicId}-check`] ?? quizBank['precision-recall-check']
  }
  return quizBank[topicId] ?? quizBank.generic
}
