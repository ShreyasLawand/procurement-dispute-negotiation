import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fmtDate, shortOutcome } from '../../lib/format';
import type { ManifestCaseEntry } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { Stamp } from '../ui/Stamp';

export function CaseCard({ entry }: { entry: ManifestCaseEntry }) {
  return (
    <Link to={`/case/${entry.id}`} className="group block">
      <Card className="flex h-full flex-col gap-3 transition-shadow group-hover:shadow-md">
        <div className="flex items-start justify-between gap-3">
          <span className="rounded-md bg-page px-2 py-1 text-xs font-semibold text-ink-secondary">
            {entry.scenarioId}
          </span>
          <Stamp tone={entry.resolved ? 'good' : 'warning'} label={entry.resolved ? 'Resolved' : 'Deadlock'} />
        </div>
        {entry.isRealCase && (
          <span className="inline-flex w-fit items-center rounded-full border border-brand/30 bg-brand-soft px-2.5 py-1 text-xs font-semibold text-brand-dark">
            Real case study
          </span>
        )}
        <div>
          <p className="font-medium leading-snug text-ink">{entry.title}</p>
          <p className="mt-1 text-sm text-ink-secondary">{shortOutcome(entry.outcome)}</p>
        </div>
        <div className="mt-auto flex items-center justify-between pt-2 text-xs text-ink-muted">
          <span>
            {entry.roundsTaken} / {entry.maxRounds} rounds · {fmtDate(entry.timestamp)}
          </span>
          <ArrowRight className="h-4 w-4 text-ink-muted transition-transform group-hover:translate-x-0.5 group-hover:text-ca" />
        </div>
      </Card>
    </Link>
  );
}
