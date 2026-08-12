import { roleLabel, roleSlug } from '../../lib/format';
import type { PreNegotiationStatement } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { Chip } from '../ui/Chip';
import { ConfidenceMeter } from '../ui/ConfidenceMeter';

const BORDER_CLASSES = {
  ca: 'border-t-4 border-t-ca',
  bidder: 'border-t-4 border-t-bidder',
  court: 'border-t-4 border-t-court',
} as const;

export function PreNegotiationCard({ statement }: { statement: PreNegotiationStatement }) {
  const slug = roleSlug(statement.role);

  return (
    <Card className={`flex flex-col gap-4 ${BORDER_CLASSES[slug]}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-ink">{roleLabel(statement.role)}</h3>
        <ConfidenceMeter value={statement.confidence_score} tone={slug} className="w-28" />
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Opening position</p>
        <p className="mt-1 text-sm leading-relaxed text-ink-secondary">{statement.opening_position}</p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">BATNA</p>
        <p className="mt-1 text-sm leading-relaxed text-ink-secondary">{statement.batna}</p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Interests</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {statement.interests.map((interest) => (
            <Chip key={interest} tone={slug}>
              {interest}
            </Chip>
          ))}
        </div>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Legal basis</p>
        <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-sm text-ink-secondary">
          {statement.legal_basis.map((basis) => (
            <li key={basis}>{basis}</li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
