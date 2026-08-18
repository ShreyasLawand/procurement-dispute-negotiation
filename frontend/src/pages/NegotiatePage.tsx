import { Sparkles } from 'lucide-react';
import { CaseFileView } from '../components/case-file/CaseFileView';
import { PageContainer } from '../components/layout/PageContainer';
import { GpuStatusBanner } from '../components/negotiate/GpuStatusBanner';
import { LiveStatusBar } from '../components/negotiate/LiveStatusBar';
import { RiskScreenPanel } from '../components/negotiate/RiskScreenPanel';
import { ScenarioPreviewCard } from '../components/negotiate/ScenarioPreviewCard';
import { Button } from '../components/ui/Button';
import { ErrorState } from '../components/ui/ErrorState';
import { MultiFileDropzone } from '../components/upload/MultiFileDropzone';
import { useNegotiationDraft } from '../lib/negotiation-draft-context';

export function NegotiatePage() {
  const {
    stage,
    files,
    setFiles,
    scenario,
    maxRounds,
    setMaxRounds,
    extracting,
    extractError,
    starting,
    startError,
    live,
    handleExtract,
    handleStart,
    handleReset,
  } = useNegotiationDraft();

  return (
    <PageContainer>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Negotiate a new case</h1>
          <p className="mt-1 text-sm text-ink-secondary">
            Upload real case documents and watch the Contracting Authority, Aggrieved Bidder, and Court agents
            negotiate it live.
          </p>
        </div>
        {stage !== 'upload' && (
          <button type="button" onClick={handleReset} className="text-sm font-medium text-brand hover:underline">
            Start over
          </button>
        )}
      </div>

      <div className="mb-6">
        <GpuStatusBanner />
      </div>

      {stage === 'upload' && (
        <div className="flex flex-col gap-4">
          <MultiFileDropzone files={files} onFilesChange={setFiles} />
          {extractError !== null && <ErrorState title="Could not extract a scenario" error={extractError} />}
          <div className="flex justify-end">
            <Button onClick={handleExtract} disabled={files.length === 0 || extracting}>
              <Sparkles className="h-4 w-4" />
              {extracting ? 'Reading documents…' : 'Extract scenario'}
            </Button>
          </div>
        </div>
      )}

      {stage === 'preview' && scenario && (
        <div className="flex flex-col gap-4">
          <ScenarioPreviewCard
            scenario={scenario}
            maxRounds={maxRounds}
            onMaxRoundsChange={setMaxRounds}
            onStart={handleStart}
            starting={starting}
          />
          {startError !== null && <ErrorState title="Could not start the negotiation" error={startError} />}
          {/* Prevention comes before negotiation — screen for challenge risk on this
              procurement before simulating how a dispute over it would play out. */}
          <RiskScreenPanel />
        </div>
      )}

      {stage === 'running' && live.state && (
        <div className="flex flex-col gap-6">
          <LiveStatusBar
            connectionStatus={live.connectionStatus}
            statusMessage={live.statusMessage}
            isDone={live.isDone}
            error={live.error}
          />
          <CaseFileView state={live.state} />
        </div>
      )}
    </PageContainer>
  );
}
