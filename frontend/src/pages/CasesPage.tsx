import { useNavigate } from 'react-router-dom';
import { BatchCard } from '../components/picker/BatchCard';
import { CaseCard } from '../components/picker/CaseCard';
import { FileDropzone } from '../components/upload/FileDropzone';
import { PageContainer } from '../components/layout/PageContainer';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { LoadingState } from '../components/ui/LoadingState';
import { useManifest } from '../lib/data-loading';
import type { ValidatedDoc } from '../lib/schema';
import { useUploadedData } from '../lib/uploaded-data-context';

export function CasesPage() {
  const { status, data: manifest, error } = useManifest();
  const navigate = useNavigate();
  const { setDoc } = useUploadedData();

  function handleUploaded(doc: ValidatedDoc) {
    setDoc(doc);
    navigate(doc.kind === 'case' ? '/case/uploaded' : '/analytics/uploaded');
  }

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-ink">Negotiation cases &amp; batch evaluations</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Output from the LangGraph multi-agent procurement dispute simulator — negotiation transcripts, Court
          compliance assessments, and batch evaluation metrics.
        </p>
      </div>

      {status === 'loading' && <LoadingState label="Loading manifest…" />}
      {status === 'error' && (
        <ErrorState
          title="Could not load data/manifest.json"
          error={error}
          className="mb-6"
        />
      )}

      {status === 'success' && manifest && (
        <div className="flex flex-col gap-10">
          <section>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted">Negotiation cases</h2>
            {manifest.cases.length === 0 ? (
              <EmptyState
                title="No negotiation logs found"
                description="Run tests/test_langgraph_negotiation.py and re-run `npm run sync-data` to populate this view."
              />
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {manifest.cases.map((entry) => (
                  <CaseCard key={entry.id} entry={entry} />
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted">Batch evaluations</h2>
            {manifest.batches.length === 0 ? (
              <EmptyState
                title="No batch evaluations found"
                description="Run tests/run_batch_evaluation.py and re-run `npm run sync-data` to populate this view."
              />
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {manifest.batches.map((entry) => (
                  <BatchCard key={entry.id} entry={entry} />
                ))}
              </div>
            )}
          </section>
        </div>
      )}

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted">Load a custom file</h2>
        <FileDropzone onLoaded={handleUploaded} />
      </section>
    </PageContainer>
  );
}
