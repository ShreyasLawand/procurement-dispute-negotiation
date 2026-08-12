import { Scale } from 'lucide-react';
import type { ComplianceAssessment } from '../../types/negotiation';
import { Card } from '../ui/Card';
import { Chip } from '../ui/Chip';
import { Stamp } from '../ui/Stamp';

// The Court agent assesses process compliance only — never who "deserves" to
// win. Copy here stays neutral by design: "process followed" / "manifest
// error found or not", never "Court sided with X".
export function ComplianceCard({ assessment }: { assessment: ComplianceAssessment }) {
  return (
    <Card className="border-l-4 border-l-court bg-court-soft/30">
      <div className="flex items-center gap-2">
        <Scale className="h-4 w-4 text-court" />
        <h4 className="text-sm font-semibold text-ink">Court compliance review — round {assessment.round_number}</h4>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <Stamp
          tone={assessment.process_followed ? 'good' : 'critical'}
          label={assessment.process_followed ? 'Process followed' : 'Process not followed'}
        />
        <Stamp
          tone={assessment.manifest_error_found ? 'critical' : 'good'}
          label={assessment.manifest_error_found ? 'Manifest error found' : 'No manifest error found'}
        />
        {assessment.deadlock && <Stamp tone="warning" label="Deadlock" />}
      </div>

      <p className="mt-3 text-sm leading-relaxed text-ink-secondary">{assessment.reasoning}</p>

      {assessment.applicable_provisions.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {assessment.applicable_provisions.map((provision) => (
            <Chip key={provision} tone="court">
              {provision}
            </Chip>
          ))}
        </div>
      )}

      <div className="mt-3 flex items-center gap-2 border-t border-hairline pt-3">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-muted">Recommended action</span>
        <Chip tone="court" className="capitalize">
          {assessment.recommended_action}
        </Chip>
      </div>
    </Card>
  );
}
