import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/cn';
import type { RoleSlug } from '../../lib/format';

interface ChipProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: RoleSlug | 'neutral';
}

const TONE_CLASSES: Record<NonNullable<ChipProps['tone']>, string> = {
  ca: 'bg-ca-soft text-ca border-ca/20',
  bidder: 'bg-bidder-soft text-bidder border-bidder/20',
  court: 'bg-court-soft text-court border-court/20',
  neutral: 'bg-page text-ink-secondary border-hairline',
};

export function Chip({ className, tone = 'neutral', ...props }: ChipProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium leading-none',
        TONE_CLASSES[tone],
        className
      )}
      {...props}
    />
  );
}
