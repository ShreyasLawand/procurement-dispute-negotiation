import { CheckCircle2 } from 'lucide-react';
import type { ConnectionStatus } from '../../lib/useLiveNegotiation';
import { ErrorState } from '../ui/ErrorState';

interface LiveStatusBarProps {
  connectionStatus: ConnectionStatus;
  statusMessage: string | null;
  isDone: boolean;
  error: string | null;
}

function ThinkingDots() {
  return (
    <span className="flex items-end gap-1" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 animate-bounce-dot rounded-full bg-brand-dark"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </span>
  );
}

export function LiveStatusBar({ connectionStatus, statusMessage, isDone, error }: LiveStatusBarProps) {
  if (error) {
    return <ErrorState title="The negotiation stream failed" error={error} />;
  }

  if (isDone) {
    return (
      <div className="flex animate-scale-in items-center gap-2.5 rounded-xl border border-good/20 bg-good-soft px-5 py-4">
        <CheckCircle2 className="h-5 w-5 shrink-0 text-good" />
        <p className="font-semibold text-good">Negotiation complete</p>
      </div>
    );
  }

  const label =
    statusMessage ?? (connectionStatus === 'connecting' ? 'Connecting to the negotiation…' : 'Working…');

  return (
    <div className="animate-pulse-glow flex items-center gap-3 rounded-xl border border-brand/20 bg-brand-soft px-5 py-4 transition-all">
      <ThinkingDots />
      <p className="text-sm font-medium text-brand-dark">{label}</p>
    </div>
  );
}
