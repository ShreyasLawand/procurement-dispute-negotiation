// Raw hex mirror of src/index.css's @theme tokens, for Recharts fill/stroke
// props (which need literal color values, not Tailwind classes). Values come
// from the dataviz skill's validated default palette (references/palette.md),
// validated via validate_palette.js for CVD + normal-vision safety.

import type { AgentRole } from '../types/negotiation';
import { roleSlug } from './format';

// Categorical slots 1/2/3 — fixed order, assigned to the three negotiating
// roles. Passes all-pairs CVD (worst ΔE 9.2 deutan, 24.0 normal-vision).
export const ROLE_COLORS: Record<AgentRole, string> = {
  contracting_authority: '#2a78d6', // slot 1, blue
  aggrieved_bidder: '#eb6834', // slot 2, orange
  court: '#1baf7a', // slot 3, aqua — neutral arbiter, neither party's hue
};

export function roleColor(role: AgentRole): string {
  return ROLE_COLORS[role];
}

// Fixed status palette — reserved meaning, never reused for series identity.
export const STATUS_COLORS = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
} as const;

export const CHART_CHROME = {
  surface: '#fcfcfb',
  page: '#f9f9f7',
  ink: '#0b0b0b',
  inkSecondary: '#52514e',
  inkMuted: '#898781',
  hairline: '#e1e0d9',
  baseline: '#c3c2b7',
} as const;

// Categorical slots 1-4, used for the "which metric" comparison in
// RateBarChart (resolution / deadlock / manifest-error-detection rate) —
// nominal identity, not good/bad state, since the bar height already shows
// magnitude. Reused deliberately from the same slot order as ROLE_COLORS;
// the two never appear in the same chart.
export const METRIC_COLORS = {
  resolutionRate: '#2a78d6', // slot 1, blue
  deadlockRate: '#eb6834', // slot 2, orange
  manifestErrorDetectionRate: '#1baf7a', // slot 3, aqua
} as const;

// Outcome -> slot mapping is hardcoded by outcome name (not by appearance
// order) so the same outcome is always the same color across every batch
// and every chart — "color follows the entity, never its rank."
const OUTCOME_SLOT_ORDER = [
  '#2a78d6', // slot 1, blue
  '#eb6834', // slot 2, orange
  '#1baf7a', // slot 3, aqua
  '#eda100', // slot 4, yellow
  '#e87ba4', // slot 5, magenta
  '#008300', // slot 6, green
  '#4a3aa7', // slot 7, violet
  '#e34948', // slot 8, red
];

const KNOWN_OUTCOME_SLOTS: Record<string, number> = {
  're-evaluation': 0,
  'continue negotiation': 1,
  'no remedy - decision stands': 2,
  damages: 3,
  deadlock: 4, // matched via the startsWith('deadlock') normalization below
};

const fallbackOutcomeSlots = new Map<string, number>();
let nextFallbackSlot = 5;

/** Stable color per distinct outcome string. Known outcomes get a fixed
 * slot; anything unrecognized (including the free-text deadlock sentence)
 * is assigned the next unused slot the first time it's seen and reused
 * after that, so repeated renders stay consistent within a session. */
export function outcomeColor(outcome: string): string {
  const key = outcome.trim().toLowerCase();
  const normalizedKey = key.startsWith('deadlock') ? 'deadlock' : key;

  if (normalizedKey in KNOWN_OUTCOME_SLOTS) {
    return OUTCOME_SLOT_ORDER[KNOWN_OUTCOME_SLOTS[normalizedKey]];
  }
  if (!fallbackOutcomeSlots.has(normalizedKey)) {
    fallbackOutcomeSlots.set(normalizedKey, nextFallbackSlot % OUTCOME_SLOT_ORDER.length);
    nextFallbackSlot += 1;
  }
  return OUTCOME_SLOT_ORDER[fallbackOutcomeSlots.get(normalizedKey)!];
}

export { roleSlug };
