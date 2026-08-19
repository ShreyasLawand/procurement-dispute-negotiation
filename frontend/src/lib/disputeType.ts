import type { DisputeScenario } from '../types/negotiation';

// Mirrors src/utils/negotiation_helpers.py::is_disclosure_dispute() exactly — keep these
// two in sync if the keyword list ever changes there. Frontend-only use: choosing which
// labels ComplianceCard shows (manifest-error framing doesn't apply to a disclosure
// application). Does not drive any negotiation logic — the backend's Court agent already
// made this same classification when it picked which system prompt to run.
const DISCLOSURE_KEYWORDS = ['disclosure', 'interim_application', 'interim application'];

export function isDisclosureDispute(scenario: Pick<DisputeScenario, 'procedural_stage' | 'dispute_type'>): boolean {
  const haystack = `${scenario.procedural_stage} ${scenario.dispute_type}`.toLowerCase();
  return DISCLOSURE_KEYWORDS.some((kw) => haystack.includes(kw));
}
