// Runtime validation for negotiation logs / batch summaries loaded from
// public/data/ or dropped in via the upload fallback. These are outputs of an
// LLM pipeline, so malformed shape is a real possibility — validate before
// rendering rather than letting a bad field crash a component tree.

import { z } from 'zod';
import type { BatchSummary, NegotiationState } from '../types/negotiation';

const AgentRoleSchema = z.enum(['contracting_authority', 'aggrieved_bidder', 'court']);

const DisputeScenarioSchema = z.object({
  dispute_id: z.string(),
  title: z.string(),
  description: z.string(),
  contract_value_gbp: z.number(),
  dispute_type: z.string(),
  procedural_stage: z.string(),
  contracting_authority_name: z.string(),
  bidder_name: z.string(),
});

const PreNegotiationStatementSchema = z.object({
  role: AgentRoleSchema,
  interests: z.array(z.string()),
  goals: z.array(z.string()),
  batna: z.string(),
  opening_position: z.string(),
  legal_basis: z.array(z.string()),
  confidence_score: z.number().min(0).max(1),
});

const NegotiationMessageSchema = z.object({
  round_number: z.number().int(),
  sender_role: AgentRoleSchema,
  message: z.string(),
  proposal: z.string().nullable(),
  concession_made: z.string().nullable(),
});

const ComplianceAssessmentSchema = z.object({
  round_number: z.number().int(),
  process_followed: z.boolean(),
  manifest_error_found: z.boolean(),
  applicable_provisions: z.array(z.string()),
  reasoning: z.string(),
  recommended_action: z.string(), // free string — LLM output varies, not a strict enum
  deadlock: z.boolean(),
});

const WinStatementSchema = z.object({
  role: AgentRoleSchema,
  outcome_relative_to_batna: z.string(),
  win_statement: z.string(),
  what_was_achieved: z.array(z.string()),
  what_was_conceded: z.array(z.string()),
});

const NegotiationSummarySchema = z.object({
  key_sticking_points: z.array(z.string()),
  concessions_summary: z.string(),
  court_reasoning_summary: z.string(),
  likely_next_steps: z.string(),
  plain_english_summary: z.string(),
});

export const NegotiationStateSchema = z.object({
  scenario: DisputeScenarioSchema,
  round_number: z.number().int(),
  max_rounds: z.number().int(),
  ca_pre_negotiation: PreNegotiationStatementSchema.nullable(),
  bidder_pre_negotiation: PreNegotiationStatementSchema.nullable(),
  messages: z.array(NegotiationMessageSchema),
  compliance_checks: z.array(ComplianceAssessmentSchema),
  resolved: z.boolean(),
  resolution_outcome: z.string().nullable(),
  adjudicated: z.boolean(),
  ca_win_statement: WinStatementSchema.nullable(),
  bidder_win_statement: WinStatementSchema.nullable(),
  summary: NegotiationSummarySchema.nullable(),
});

const BatchIndividualRunSchema = z.object({
  run_number: z.number().int(),
  resolved: z.boolean().nullable(),
  outcome: z.string().nullable(),
  rounds_taken: z.number().int().nullable(),
  manifest_error_found_any_round: z.boolean().nullable(),
  manifest_error_rounds: z.array(z.number().int()),
  process_not_followed_any_round: z.boolean().nullable(),
  duration_seconds: z.number(),
  error: z.string().nullable(),
});

// `resolution_rate` was named `agreement_rate` until Aug 2026 — the old name measured
// "resolved without deadlock" but read as if it meant the parties agreed with each
// other. Batches generated before the rename still have the old key on disk, and a
// user can drop one of those files in via the upload fallback directly (bypassing
// sync-data.mjs, which normalizes this for the manifest path), so this preprocess
// step maps the legacy key across before validation rather than rejecting old files.
const BatchMetricsSchema = z.preprocess(
  (raw) => {
    if (raw && typeof raw === 'object' && !('resolution_rate' in raw) && 'agreement_rate' in raw) {
      const { agreement_rate, ...rest } = raw as Record<string, unknown>;
      return { ...rest, resolution_rate: agreement_rate };
    }
    return raw;
  },
  z.object({
    resolution_rate: z.number().nullable(),
    deadlock_rate: z.number().nullable(),
    manifest_error_detection_rate: z.number().nullable(),
    average_rounds_to_conclusion: z.number(),
    average_duration_seconds: z.number(),
    outcome_distribution: z.record(z.string(), z.number()),
  }),
);

export const BatchSummarySchema = z.object({
  scenario_id: z.string(),
  scenario_title: z.string(),
  n_runs_requested: z.number().int(),
  n_runs_successful: z.number().int(),
  n_runs_failed: z.number().int(),
  max_rounds: z.number().int(),
  timestamp: z.string(),
  metrics: BatchMetricsSchema,
  individual_runs: z.array(BatchIndividualRunSchema),
});

// Compile-time drift guard: if types/negotiation.ts and these schemas
// diverge (the zod-inferred shape stops being assignable to the hand-written
// interface), this fails to typecheck (caught by `npm run build`, not just
// at runtime). `satisfies` only applies to value expressions, not type
// aliases, so the check is expressed as a constrained generic instead.
export type AssertAssignable<Expected, Actual extends Expected> = Actual;
export type _CheckState = AssertAssignable<NegotiationState, z.infer<typeof NegotiationStateSchema>>;
export type _CheckBatch = AssertAssignable<BatchSummary, z.infer<typeof BatchSummarySchema>>;

export type ValidatedDoc =
  | { kind: 'case'; data: NegotiationState }
  | { kind: 'batch'; data: BatchSummary };

/** Tries NegotiationState first, then BatchSummary. Throws with both zod error
 * trees attached if neither shape matches, so callers can render real
 * validation issues instead of a generic "invalid file" message. */
export function parseUnknownDoc(json: unknown): ValidatedDoc {
  const asCase = NegotiationStateSchema.safeParse(json);
  if (asCase.success) {
    return { kind: 'case', data: asCase.data };
  }
  const asBatch = BatchSummarySchema.safeParse(json);
  if (asBatch.success) {
    return { kind: 'batch', data: asBatch.data };
  }
  throw new AggregateError(
    [asCase.error, asBatch.error],
    'JSON did not match either a negotiation case (NegotiationState) or a batch summary (BatchSummary).'
  );
}
