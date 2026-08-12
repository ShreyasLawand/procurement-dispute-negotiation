// Runtime validation for public/data/manifest.json — cheap insurance against
// a stale or partially-written sync (e.g. an interrupted `npm run sync-data`).

import { z } from 'zod';
import type { Manifest } from '../types/negotiation';

const BatchMetricsSchema = z.object({
  agreement_rate: z.number().nullable(),
  deadlock_rate: z.number().nullable(),
  manifest_error_detection_rate: z.number().nullable(),
  average_rounds_to_conclusion: z.number(),
  average_duration_seconds: z.number(),
  outcome_distribution: z.record(z.string(), z.number()),
});

const ManifestCaseEntrySchema = z.object({
  id: z.string(),
  source: z.literal('root'),
  file: z.string(),
  scenarioId: z.string(),
  title: z.string(),
  timestamp: z.string(),
  timestampSource: z.literal('file-mtime'),
  resolved: z.boolean(),
  outcome: z.string().nullable(),
  roundsTaken: z.number(),
  maxRounds: z.number(),
  isRealCase: z.boolean(),
});

const ManifestBatchRunSchema = z.object({
  runNumber: z.number(),
  resolved: z.boolean().nullable(),
  outcome: z.string().nullable(),
  roundsTaken: z.number().nullable(),
  manifestErrorFoundAnyRound: z.boolean().nullable(),
  hasTranscript: z.boolean(),
  file: z.string().nullable(),
  error: z.string().nullable(),
});

const ManifestBatchEntrySchema = z.object({
  id: z.string(),
  dir: z.string(),
  scenarioId: z.string(),
  scenarioTitle: z.string(),
  timestamp: z.string(),
  timestampIso: z.string(),
  nRunsRequested: z.number(),
  nRunsSuccessful: z.number(),
  nRunsFailed: z.number(),
  maxRounds: z.number(),
  metrics: BatchMetricsSchema,
  runs: z.array(ManifestBatchRunSchema),
});

export const ManifestSchema = z.object({
  generatedAt: z.string(),
  cases: z.array(ManifestCaseEntrySchema),
  batches: z.array(ManifestBatchEntrySchema),
});

// See lib/schema.ts for why this uses a constrained generic rather than `satisfies`.
export type AssertAssignable<Expected, Actual extends Expected> = Actual;
export type _CheckManifest = AssertAssignable<Manifest, z.infer<typeof ManifestSchema>>;
