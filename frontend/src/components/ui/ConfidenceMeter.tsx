import type { RoleSlug } from '../../lib/format';
import { cn } from '../../lib/cn';

interface ConfidenceMeterProps {
  value: number; // 0-1
  tone: RoleSlug;
  className?: string;
}

const FILL_CLASSES: Record<RoleSlug, string> = {
  ca: 'bg-ca',
  bidder: 'bg-bidder',
  court: 'bg-court',
};

export function ConfidenceMeter({ value, tone, className }: ConfidenceMeterProps) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-page" role="presentation">
        <div className={cn('h-full rounded-full', FILL_CLASSES[tone])} style={{ width: `${pct}%` }} />
      </div>
      <span className="tabular-nums text-xs font-medium text-ink-secondary">{pct}%</span>
    </div>
  );
}
