import { Handshake } from 'lucide-react';
import { roleLabel, roleSlug } from '../../lib/format';
import type { NegotiationMessage } from '../../types/negotiation';
import { cn } from '../../lib/cn';

const SIDE_CLASSES = {
  ca: 'items-start',
  bidder: 'items-end',
  court: 'items-center',
} as const;

const BUBBLE_CLASSES = {
  ca: 'bg-ca-soft border-l-4 border-l-ca',
  bidder: 'bg-bidder-soft border-r-4 border-r-bidder',
  court: 'bg-court-soft border-l-4 border-l-court',
} as const;

export function MessageBubble({ message }: { message: NegotiationMessage }) {
  const slug = roleSlug(message.sender_role);
  const hasCallout = message.proposal || message.concession_made;

  return (
    <div className={cn('flex flex-col gap-1', SIDE_CLASSES[slug])}>
      <span className="px-1 text-xs font-medium text-ink-muted">{roleLabel(message.sender_role)}</span>
      <div className={cn('max-w-2xl rounded-lg px-4 py-3 text-sm leading-relaxed text-ink', BUBBLE_CLASSES[slug])}>
        <p>{message.message}</p>
        {hasCallout && (
          <div className="mt-2.5 space-y-1.5 border-t border-ink/10 pt-2.5">
            {message.proposal && (
              <p className="flex items-start gap-1.5 text-sm font-medium text-ink">
                <Handshake className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <span>{message.proposal}</span>
              </p>
            )}
            {message.concession_made && (
              <p className="text-xs italic text-ink-secondary">Concession: {message.concession_made}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
