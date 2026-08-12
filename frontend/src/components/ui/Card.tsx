import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/cn';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padded?: boolean;
}

export function Card({ className, padded = true, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-hairline bg-surface shadow-sm',
        padded && 'p-5',
        className
      )}
      {...props}
    />
  );
}
