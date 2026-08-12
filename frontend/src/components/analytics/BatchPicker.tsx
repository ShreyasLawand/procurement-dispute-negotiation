import { fmtDate } from '../../lib/format';
import type { ManifestBatchEntry } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { cn } from '../../lib/cn';

const MAX_SELECTION = 4;

interface BatchPickerProps {
  batches: ManifestBatchEntry[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}

export function BatchPicker({ batches, selectedIds, onChange }: BatchPickerProps) {
  const byScenario = new Map<string, ManifestBatchEntry[]>();
  for (const batch of batches) {
    const list = byScenario.get(batch.scenarioId) ?? [];
    list.push(batch);
    byScenario.set(batch.scenarioId, list);
  }

  function toggle(id: string) {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id));
    } else if (selectedIds.length < MAX_SELECTION) {
      onChange([...selectedIds, id]);
    }
  }

  return (
    <Card>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink">Compare batches</h3>
        <span className="text-xs text-ink-muted">
          {selectedIds.length} / {MAX_SELECTION} selected
        </span>
      </div>

      <div className="mt-4 flex flex-col gap-4">
        {[...byScenario.entries()].map(([scenarioId, group]) => (
          <div key={scenarioId}>
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-ink-muted">{scenarioId}</p>
            <div className="flex flex-col gap-1">
              {group.map((batch) => {
                const checked = selectedIds.includes(batch.id);
                const disabled = !checked && selectedIds.length >= MAX_SELECTION;
                return (
                  <label
                    key={batch.id}
                    className={cn(
                      'flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 text-sm',
                      checked && 'bg-ca-soft',
                      disabled && 'cursor-not-allowed opacity-50'
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      disabled={disabled}
                      onChange={() => toggle(batch.id)}
                      className="h-4 w-4 accent-current text-ca"
                    />
                    <span className="min-w-0 flex-1 truncate text-ink">{batch.scenarioTitle}</span>
                    <span className="shrink-0 text-xs text-ink-muted">{fmtDate(batch.timestampIso)}</span>
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
