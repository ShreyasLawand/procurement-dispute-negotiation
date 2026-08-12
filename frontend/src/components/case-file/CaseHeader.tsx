import { Building2, Landmark } from 'lucide-react';
import { fmtGBP } from '../../lib/format';
import type { DisputeScenario } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { Chip } from '../ui/Chip';

interface CaseHeaderProps {
  scenario: DisputeScenario;
  roundNumber: number;
  maxRounds: number;
}

export function CaseHeader({ scenario, roundNumber, maxRounds }: CaseHeaderProps) {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-md bg-page px-2 py-1 text-xs font-semibold text-ink-secondary">
          {scenario.dispute_id}
        </span>
        <Chip>{scenario.dispute_type.replace(/_/g, ' ')}</Chip>
        <Chip>{scenario.procedural_stage.replace(/_/g, ' ')}</Chip>
        <span className="ml-auto text-xs text-ink-muted">
          Round {roundNumber} of {maxRounds}
        </span>
      </div>

      <div>
        <h1 className="text-xl font-semibold leading-snug text-ink">{scenario.title}</h1>
        <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-secondary">
          {scenario.description}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-hairline pt-4 text-sm">
        <span className="flex items-center gap-1.5 text-ink-secondary">
          <Landmark className="h-4 w-4 text-ca" />
          {scenario.contracting_authority_name}
        </span>
        <span className="flex items-center gap-1.5 text-ink-secondary">
          <Building2 className="h-4 w-4 text-bidder" />
          {scenario.bidder_name}
        </span>
        <span className="ml-auto font-semibold tabular-nums text-ink">
          {fmtGBP(scenario.contract_value_gbp)} contract
        </span>
      </div>
    </Card>
  );
}
