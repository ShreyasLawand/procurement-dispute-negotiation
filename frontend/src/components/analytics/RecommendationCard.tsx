import { Gavel } from 'lucide-react';
import { useEffect, useState } from 'react';
import { API_BASE } from '../../lib/api-config';
import { fmtPct } from '../../lib/format';
import type { SettlementRecommendation } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { Stamp } from '../ui/Stamp';

// Fetched live from /api/recommendation/{batchId} (src/recommendation/settlement_recommendation.py) —
// unlike the rest of this page, which reads pre-synced static JSON, this needs the API server running.
// That's a deliberate, contained exception: the recommendation is pure aggregation with no LLM call, so
// there's no cost to computing it on demand, and it keeps this feature out of the sync-data build step.
export function RecommendationCard({ batchId }: { batchId: string }) {
  const [state, setState] = useState<
    { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; data: SettlementRecommendation }
  >({ status: 'loading' });

  useEffect(() => {
    let cancelled = false;
    setState({ status: 'loading' });
    fetch(`${API_BASE}/api/recommendation/${batchId}`)
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new Error(body?.detail ?? `Recommendation unavailable (${res.status})`);
        }
        return res.json() as Promise<{ recommendation: SettlementRecommendation }>;
      })
      .then((data) => {
        if (!cancelled) setState({ status: 'ready', data: data.recommendation });
      })
      .catch((err) => {
        if (!cancelled) setState({ status: 'error', message: err instanceof Error ? err.message : String(err) });
      });
    return () => {
      cancelled = true;
    };
  }, [batchId]);

  // A recommendation server isn't guaranteed to be running when this static page is
  // viewed — fail quietly rather than blocking the rest of the analytics panel.
  if (state.status === 'error') return null;
  if (state.status === 'loading') {
    return (
      <Card className="text-sm text-ink-muted">
        <p>Synthesising settlement recommendation…</p>
      </Card>
    );
  }

  const rec = state.data;
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Gavel className="h-4 w-4 text-ink-secondary" />
        <h3 className="text-sm font-semibold text-ink">Settlement recommendation</h3>
        <span className="text-xs text-ink-muted">non-binding — see framing below</span>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Stamp tone="neutral" label={rec.modal_outcome} />
        <span className="text-xs text-ink-muted">{fmtPct(rec.confidence)} confidence · n={rec.n_runs}</span>
      </div>
      <p className="text-sm text-ink-secondary">{rec.modal_outcome_meaning}</p>

      {rec.dissenting_outcomes.length > 0 && (
        <div className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3 text-sm">
          <p className="font-medium text-ink">Dissenting outcomes — do not ignore these:</p>
          <ul className="mt-1 list-disc pl-5 text-ink-secondary">
            {rec.dissenting_outcomes.map((d) => (
              <li key={d.outcome}>
                {fmtPct(d.share)} ({d.n_runs}/{rec.n_runs}) reached: {d.outcome}
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="text-sm text-ink-secondary">{rec.rationale}</p>
      <p className="border-t border-hairline pt-3 text-xs text-ink-muted">{rec.framing_caveat}</p>
    </Card>
  );
}
