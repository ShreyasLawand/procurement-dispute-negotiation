import { CheckCircle2, TriangleAlert } from 'lucide-react';
import { shortOutcome } from '../../lib/format';
import { cn } from '../../lib/cn';

interface OutcomeRibbonProps {
  resolved: boolean;
  outcome: string | null;
}

export function OutcomeRibbon({ resolved, outcome }: OutcomeRibbonProps) {
  const Icon = resolved ? CheckCircle2 : TriangleAlert;
  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-xl border px-5 py-4',
        resolved ? 'border-good/20 bg-good-soft' : 'border-warning/30 bg-warning-soft'
      )}
    >
      <Icon className={cn('h-5 w-5 shrink-0', resolved ? 'text-good' : 'text-warning')} />
      <div>
        <p className={cn('font-semibold', resolved ? 'text-good' : 'text-warning')}>
          {resolved ? 'Resolved' : 'Deadlock'}
        </p>
        <p className="text-sm text-ink-secondary">{shortOutcome(outcome)}</p>
      </div>
    </div>
  );
}
