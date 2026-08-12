import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { CHART_CHROME, METRIC_COLORS } from '../../lib/chartTheme';
import { fmtPct } from '../../lib/format';
import { Card } from '../ui/Card';

export interface RateBarChartRow {
  label: string;
  agreement: number | null;
  deadlock: number | null;
  detection: number | null;
}

// Nominal comparison of three named metrics across batches — bar height
// already shows magnitude, so color encodes "which metric" (categorical
// identity, slots 1/2/3), not good/bad state.
export function RateBarChart({ data }: { data: RateBarChartRow[] }) {
  return (
    <Card>
      <h3 className="text-sm font-semibold text-ink">Rate comparison</h3>
      <div className="mt-4 h-72 w-full">
        <ResponsiveContainer>
          <BarChart data={data} barGap={4} margin={{ top: 8, right: 8, left: -8, bottom: 8 }}>
            <CartesianGrid stroke={CHART_CHROME.hairline} vertical={false} />
            <XAxis dataKey="label" tick={{ fill: CHART_CHROME.inkMuted, fontSize: 12 }} axisLine={{ stroke: CHART_CHROME.baseline }} tickLine={false} />
            <YAxis
              tickFormatter={(v: number) => fmtPct(v)}
              tick={{ fill: CHART_CHROME.inkMuted, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={48}
            />
            <Tooltip
              formatter={(value, name) => [fmtPct(Number(value)), String(name)]}
              contentStyle={{
                background: CHART_CHROME.surface,
                border: `1px solid ${CHART_CHROME.hairline}`,
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: CHART_CHROME.inkSecondary }} />
            <Bar dataKey="agreement" name="Agreement rate" fill={METRIC_COLORS.agreementRate} radius={[4, 4, 0, 0]} />
            <Bar dataKey="deadlock" name="Deadlock rate" fill={METRIC_COLORS.deadlockRate} radius={[4, 4, 0, 0]} />
            <Bar
              dataKey="detection"
              name="Manifest-error detection rate"
              fill={METRIC_COLORS.manifestErrorDetectionRate}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
