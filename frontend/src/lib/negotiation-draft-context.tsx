import { createContext, useContext, useState, type ReactNode } from 'react';
import { API_BASE, describeFetchError } from './api-config';
import { useLiveNegotiation, type LiveNegotiation } from './useLiveNegotiation';
import type { DisputeScenario } from '../types/negotiation';

export type NegotiationStage = 'upload' | 'preview' | 'running';

interface NegotiationDraftContextValue {
  stage: NegotiationStage;
  files: File[];
  setFiles: (files: File[]) => void;
  scenario: DisputeScenario | null;
  maxRounds: number;
  setMaxRounds: (n: number) => void;
  extracting: boolean;
  extractError: unknown;
  starting: boolean;
  startError: unknown;
  live: LiveNegotiation;
  handleExtract: () => Promise<void>;
  handleStart: () => Promise<void>;
  handleReset: () => void;
}

const NegotiationDraftContext = createContext<NegotiationDraftContextValue | null>(null);

/**
 * Owns NegotiatePage's whole in-progress state, mounted once at the App root rather than
 * inside NegotiatePage itself - react-router unmounts route components on navigation, which
 * was silently discarding an uploaded-but-not-yet-extracted file the moment the user switched
 * tabs and came back. The same unmount also tears down useLiveNegotiation's EventSource
 * (see its cleanup function), so a negotiation already running would have been killed by a
 * tab switch too, not just a pending upload - fixed the same way, by giving both a home that
 * outlives the page component.
 */
export function NegotiationDraftProvider({ children }: { children: ReactNode }) {
  const [stage, setStage] = useState<NegotiationStage>('upload');
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
      setExtractError(describeFetchError(err));
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
      setStartError(describeFetchError(err));
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

  const value: NegotiationDraftContextValue = {
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
  };

  return <NegotiationDraftContext.Provider value={value}>{children}</NegotiationDraftContext.Provider>;
}

export function useNegotiationDraft(): NegotiationDraftContextValue {
  const ctx = useContext(NegotiationDraftContext);
  if (!ctx) {
    throw new Error('useNegotiationDraft must be used within a NegotiationDraftProvider');
  }
  return ctx;
}
