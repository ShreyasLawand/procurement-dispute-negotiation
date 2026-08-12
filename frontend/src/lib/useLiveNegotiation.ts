import { useEffect, useState } from 'react';
import { API_BASE } from './api-config';
import type {
  ComplianceAssessment,
  DisputeScenario,
  NegotiationMessage,
  NegotiationState,
  NegotiationSummary,
  PreNegotiationStatement,
  WinStatement,
} from '../types/negotiation';

export type ConnectionStatus = 'idle' | 'connecting' | 'open' | 'closed' | 'error';

export interface LiveNegotiation {
  connectionStatus: ConnectionStatus;
  phase: string | null;
  statusMessage: string | null;
  state: NegotiationState | null;
  error: string | null;
  isDone: boolean;
}

function emptyState(scenario: DisputeScenario, maxRounds: number): NegotiationState {
  return {
    scenario,
    round_number: 0,
    max_rounds: maxRounds,
    ca_pre_negotiation: null,
    bidder_pre_negotiation: null,
    messages: [],
    compliance_checks: [],
    resolved: false,
    resolution_outcome: null,
    adjudicated: false,
    ca_win_statement: null,
    bidder_win_statement: null,
    summary: null,
  };
}

function parseData<T>(e: Event): T {
  return JSON.parse((e as MessageEvent).data) as T;
}

/**
 * Consumes the SSE stream from POST /api/negotiations -> GET
 * /api/negotiations/{id}/stream, progressively building a full
 * NegotiationState-shaped object as events arrive. The result is fed
 * directly into <CaseFileView state={...} /> — that component already
 * gates every section on data presence, so no separate "live mode" is
 * needed there.
 */
export function useLiveNegotiation(
  sessionId: string | null,
  scenario: DisputeScenario | null,
  maxRounds: number
): LiveNegotiation {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('idle');
  const [phase, setPhase] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [state, setState] = useState<NegotiationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    if (!sessionId || !scenario) return;

    setState(emptyState(scenario, maxRounds));
    setConnectionStatus('connecting');
    setPhase(null);
    setStatusMessage(null);
    setIsDone(false);
    setError(null);

    const finishedRef = { current: false };
    const es = new EventSource(`${API_BASE}/api/negotiations/${sessionId}/stream`);

    es.onopen = () => setConnectionStatus('open');

    es.addEventListener('pre_negotiation', (e) => {
      const data = parseData<{
        ca_pre_negotiation: PreNegotiationStatement;
        bidder_pre_negotiation: PreNegotiationStatement;
      }>(e);
      setPhase('pre_negotiation');
      setState((s) =>
        s && {
          ...s,
          ca_pre_negotiation: data.ca_pre_negotiation,
          bidder_pre_negotiation: data.bidder_pre_negotiation,
        }
      );
    });

    const handleRound = (name: string) => (e: Event) => {
      const data = parseData<{ round_number: number; message: NegotiationMessage }>(e);
      setPhase(name);
      setState((s) => s && { ...s, round_number: data.round_number, messages: [...s.messages, data.message] });
    };
    es.addEventListener('ca_round', handleRound('ca_round'));
    es.addEventListener('bidder_round', handleRound('bidder_round'));

    es.addEventListener('court_check', (e) => {
      const data = parseData<{
        compliance_check: ComplianceAssessment;
        resolved: boolean;
        resolution_outcome: string | null;
      }>(e);
      setPhase('court_check');
      setState(
        (s) =>
          s && {
            ...s,
            compliance_checks: [...s.compliance_checks, data.compliance_check],
            resolved: data.resolved,
            resolution_outcome: data.resolution_outcome,
          }
      );
    });

    es.addEventListener('win_statements', (e) => {
      const data = parseData<{ ca_win_statement: WinStatement; bidder_win_statement: WinStatement }>(e);
      setPhase('win_statements');
      setState(
        (s) => s && { ...s, ca_win_statement: data.ca_win_statement, bidder_win_statement: data.bidder_win_statement }
      );
    });

    es.addEventListener('summary', (e) => {
      const data = parseData<{ summary: NegotiationSummary }>(e);
      setPhase('summary');
      setState((s) => s && { ...s, summary: data.summary });
    });

    es.addEventListener('status', (e) => {
      const data = parseData<{ message: string }>(e);
      setStatusMessage(data.message);
    });

    es.addEventListener('done', () => {
      finishedRef.current = true;
      setIsDone(true);
      setConnectionStatus('closed');
      es.close();
    });

    // A server-sent `event: error` frame and a genuine browser connection
    // failure both dispatch as the EventSource "error" event type — this is
    // the single handler for both, distinguished by whether a JSON payload
    // is present.
    es.addEventListener('error', (e) => {
      if (finishedRef.current) return;
      finishedRef.current = true;
      try {
        const data = parseData<{ message: string }>(e);
        setError(data.message);
      } catch {
        setError('Connection to the negotiation stream was lost.');
      }
      setConnectionStatus('error');
      es.close();
    });

    return () => {
      finishedRef.current = true;
      es.close();
    };
  }, [sessionId, scenario, maxRounds]);

  return { connectionStatus, phase, statusMessage, state, error, isDone };
}
