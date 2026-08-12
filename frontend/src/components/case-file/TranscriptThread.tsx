import type { ComplianceAssessment, NegotiationMessage } from '../../types/negotiation';
import { ComplianceCard } from './ComplianceCard';
import { MessageBubble } from './MessageBubble';

interface TranscriptThreadProps {
  messages: NegotiationMessage[];
  complianceChecks: ComplianceAssessment[];
}

export function TranscriptThread({ messages, complianceChecks }: TranscriptThreadProps) {
  const roundNumbers = Array.from(
    new Set([...messages.map((m) => m.round_number), ...complianceChecks.map((c) => c.round_number)])
  ).sort((a, b) => a - b);

  const complianceByRound = new Map(complianceChecks.map((c) => [c.round_number, c]));

  return (
    <div className="flex flex-col gap-6">
      {roundNumbers.map((round) => {
        const roundMessages = messages.filter((m) => m.round_number === round);
        const compliance = complianceByRound.get(round);

        return (
          <div key={round} className="flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold uppercase tracking-wide text-ink-muted">Round {round}</span>
              <div className="h-px flex-1 bg-hairline" />
            </div>

            <div className="flex flex-col gap-3">
              {roundMessages.map((message, i) => (
                <MessageBubble key={`${message.round_number}-${message.sender_role}-${i}`} message={message} />
              ))}
            </div>

            {compliance && <ComplianceCard assessment={compliance} />}
          </div>
        );
      })}
    </div>
  );
}
