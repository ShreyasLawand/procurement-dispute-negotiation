import type { AgentRole } from '../types/negotiation';

const gbpFormatter = new Intl.NumberFormat('en-GB', {
  style: 'currency',
  currency: 'GBP',
  maximumFractionDigits: 0,
});

export function fmtGBP(value: number): string {
  return gbpFormatter.format(value);
}

export function fmtPct(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return `${(value * 100).toFixed(digits)}%`;
}

export function fmtDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

export function fmtDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) return '—';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}m ${secs}s`;
}

const ROLE_LABELS: Record<AgentRole, string> = {
  contracting_authority: 'Contracting Authority',
  aggrieved_bidder: 'Aggrieved Bidder',
  court: 'Court',
};

export function roleLabel(role: AgentRole): string {
  return ROLE_LABELS[role] ?? role;
}

export type RoleSlug = 'ca' | 'bidder' | 'court';

const ROLE_SLUGS: Record<AgentRole, RoleSlug> = {
  contracting_authority: 'ca',
  aggrieved_bidder: 'bidder',
  court: 'court',
};

export function roleSlug(role: AgentRole): RoleSlug {
  return ROLE_SLUGS[role] ?? 'court';
}

// Known recommended_action / resolution_outcome values get a short, stable
// label. Anything unrecognized falls back to a truncated version of the raw
// string rather than guessing — these are free-text LLM outputs.
const SHORT_OUTCOME_MAP: Record<string, string> = {
  'continue negotiation': 'Continuing',
  're-evaluation': 'Re-evaluation ordered',
  'no remedy - decision stands': 'No remedy — decision stands',
  damages: 'Damages awarded',
};

export function shortOutcome(outcome: string | null | undefined): string {
  if (!outcome) return '—';
  const lower = outcome.trim().toLowerCase();
  if (lower.startsWith('deadlock')) return 'Deadlock';
  if (SHORT_OUTCOME_MAP[lower]) return SHORT_OUTCOME_MAP[lower];
  return outcome.length > 40 ? `${outcome.slice(0, 40)}…` : outcome;
}
