import type { NegotiationSummary } from '../../types/negotiation';
import { Card } from '../ui/Card';

// Renders whenever `summary` is non-null — deliberately independent of the
// `resolved` flag, since a deadlock still runs the summary step.
export function SummaryPanel({ summary }: { summary: NegotiationSummary }) {
  return (
    <Card className="flex flex-col gap-5">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">Plain-English summary</h3>
      <blockquote className="border-l-4 border-l-hairline pl-4 text-base leading-relaxed text-ink">
        {summary.plain_english_summary}
      </blockquote>

      <div className="grid gap-5 border-t border-hairline pt-5 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Key sticking points</p>
          <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-sm text-ink-secondary">
            {summary.key_sticking_points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Concessions</p>
          <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">{summary.concessions_summary}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Court reasoning</p>
          <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">{summary.court_reasoning_summary}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Likely next steps</p>
          <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">{summary.likely_next_steps}</p>
        </div>
      </div>
    </Card>
  );
}
