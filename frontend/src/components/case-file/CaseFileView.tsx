import type { NegotiationState } from '../../types/negotiation';
import { CaseHeader } from './CaseHeader';
import { OutcomeRibbon } from './OutcomeRibbon';
import { PreNegotiationCard } from './PreNegotiationCard';
import { SummaryPanel } from './SummaryPanel';
import { TranscriptThread } from './TranscriptThread';
import { WinStatementCard } from './WinStatementCard';

export function CaseFileView({ state }: { state: NegotiationState }) {
  return (
    <div className="flex flex-col gap-6">
      <CaseHeader scenario={state.scenario} roundNumber={state.round_number} maxRounds={state.max_rounds} />

      {(state.ca_pre_negotiation || state.bidder_pre_negotiation) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {state.ca_pre_negotiation && <PreNegotiationCard statement={state.ca_pre_negotiation} />}
          {state.bidder_pre_negotiation && <PreNegotiationCard statement={state.bidder_pre_negotiation} />}
        </div>
      )}

      {state.messages.length > 0 && (
        <TranscriptThread messages={state.messages} complianceChecks={state.compliance_checks} />
      )}

      {/* Gated on resolution_outcome being set, not rendered unconditionally
          — for a live/in-progress negotiation, resolved defaults to false
          before any outcome exists, which would otherwise show a
          misleading "Deadlock" ribbon before the negotiation has actually
          concluded. Every completed static log already has
          resolution_outcome set (including the deadlock string), so this
          changes nothing for the existing static/analytics view. */}
      {state.resolution_outcome !== null && (
        <OutcomeRibbon resolved={state.resolved} outcome={state.resolution_outcome} />
      )}

      {/* Gated on the field being non-null, not on `resolved` — deadlocked
          negotiations still populate a summary and win statements. */}
      {state.summary && <SummaryPanel summary={state.summary} />}

      {(state.ca_win_statement || state.bidder_win_statement) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {state.ca_win_statement && <WinStatementCard statement={state.ca_win_statement} />}
          {state.bidder_win_statement && <WinStatementCard statement={state.bidder_win_statement} />}
        </div>
      )}
    </div>
  );
}
