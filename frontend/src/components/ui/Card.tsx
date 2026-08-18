import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/cn';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padded?: boolean;
  /** Lifts and brightens the border on hover — for cards that are themselves a
   * click target (CaseCard, BatchCard), not for passive content containers. */
  hoverable?: boolean;
}

export function Card({ className, padded = true, hoverable = false, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-hairline bg-surface shadow-sm',
        padded && 'p-5',
        hoverable &&
          'transition-all duration-200 ease-out hover:-translate-y-1 hover:border-brand/30 hover:shadow-lg',
        className
      )}
      {...props}
    />
  );
}
