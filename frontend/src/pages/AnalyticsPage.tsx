import { useSearchParams } from 'react-router-dom';
import { BatchPicker } from '../components/analytics/BatchPicker';
import { KpiCard } from '../components/analytics/KpiCard';
import { OutcomeDistributionChart } from '../components/analytics/OutcomeDistributionChart';
import { RateBarChart } from '../components/analytics/RateBarChart';
import { RoundsDurationTiles } from '../components/analytics/RoundsDurationTiles';
import { RunsTable } from '../components/analytics/RunsTable';
import { PageContainer } from '../components/layout/PageContainer';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { LoadingState } from '../components/ui/LoadingState';
import { useManifest, useMultipleBatchData } from '../lib/data-loading';
import { fmtPct } from '../lib/format';
import type { BatchSummary } from '../types/negotiation';
import { useUploadedData } from '../lib/uploaded-data-context';

interface KpiDeltaInput {
  text: string;
  direction: 'up' | 'down' | 'flat';
  goodDirection: 'up' | 'down';
}

function pctPointDelta(current: number | null, baseline: number | null, goodDirection: 'up' | 'down'): KpiDeltaInput | null {
  if (current === null || baseline === null) return null;
  const diffPp = Math.round((current - baseline) * 100);
  if (diffPp === 0) return { text: '±0pp', direction: 'flat', goodDirection };
  return { text: `${diffPp > 0 ? '+' : ''}${diffPp}pp`, direction: diffPp > 0 ? 'up' : 'down', goodDirection };
}

function numberDelta(current: number, baseline: number, digits: number, suffix: string, goodDirection: 'up' | 'down'): KpiDeltaInput | null {
  const diff = current - baseline;
  if (Math.abs(diff) < 10 ** -digits / 2) return { text: `±0${suffix}`, direction: 'flat', goodDirection };
  return {
    text: `${diff > 0 ? '+' : ''}${diff.toFixed(digits)}${suffix}`,
    direction: diff > 0 ? 'up' : 'down',
    goodDirection,
  };
}

function batchLabel(batch: BatchSummary): string {
  return `${batch.scenario_id} · ${batch.timestamp}`;
}

function BatchPanel({ batch, baseline }: { batch: BatchSummary; baseline: BatchSummary | null }) {
  const isBaseline = baseline === batch;
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold text-ink">{batch.scenario_title}</h2>
        <span className="text-xs text-ink-muted">
          {batch.scenario_id} · {batch.timestamp}
          {isBaseline && ' · baseline'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <KpiCard
          label="Agreement rate"
          value={fmtPct(batch.metrics.agreement_rate)}
          delta={!isBaseline && baseline ? pctPointDelta(batch.metrics.agreement_rate, baseline.metrics.agreement_rate, 'up') : null}
        />
        <KpiCard
          label="Deadlock rate"
          value={fmtPct(batch.metrics.deadlock_rate)}
          delta={!isBaseline && baseline ? pctPointDelta(batch.metrics.deadlock_rate, baseline.metrics.deadlock_rate, 'down') : null}
        />
        <KpiCard
          label="Manifest-error detection"
          value={fmtPct(batch.metrics.manifest_error_detection_rate)}
          delta={
            !isBaseline && baseline
              ? pctPointDelta(batch.metrics.manifest_error_detection_rate, baseline.metrics.manifest_error_detection_rate, 'up')
              : null
          }
        />
        <KpiCard
          label="Avg. rounds"
          value={batch.metrics.average_rounds_to_conclusion.toFixed(1)}
          delta={
            !isBaseline && baseline
              ? numberDelta(batch.metrics.average_rounds_to_conclusion, baseline.metrics.average_rounds_to_conclusion, 1, '', 'down')
              : null
          }
        />
        <KpiCard
          label="Avg. duration"
          value={`${batch.metrics.average_duration_seconds.toFixed(1)}s`}
          delta={
            !isBaseline && baseline
              ? numberDelta(batch.metrics.average_duration_seconds, baseline.metrics.average_duration_seconds, 1, 's', 'down')
              : null
          }
        />
      </div>

      <RunsTable runs={batch.individual_runs} title={`Run ledger — ${batchLabel(batch)}`} />
    </div>
  );
}

export function AnalyticsPage() {
  const { status: manifestStatus, data: manifest, error: manifestError } = useManifest();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedIds = (searchParams.get('batches') ?? '').split(',').filter(Boolean);

  function setSelectedIds(ids: string[]) {
    const next = new URLSearchParams(searchParams);
    if (ids.length) next.set('batches', ids.join(','));
    else next.delete('batches');
    setSearchParams(next);
  }

  const { status: batchesStatus, dataById, errorsById } = useMultipleBatchData(selectedIds);

  if (manifestStatus === 'loading') {
    return (
      <PageContainer>
        <LoadingState label="Loading batches…" />
      </PageContainer>
    );
  }
  if (manifestStatus === 'error' || !manifest) {
    return (
      <PageContainer>
        <ErrorState title="Could not load the batch manifest" error={manifestError} />
      </PageContainer>
    );
  }

  const selectedBatches = selectedIds.map((id) => dataById.get(id)).filter((b): b is BatchSummary => Boolean(b));
  const baseline = selectedBatches[0] ?? null;

  return (
    <PageContainer>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Docket analytics</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Compare batch evaluation runs — agreement rate, deadlock rate, manifest-error detection, rounds and
          duration to conclusion.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <BatchPicker batches={manifest.batches} selectedIds={selectedIds} onChange={setSelectedIds} />

        <div className="flex flex-col gap-8">
          {manifest.batches.length === 0 && (
            <EmptyState
              title="No batch evaluations found"
              description="Run tests/run_batch_evaluation.py and re-run `npm run sync-data` to populate this view."
            />
          )}

          {manifest.batches.length > 0 && selectedIds.length === 0 && (
            <EmptyState title="Select one or more batches to compare" description="Up to 4 at a time." />
          )}

          {selectedIds.length > 0 && batchesStatus === 'loading' && <LoadingState label="Loading batch data…" />}

          {[...errorsById.entries()].map(([id, error]) => (
            <ErrorState key={id} title={`Could not load batch ${id}`} error={error} />
          ))}

          {selectedBatches.length > 0 && (
            <>
              <RateBarChart
                data={selectedBatches.map((b) => ({
                  label: batchLabel(b),
                  agreement: b.metrics.agreement_rate,
                  deadlock: b.metrics.deadlock_rate,
                  detection: b.metrics.manifest_error_detection_rate,
                }))}
              />
              <OutcomeDistributionChart
                data={selectedBatches.map((b) => ({ label: batchLabel(b), distribution: b.metrics.outcome_distribution }))}
              />
              <RoundsDurationTiles
                rows={selectedBatches.map((b, i) => ({
                  id: selectedIds[i],
                  label: batchLabel(b),
                  avgRounds: b.metrics.average_rounds_to_conclusion,
                  avgDurationSeconds: b.metrics.average_duration_seconds,
                }))}
              />

              <div className="flex flex-col gap-8">
                {selectedBatches.map((batch) => (
                  <BatchPanel key={batchLabel(batch)} batch={batch} baseline={baseline} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

export function UploadedAnalyticsPage() {
  const { doc } = useUploadedData();

  if (!doc || doc.kind !== 'batch') {
    return (
      <PageContainer>
        <EmptyState
          title="No uploaded batch loaded"
          description="Drop a batch_summary.json file on the landing page to view it here."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">{doc.data.scenario_title}</h1>
        <p className="mt-1 text-sm text-ink-secondary">Uploaded batch — {doc.data.scenario_id}</p>
      </div>
      <div className="flex flex-col gap-8">
        <BatchPanel batch={doc.data} baseline={null} />
      </div>
    </PageContainer>
  );
}
