import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { fmtDuration, shortOutcome } from '../../lib/format';
import type { BatchIndividualRun } from '../../types/negotiation';
import { Card } from '../ui/Card';

export function RunsTable({ runs, title }: { runs: BatchIndividualRun[]; title?: string }) {
  return (
    <Card padded={false}>
      <div className="border-b border-hairline px-5 py-4">
        <h3 className="text-sm font-semibold text-ink">{title ?? 'Run ledger'}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="text-left text-xs font-medium uppercase tracking-wide text-ink-muted">
              <th className="px-5 py-2 font-medium">Run</th>
              <th className="px-5 py-2 font-medium">Resolved</th>
              <th className="px-5 py-2 font-medium">Outcome</th>
              <th className="px-5 py-2 text-right font-medium">Rounds</th>
              <th className="px-5 py-2 font-medium">Manifest error</th>
              <th className="px-5 py-2 text-right font-medium">Duration</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.run_number} className="border-t border-hairline">
                <td className="px-5 py-2.5 tabular-nums text-ink">{run.run_number}</td>
                <td className="px-5 py-2.5">
                  {run.error ? (
                    <span className="flex items-center gap-1.5 text-critical" title={run.error}>
                      <XCircle className="h-4 w-4" /> Failed
                    </span>
                  ) : run.resolved ? (
                    <CheckCircle2 className="h-4 w-4 text-good" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-warning" />
                  )}
                </td>
                <td className="px-5 py-2.5 text-ink-secondary" title={run.outcome ?? undefined}>
                  {shortOutcome(run.outcome)}
                </td>
                <td className="px-5 py-2.5 text-right tabular-nums text-ink">{run.rounds_taken ?? '—'}</td>
                <td className="px-5 py-2.5">
                  {run.manifest_error_found_any_round === null ? (
                    <span className="text-ink-muted">—</span>
                  ) : run.manifest_error_found_any_round ? (
                    <span className="text-critical">Found</span>
                  ) : (
                    <span className="text-ink-muted">None</span>
                  )}
                </td>
                <td className="px-5 py-2.5 text-right tabular-nums text-ink">{fmtDuration(run.duration_seconds)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
