import { Sparkles } from 'lucide-react';
import { useState } from 'react';
import { CaseFileView } from '../components/case-file/CaseFileView';
import { PageContainer } from '../components/layout/PageContainer';
import { LiveStatusBar } from '../components/negotiate/LiveStatusBar';
import { RiskScreenPanel } from '../components/negotiate/RiskScreenPanel';
import { ScenarioPreviewCard } from '../components/negotiate/ScenarioPreviewCard';
import { Button } from '../components/ui/Button';
import { ErrorState } from '../components/ui/ErrorState';
import { MultiFileDropzone } from '../components/upload/MultiFileDropzone';
import { API_BASE } from '../lib/api-config';
import { useLiveNegotiation } from '../lib/useLiveNegotiation';
import type { DisputeScenario } from '../types/negotiation';

type Stage = 'upload' | 'preview' | 'running';

export function NegotiatePage() {
  const [stage, setStage] = useState<Stage>('upload');
  const [files, setFiles] = useState<File[]>([]);
  const [scenario, setScenario] = useState<DisputeScenario | null>(null);
  const [maxRounds, setMaxRounds] = useState(3);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState<unknown>(null);
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState<unknown>(null);

  const live = useLiveNegotiation(sessionId, scenario, maxRounds);

  async function handleExtract() {
    setExtracting(true);
    setExtractError(null);
    try {
      const formData = new FormData();
      for (const file of files) formData.append('files', file);
      const res = await fetch(`${API_BASE}/api/extract`, { method: 'POST', body: formData });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? `Extraction failed (${res.status})`);
      }
      const data = (await res.json()) as { scenario: DisputeScenario };
      setScenario(data.scenario);
      setStage('preview');
    } catch (err) {
      setExtractError(err);
    } finally {
      setExtracting(false);
    }
  }

  async function handleStart() {
    if (!scenario) return;
    setStarting(true);
    setStartError(null);
    try {
      const res = await fetch(`${API_BASE}/api/negotiations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, max_rounds: maxRounds }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? `Could not start negotiation (${res.status})`);
      }
      const data = (await res.json()) as { session_id: string };
      setSessionId(data.session_id);
      setStage('running');
    } catch (err) {
      setStartError(err);
    } finally {
      setStarting(false);
    }
  }

  function handleReset() {
    setStage('upload');
    setFiles([]);
    setScenario(null);
    setSessionId(null);
    setExtractError(null);
    setStartError(null);
  }

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
