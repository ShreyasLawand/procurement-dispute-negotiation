import { roleLabel, roleSlug } from '../../lib/format';
import type { WinStatement } from '../../types/negotiation';
import { Card } from '../ui/Card';

const BORDER_CLASSES = {
  ca: 'border-t-4 border-t-ca',
  bidder: 'border-t-4 border-t-bidder',
  court: 'border-t-4 border-t-court',
} as const;

// Renders only when the caller has a non-null WinStatement — independent of
// `resolved`, since deadlocked negotiations still produce reflections.
export function WinStatementCard({ statement }: { statement: WinStatement }) {
  const slug = roleSlug(statement.role);

  return (
    <Card className={`flex flex-col gap-4 ${BORDER_CLASSES[slug]}`}>
      <div>
        <h3 className="font-semibold text-ink">{roleLabel(statement.role)}</h3>
        <p className="mt-1 text-sm font-medium text-ink-secondary">{statement.outcome_relative_to_batna}</p>
      </div>

      <p className="text-sm italic leading-relaxed text-ink-secondary">“{statement.win_statement}”</p>

      <div className="grid gap-4 border-t border-hairline pt-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Achieved</p>
          <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-sm text-ink-secondary">
            {statement.what_was_achieved.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Conceded</p>
          <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-sm text-ink-secondary">
            {statement.what_was_conceded.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}
