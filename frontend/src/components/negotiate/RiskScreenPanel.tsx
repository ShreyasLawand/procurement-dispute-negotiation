import { ShieldAlert } from 'lucide-react';
import { useState } from 'react';
import { API_BASE } from '../../lib/api-config';
import type { BidderProfileInput, CAProfileInput, ChallengeRiskAssessment } from '../../types/negotiation';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { ErrorState } from '../ui/ErrorState';
import { Stamp, type StampTone } from '../ui/Stamp';

// Deliberately a curated subset of CAProfile/BidderProfile (see
// src/risk/challenge_risk.py) — the highest-severity, CA-verifiable factors,
// not the full 16-field taxonomy the CLI exposes. This runs BEFORE a dispute
// exists, on facts the authority can actually check before the standstill
// letter goes out.
const BAND_TONE: Record<ChallengeRiskAssessment['overall_risk_band'], StampTone> = {
  low: 'good',
  medium: 'warning',
  high: 'critical',
};

const SEVERITY_TONE: Record<'low' | 'medium' | 'high', StampTone> = {
  low: 'neutral',
  medium: 'warning',
  high: 'critical',
};

function FieldSelect<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T | undefined;
  options: { value: T; label: string }[];
  onChange: (v: T | undefined) => void;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-ink">{label}</span>
      <select
        value={value ?? ''}
        onChange={(e) => onChange((e.target.value || undefined) as T | undefined)}
        className="rounded-md border border-hairline bg-surface px-2 py-1.5 text-sm text-ink"
      >
        <option value="">Not screened for</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function RiskScreenPanel() {
  const [ca, setCa] = useState<CAProfileInput>({});
  const [bidder, setBidder] = useState<BidderProfileInput>({});
  const [result, setResult] = useState<ChallengeRiskAssessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function runScreen() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/risk-assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ca_profile: ca, bidder_profile: bidder }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? `Risk screen failed (${res.status})`);
      }
      const data = (await res.json()) as { assessment: ChallengeRiskAssessment };
      setResult(data.assessment);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 text-ink-secondary" />
        <div>
          <h3 className="text-sm font-semibold text-ink">Pre-award challenge risk screen</h3>
          <p className="text-xs text-ink-muted">
            Run this BEFORE the standstill letter goes out — fill in what you actually know about this
            procurement. An unset field is "not screened for", not "low risk".
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FieldSelect
          label="Evaluation record documentation"
          value={ca.documentation_quality}
          options={[
            { value: 'robust', label: 'Robust — complete audit trail' },
            { value: 'partial', label: 'Partial — some gaps' },
            { value: 'weak', label: 'Weak — incomplete / inconsistent' },
          ]}
          onChange={(v) => setCa((s) => ({ ...s, documentation_quality: v }))}
        />
        <FieldSelect
          label="Evaluation panel"
          value={ca.panel_capability}
          options={[
            { value: 'procurement_trained', label: 'Procurement-trained' },
            { value: 'mixed', label: 'Mixed familiarity' },
            { value: 'technical_untrained', label: 'Technical, untrained in procurement' },
          ]}
          onChange={(v) => setCa((s) => ({ ...s, panel_capability: v }))}
        />
        <FieldSelect
          label="Internal accountability exposure"
          value={ca.internal_accountability_exposure}
          options={[
            { value: 'low', label: 'Low' },
            { value: 'medium', label: 'Medium' },
            { value: 'high', label: 'High — individuals personally exposed' },
          ]}
          onChange={(v) => setCa((s) => ({ ...s, internal_accountability_exposure: v }))}
        />
        <FieldSelect
          label="Score margin to the losing bidder"
          value={bidder.score_margin}
          options={[
            { value: 'wide', label: 'Wide' },
            { value: 'moderate', label: 'Moderate' },
            { value: 'narrow', label: 'Narrow' },
          ]}
          onChange={(v) => setBidder((s) => ({ ...s, score_margin: v }))}
        />
        <FieldSelect
          label="Debrief you are about to send"
          value={bidder.feedback_quality_received}
          options={[
            { value: 'detailed', label: 'Detailed' },
            { value: 'adequate', label: 'Adequate' },
            { value: 'minimal', label: 'Minimal / vague' },
          ]}
          onChange={(v) => setBidder((s) => ({ ...s, feedback_quality_received: v }))}
        />
        <label className="flex items-center gap-2 pt-6 text-sm text-ink">
          <input
            type="checkbox"
            checked={bidder.incumbent ?? false}
            onChange={(e) => setBidder((s) => ({ ...s, incumbent: e.target.checked || undefined }))}
            className="h-4 w-4 rounded border-hairline"
          />
          Losing bidder is the incumbent
        </label>
      </div>

      <div className="flex justify-end">
        <Button onClick={runScreen} disabled={loading}>
          {loading ? 'Screening…' : 'Screen for challenge risk'}
        </Button>
      </div>

      {error !== null && <ErrorState title="Could not run the risk screen" error={error} />}

      {result && (
        <div className="flex flex-col gap-3 border-t border-hairline pt-4">
          <div className="flex items-center gap-3">
            <Stamp tone={BAND_TONE[result.overall_risk_band]} label={`${result.overall_risk_band.toUpperCase()} risk`} />
            <span className="text-xs text-ink-muted">score {result.risk_score.toFixed(2)}</span>
          </div>
          <p className="text-sm text-ink-secondary">{result.summary}</p>

          {result.flags.length > 0 && (
            <div className="flex flex-col gap-2">
              {[...result.flags]
                .sort((a, b) => ({ high: 3, medium: 2, low: 1 })[b.severity] - ({ high: 3, medium: 2, low: 1 })[a.severity])
                .map((f, i) => (
                  <div key={i} className="rounded-md border border-hairline bg-page p-3 text-sm">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <Stamp tone={SEVERITY_TONE[f.severity]} label={f.severity} />
                      <span className="text-xs text-ink-muted">
                        {f.confidence === 'known' ? 'CA-verifiable' : 'estimated'}
                      </span>
                      <span className="font-medium text-ink">{f.category}</span>
                    </div>
                    <p className="text-ink-secondary">{f.rationale}</p>
                    <p className="mt-1 text-ink-secondary">
                      <span className="font-medium text-ink">Mitigate: </span>
                      {f.mitigation}
                    </p>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
