import { CheckCircle2, Loader2 } from 'lucide-react';
import type { ConnectionStatus } from '../../lib/useLiveNegotiation';
import { ErrorState } from '../ui/ErrorState';

interface LiveStatusBarProps {
  connectionStatus: ConnectionStatus;
  statusMessage: string | null;
  isDone: boolean;
  error: string | null;
}

export function LiveStatusBar({ connectionStatus, statusMessage, isDone, error }: LiveStatusBarProps) {
  if (error) {
    return <ErrorState title="The negotiation stream failed" error={error} />;
  }

  if (isDone) {
    return (
      <div className="flex items-center gap-2.5 rounded-xl border border-good/20 bg-good-soft px-5 py-4">
        <CheckCircle2 className="h-5 w-5 shrink-0 text-good" />
        <p className="font-semibold text-good">Negotiation complete</p>
      </div>
    );
  }

  const label =
    statusMessage ?? (connectionStatus === 'connecting' ? 'Connecting to the negotiation…' : 'Working…');

  return (
    <div className="flex items-center gap-2.5 rounded-xl border border-brand/20 bg-brand-soft px-5 py-4">
      <Loader2 className="h-5 w-5 shrink-0 animate-spin text-brand-dark" />
      <p className="text-sm font-medium text-brand-dark">{label}</p>
    </div>
  );
}
