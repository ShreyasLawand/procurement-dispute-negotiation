import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { CHART_CHROME, outcomeColor } from '../../lib/chartTheme';
import { shortOutcome } from '../../lib/format';
import { Card } from '../ui/Card';

export interface OutcomeDistributionRow {
  label: string;
  distribution: Record<string, number>;
}

// Outcome -> color is assigned by outcomeColor() keyed on the outcome name
// itself, so the same outcome is always the same color across every batch
// and chart, regardless of which batches are currently selected.
export function OutcomeDistributionChart({ data }: { data: OutcomeDistributionRow[] }) {
  const outcomeKeys = Array.from(new Set(data.flatMap((row) => Object.keys(row.distribution))));

  const chartData = data.map((row) => ({ label: row.label, ...row.distribution }));

  return (
    <Card>
      <h3 className="text-sm font-semibold text-ink">Outcome distribution</h3>
      <div className="mt-4 h-72 w-full">
        <ResponsiveContainer>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -8, bottom: 8 }}>
            <CartesianGrid stroke={CHART_CHROME.hairline} vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: CHART_CHROME.inkMuted, fontSize: 12 }}
              axisLine={{ stroke: CHART_CHROME.baseline }}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: CHART_CHROME.inkMuted, fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={32}
            />
            <Tooltip
              formatter={(value, name) => [String(value), shortOutcome(String(name))]}
              contentStyle={{
                background: CHART_CHROME.surface,
                border: `1px solid ${CHART_CHROME.hairline}`,
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend
              formatter={(value: string) => shortOutcome(value)}
              wrapperStyle={{ fontSize: 12, color: CHART_CHROME.inkSecondary }}
            />
            {outcomeKeys.map((key) => (
              <Bar key={key} dataKey={key} name={key} stackId="a" fill={outcomeColor(key)} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
