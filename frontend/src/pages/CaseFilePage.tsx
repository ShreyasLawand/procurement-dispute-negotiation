import { ArrowLeft } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { CaseFileView } from '../components/case-file/CaseFileView';
import { PageContainer } from '../components/layout/PageContainer';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { LoadingState } from '../components/ui/LoadingState';
import { useCaseData } from '../lib/data-loading';
import { useUploadedData } from '../lib/uploaded-data-context';

function BackLink() {
  return (
    <Link to="/cases" className="mb-4 flex items-center gap-1.5 text-sm font-medium text-ink-secondary hover:text-ink">
      <ArrowLeft className="h-4 w-4" />
      Back to cases
    </Link>
  );
}

function UploadedCasePage() {
  const { doc } = useUploadedData();

  if (!doc || doc.kind !== 'case') {
    return (
      <PageContainer>
        <BackLink />
        <EmptyState
          title="No uploaded case loaded"
          description="Drop a negotiation log JSON file on the landing page to view it here."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <BackLink />
      <CaseFileView state={doc.data} />
    </PageContainer>
  );
}

function ManifestCasePage({ caseId }: { caseId: string }) {
  const { status, data, error } = useCaseData(caseId);

  return (
    <PageContainer>
      <BackLink />
      {status === 'loading' && <LoadingState label="Loading case…" />}
      {status === 'error' && <ErrorState title="Could not load this case" error={error} />}
      {status === 'success' && data && <CaseFileView state={data} />}
    </PageContainer>
  );
}

export function CaseFilePage() {
  const { caseId } = useParams<{ caseId: string }>();

  if (caseId === 'uploaded') {
    return <UploadedCasePage />;
  }
  if (!caseId) {
    return (
      <PageContainer>
        <EmptyState title="No case selected" />
      </PageContainer>
    );
  }
  return <ManifestCasePage caseId={caseId} />;
}
