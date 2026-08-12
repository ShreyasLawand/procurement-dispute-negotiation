import { AlertOctagon, AlertTriangle, CheckCircle2, Circle, XCircle } from 'lucide-react';
import type { ComponentType } from 'react';
import { cn } from '../../lib/cn';

export type StampTone = 'good' | 'warning' | 'serious' | 'critical' | 'neutral';

interface StampProps {
  tone: StampTone;
  label: string;
  className?: string;
}

const TONE_CONFIG: Record<StampTone, { icon: ComponentType<{ className?: string }>; classes: string }> = {
  good: { icon: CheckCircle2, classes: 'bg-good-soft text-good border-good/20' },
  warning: { icon: AlertTriangle, classes: 'bg-warning-soft text-warning border-warning/30' },
  serious: { icon: AlertOctagon, classes: 'bg-serious-soft text-serious border-serious/20' },
  critical: { icon: XCircle, classes: 'bg-critical-soft text-critical border-critical/20' },
  neutral: { icon: Circle, classes: 'bg-page text-ink-secondary border-hairline' },
};

// Status meaning is always carried by icon + label together, never by the
// background color alone (dataviz skill: warning/serious sit below 3:1
// contrast on the light surface by design — the icon+label pairing is the
// required mitigation).
export function Stamp({ tone, label, className }: StampProps) {
  const { icon: Icon, classes } = TONE_CONFIG[tone];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold leading-none',
        classes,
        className
      )}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {label}
    </span>
  );
}
