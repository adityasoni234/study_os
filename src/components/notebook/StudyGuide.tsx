import { useState } from 'react'
import {
  AlertCircle,
  BookOpen,
  Braces,
  CheckSquare,
  GraduationCap,
  Lightbulb,
  ListChecks,
  RefreshCw,
  Sigma,
  Zap,
} from 'lucide-react'
import { Collapse } from '@/components/ui/Collapse'
import { CitationChip } from '@/components/tutor/blocks'
import { Button } from '@/components/ui/Button'

function Def({ term, def }: { term: string; def: string }) {
  return (
    <div className="rounded-xl border bg-card p-3.5">
      <dt className="text-[13px] font-bold">{term}</dt>
      <dd className="mt-1 text-[12.5px] leading-relaxed text-ink-soft">{def}</dd>
    </div>
  )
}

function Reveal({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-xl border bg-card p-3.5">
      <div className="text-[13.5px] leading-relaxed font-medium">{q}</div>
      {open ? (
        <p className="anim-fade mt-2 rounded-lg bg-mint-soft/70 px-3 py-2 text-[13px] leading-relaxed text-mint-ink">
          {a}
        </p>
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="mt-2 text-[12.5px] font-semibold text-indigo-ink transition-opacity hover:opacity-70"
        >
          Reveal answer →
        </button>
      )}
    </div>
  )
}

export function StudyGuide() {
  const [regenerating, setRegenerating] = useState(false)

  const regenerate = () => {
    setRegenerating(true)
    window.setTimeout(() => setRegenerating(false), 1800)
  }

  if (regenerating) {
    return (
      <div className="space-y-3 p-5">
        <div className="flex items-center gap-2.5 text-[13.5px] font-medium text-ink-soft">
          <RefreshCw size={14} className="animate-spin text-indigo" />
          Rebuilding your study guide from 4 sources…
        </div>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="skeleton h-14 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-[16px] font-semibold">Unit 3 — Model Evaluation</h3>
          <p className="mt-0.5 text-[12px] text-ink-faint">
            Generated from 4 sources · 12 citations · updated after your last quiz
          </p>
        </div>
        <Button size="sm" variant="secondary" onClick={regenerate}>
          <RefreshCw size={13} /> Regenerate
        </Button>
      </div>

      <div className="space-y-2.5">
        <Collapse title="Overview" icon={<BookOpen size={15} />} defaultOpen>
          <p className="text-[13.5px] leading-relaxed text-ink-soft">
            Accuracy alone can badly mislead you on imbalanced problems. This unit builds the four
            counts of the confusion matrix into the metrics that actually matter — precision,
            recall, F1 and ROC — and teaches you to pick the right one by asking a single question:{' '}
            <strong className="text-ink">which mistake is expensive here?</strong>
          </p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <CitationChip label="ML Course Notes · Unit 3, p.14" sourceId="unit3-p14" />
            <CitationChip label="StatQuest · 04:12" sourceId="statquest-412" />
          </div>
        </Collapse>

        <Collapse title="Core concepts" icon={<Lightbulb size={15} />} defaultOpen>
          <ul className="space-y-2.5">
            {[
              ['Confusion matrix', 'The 2×2 table of predicted vs. actual — TP, FP, FN, TN. Every metric below is arithmetic on these four numbers.'],
              ['Precision', 'Trustworthiness of positive calls. High precision = few false alarms.'],
              ['Recall', 'Coverage of real positives. High recall = few misses.'],
              ['The trade-off', 'Raising the decision threshold trades recall away for precision, and vice versa. You choose the balance based on error costs.'],
            ].map(([t, d]) => (
              <li key={t} className="flex gap-3 text-[13.5px] leading-relaxed">
                <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-indigo" />
                <span className="text-ink-soft">
                  <strong className="font-semibold text-ink">{t}.</strong> {d}
                </span>
              </li>
            ))}
          </ul>
        </Collapse>

        <Collapse title="Definitions" icon={<ListChecks size={15} />}>
          <dl className="grid gap-2.5 sm:grid-cols-2">
            <Def term="True Positive (TP)" def="Model said positive; it really was positive." />
            <Def term="False Positive (FP)" def="Model said positive; it was actually negative. A false alarm." />
            <Def term="False Negative (FN)" def="Model said negative; it was actually positive. A miss." />
            <Def term="Specificity" def="Of all real negatives, how many the model correctly left alone — TN / (TN + FP)." />
          </dl>
        </Collapse>

        <Collapse title="Important formulas" icon={<Sigma size={15} />}>
          <div className="space-y-2">
            {[
              ['Precision', 'TP / (TP + FP)'],
              ['Recall', 'TP / (TP + FN)'],
              ['F1 score', '2 · P · R / (P + R)'],
              ['Accuracy', '(TP + TN) / total — beware on imbalanced data'],
            ].map(([label, f]) => (
              <div key={label} className="flex items-center gap-3 rounded-lg border bg-card px-3.5 py-2">
                <span className="w-20 shrink-0 text-[11px] font-bold tracking-wide text-ink-faint uppercase">
                  {label}
                </span>
                <span className="text-[13.5px] font-semibold tracking-wide">{f}</span>
              </div>
            ))}
          </div>
          <div className="mt-3">
            <CitationChip label="ML Course Notes · Unit 3, p.15" sourceId="unit3-p15" />
          </div>
        </Collapse>

        <Collapse title="Worked example" icon={<Braces size={15} />}>
          <p className="text-[13.5px] leading-relaxed text-ink-soft">
            A fraud model reviews 1,000 transactions (20 real frauds). It flags 25, of which 15 are
            real. <strong className="text-ink">Precision = 15/25 = 60%</strong> (trust of its
            alarms), <strong className="text-ink">Recall = 15/20 = 75%</strong> (share of fraud
            caught). Whether that’s good depends entirely on the cost of the 5 false alarms vs. the
            5 missed frauds.
          </p>
        </Collapse>

        <Collapse title="Common mistakes" icon={<AlertCircle size={15} />}>
          <div className="space-y-2">
            {[
              'Swapping the denominators — precision divides by predicted positives, recall by actual positives.',
              'Trusting accuracy on imbalanced data. Predicting “majority class” for everything can score 99%.',
              'Optimising one metric to 100% and ignoring what it does to the other.',
            ].map((m) => (
              <div key={m} className="rounded-lg bg-amber-soft/70 px-3.5 py-2.5 text-[13px] leading-relaxed text-amber-ink">
                {m}
              </div>
            ))}
          </div>
        </Collapse>

        <Collapse title="Exam tips" icon={<GraduationCap size={15} />}>
          <ul className="space-y-1.5 text-[13.5px] leading-relaxed text-ink-soft">
            {[
              'Write the confusion matrix first — even when not asked. Every metric falls out of it.',
              'When a question mentions cost of mistakes, name the error type (FP or FN) before naming the metric.',
              'Remember: “don’t cry wolf” = precision, “don’t miss the wolf” = recall.',
            ].map((t) => (
              <li key={t} className="flex gap-2.5">
                <CheckSquare size={14} className="mt-[3px] shrink-0 text-mint" /> {t}
              </li>
            ))}
          </ul>
        </Collapse>

        <Collapse title="Practice questions" icon={<Zap size={15} />}>
          <div className="space-y-2.5">
            <Reveal
              q="A screening test flags 200 people; 160 truly have the condition. Precision?"
              a="160 / 200 = 80%. Recall would need the number of actual cases the test missed."
            />
            <Reveal
              q="Your model's precision is 0.95 but recall is 0.30. Describe its behaviour in one sentence."
              a="It's very cautious: almost every alarm it raises is right, but it misses 70% of real positives."
            />
            <Reveal
              q="Why is F1 the harmonic (not arithmetic) mean?"
              a="The harmonic mean collapses toward the smaller value, so a model can't hide terrible recall behind excellent precision."
            />
          </div>
        </Collapse>

        <Collapse title="Quick revision" icon={<Zap size={15} />}>
          <div className="flex flex-wrap gap-1.5">
            {[
              'Precision = TP/(TP+FP)',
              'Recall = TP/(TP+FN)',
              'F1 = 2PR/(P+R)',
              'Threshold ↑ → precision ↑, recall ↓',
              'Imbalance breaks accuracy',
              'Cost of mistake picks the metric',
            ].map((chip) => (
              <span key={chip} className="rounded-full border bg-card px-3 py-1.5 text-[12px] font-medium text-ink-soft">
                {chip}
              </span>
            ))}
          </div>
        </Collapse>
      </div>
    </div>
  )
}
