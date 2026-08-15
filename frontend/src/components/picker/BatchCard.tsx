import { ArrowRight, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fmtDate, fmtPct } from '../../lib/format';
import type { ManifestBatchEntry } from '../../types/negotiation';
import { Card } from '../ui/Card';

export function BatchCard({ entry }: { entry: ManifestBatchEntry }) {
  return (
    <Link to={`/analytics?batches=${entry.id}`} className="group block">
      <Card className="flex h-full flex-col gap-3 transition-shadow group-hover:shadow-md">
        <div className="flex items-start justify-between gap-3">
          <span className="rounded-md bg-page px-2 py-1 text-xs font-semibold text-ink-secondary">
            {entry.scenarioId}
          </span>
          <span className="flex items-center gap-1 text-xs text-ink-muted">
            <Layers className="h-3.5 w-3.5" />
            {entry.nRunsSuccessful}/{entry.nRunsRequested} runs
          </span>
        </div>
        <div>
          <p className="font-medium leading-snug text-ink">{entry.scenarioTitle}</p>
          <p className="mt-1 text-sm text-ink-secondary">
            Resolution rate {fmtPct(entry.metrics.resolution_rate)} · Manifest-error detection{' '}
            {fmtPct(entry.metrics.manifest_error_detection_rate)}
          </p>
        </div>
        <div className="mt-auto flex items-center justify-between pt-2 text-xs text-ink-muted">
          <span>{fmtDate(entry.timestampIso)}</span>
          <ArrowRight className="h-4 w-4 text-ink-muted transition-transform group-hover:translate-x-0.5 group-hover:text-ca" />
        </div>
      </Card>
    </Link>
  );
}
