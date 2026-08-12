import { fmtDuration } from '../../lib/format';
import { Card } from '../ui/Card';

export interface RoundsDurationRow {
  id: string;
  label: string;
  avgRounds: number;
  avgDurationSeconds: number;
}

// Two separate stat columns rather than one dual-axis chart — rounds and
// seconds are different scales/units and shouldn't share an axis.
export function RoundsDurationTiles({ rows }: { rows: RoundsDurationRow[] }) {
  return (
    <Card padded={false}>
      <div className="border-b border-hairline px-5 py-4">
        <h3 className="text-sm font-semibold text-ink">Rounds &amp; duration to conclusion</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs font-medium uppercase tracking-wide text-ink-muted">
            <th className="px-5 py-2 font-medium">Batch</th>
            <th className="px-5 py-2 text-right font-medium">Avg. rounds</th>
            <th className="px-5 py-2 text-right font-medium">Avg. duration</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="border-t border-hairline">
              <td className="px-5 py-2.5 text-ink">{row.label}</td>
              <td className="px-5 py-2.5 text-right tabular-nums text-ink">{row.avgRounds.toFixed(1)}</td>
              <td className="px-5 py-2.5 text-right tabular-nums text-ink">{fmtDuration(row.avgDurationSeconds)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
