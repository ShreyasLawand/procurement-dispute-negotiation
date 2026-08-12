import { Minus, TrendingDown, TrendingUp } from 'lucide-react';
import { cn } from '../../lib/cn';
import { Card } from '../ui/Card';

interface KpiCardProps {
  label: string;
  value: string;
  /** Percentage-point-style delta vs. a baseline batch, already formatted. */
  delta?: { text: string; direction: 'up' | 'down' | 'flat'; goodDirection: 'up' | 'down' } | null;
}

export function KpiCard({ label, value, delta }: KpiCardProps) {
  const isGood = delta && delta.direction !== 'flat' && delta.direction === delta.goodDirection;
  const isBad = delta && delta.direction !== 'flat' && delta.direction !== delta.goodDirection;
  const DeltaIcon = delta?.direction === 'up' ? TrendingUp : delta?.direction === 'down' ? TrendingDown : Minus;

  return (
    <Card className="flex flex-col gap-1.5" padded>
      <span className="text-xs font-medium uppercase tracking-wide text-ink-muted">{label}</span>
      <span className="tabular-nums text-2xl font-semibold text-ink">{value}</span>
      {delta && (
        <span
          className={cn(
            'flex items-center gap-1 text-xs font-medium',
            isGood && 'text-good-text',
            isBad && 'text-critical',
            !isGood && !isBad && 'text-ink-muted'
          )}
        >
          <DeltaIcon className="h-3.5 w-3.5" />
          {delta.text} vs. baseline
        </span>
      )}
    </Card>
  );
}
