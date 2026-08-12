import { Play } from 'lucide-react';
import { fmtGBP } from '../../lib/format';
import type { DisputeScenario } from '../../types/negotiation';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Chip } from '../ui/Chip';

interface ScenarioPreviewCardProps {
  scenario: DisputeScenario;
  maxRounds: number;
  onMaxRoundsChange: (rounds: number) => void;
  onStart: () => void;
  starting?: boolean;
}

const ROUND_OPTIONS = [3, 5];

export function ScenarioPreviewCard({
  scenario,
  maxRounds,
  onMaxRoundsChange,
  onStart,
  starting = false,
}: ScenarioPreviewCardProps) {
  return (
    <Card className="flex flex-col gap-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Extracted scenario</p>
        <h2 className="mt-1 text-lg font-semibold text-ink">{scenario.title}</h2>
      </div>

      <p className="whitespace-pre-line text-sm leading-relaxed text-ink-secondary">{scenario.description}</p>

      <div className="flex flex-wrap gap-2">
        <Chip>{scenario.dispute_type.replace(/_/g, ' ')}</Chip>
        <Chip>{scenario.procedural_stage.replace(/_/g, ' ')}</Chip>
        <Chip>{fmtGBP(scenario.contract_value_gbp)} contract</Chip>
      </div>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-1 border-t border-hairline pt-4 text-sm text-ink-secondary">
        <span>
          <span className="font-medium text-ink">Contracting Authority:</span> {scenario.contracting_authority_name}
        </span>
        <span>
          <span className="font-medium text-ink">Bidder:</span> {scenario.bidder_name}
        </span>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 border-t border-hairline pt-4">
        <label className="flex items-center gap-2 text-sm text-ink-secondary">
          Rounds
          <select
            value={maxRounds}
            onChange={(e) => onMaxRoundsChange(Number(e.target.value))}
            disabled={starting}
            className="rounded-md border border-hairline bg-surface px-2 py-1 text-sm text-ink"
          >
            {ROUND_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>
        <Button onClick={onStart} disabled={starting}>
          <Play className="h-4 w-4" />
          {starting ? 'Starting…' : 'Start negotiation'}
        </Button>
      </div>
    </Card>
  );
}
