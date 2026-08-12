#!/usr/bin/env node
// Copies JSON output from the Python backend (root negotiation_log_*.json files
// and batch_results/) into frontend/public/data/, and writes a manifest.json
// describing what's available. Run manually via `npm run sync-data` whenever
// the backend has produced new logs/runs — not wired into `dev` automatically,
// so a stale sync during dev iteration is never silently masked.

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND_DIR = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(FRONTEND_DIR, '..'); // procurement-dispute-negotiation/
const BATCH_RESULTS_DIR = path.join(REPO_ROOT, 'batch_results');
const DATA_OUT_DIR = path.join(FRONTEND_DIR, 'public', 'data');
const CASES_OUT_DIR = path.join(DATA_OUT_DIR, 'cases');
const BATCHES_OUT_DIR = path.join(DATA_OUT_DIR, 'batches');

async function readJson(filePath) {
  const raw = await fs.readFile(filePath, 'utf-8');
  return JSON.parse(raw);
}

async function writeJsonPretty(filePath, value) {
  await fs.writeFile(filePath, JSON.stringify(value, null, 2) + '\n', 'utf-8');
}

/** "20260726_230957" -> ISO string. Batch timestamps are written by the local
 * machine clock (Python's datetime.now(), not UTC), so we parse them as local
 * time rather than assuming UTC. */
function parseBatchTimestamp(ts) {
  const m = /^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})$/.exec(ts);
  if (!m) return null;
  const [, y, mo, d, h, mi, s] = m.map(Number);
  return new Date(y, mo - 1, d, h, mi, s).toISOString();
}

async function syncRootCases() {
  const entries = await fs.readdir(REPO_ROOT, { withFileTypes: true });
  const caseFiles = entries
    .filter((e) => e.isFile() && /^negotiation_log_.*\.json$/i.test(e.name))
    .map((e) => e.name)
    .sort();

  const cases = [];
  for (const fileName of caseFiles) {
    const fullPath = path.join(REPO_ROOT, fileName);
    let parsed;
    try {
      parsed = await readJson(fullPath);
    } catch (err) {
      console.warn(`[sync-data] WARN: could not parse ${fileName}, skipping (${err.message})`);
      continue;
    }
    if (!parsed?.scenario || !Array.isArray(parsed?.messages) || !Array.isArray(parsed?.compliance_checks)) {
      console.warn(`[sync-data] WARN: ${fileName} does not look like a NegotiationState, skipping`);
      continue;
    }

    const id = fileName.replace(/\.json$/i, '');
    await writeJsonPretty(path.join(CASES_OUT_DIR, `${id}.json`), parsed);

    const stat = await fs.stat(fullPath);
    cases.push({
      id,
      source: 'root',
      file: `data/cases/${id}.json`,
      scenarioId: parsed.scenario.dispute_id,
      title: parsed.scenario.title,
      timestamp: stat.mtime.toISOString(),
      timestampSource: 'file-mtime',
      resolved: Boolean(parsed.resolved),
      outcome: parsed.resolution_outcome ?? null,
      roundsTaken: parsed.round_number,
      maxRounds: parsed.max_rounds,
      isRealCase: /^negotiation_log_realcase_/i.test(fileName),
    });
  }

  cases.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  return cases;
}

async function syncBatches() {
  let batchDirs = [];
  try {
    const entries = await fs.readdir(BATCH_RESULTS_DIR, { withFileTypes: true });
    batchDirs = entries
      .filter((e) => e.isDirectory() && /^batch_\d{8}_\d{6}$/.test(e.name))
      .map((e) => e.name)
      .sort();
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.warn('[sync-data] WARN: batch_results/ does not exist, skipping batches');
      return [];
    }
    throw err;
  }

  const batches = [];
  for (const batchId of batchDirs) {
    const batchDir = path.join(BATCH_RESULTS_DIR, batchId);
    let summary;
    try {
      summary = await readJson(path.join(batchDir, 'batch_summary.json'));
    } catch (err) {
      console.warn(`[sync-data] WARN: ${batchId} has no readable batch_summary.json, skipping (${err.message})`);
      continue;
    }

    const dirEntries = await fs.readdir(batchDir, { withFileTypes: true });
    const runFileNumbers = new Map();
    for (const e of dirEntries) {
      const m = e.isFile() && /^run_(\d+)\.json$/.exec(e.name);
      if (m) runFileNumbers.set(Number(m[1]), e.name);
    }

    const outBatchDir = path.join(BATCHES_OUT_DIR, batchId);
    await fs.mkdir(outBatchDir, { recursive: true });
    await writeJsonPretty(path.join(outBatchDir, 'batch_summary.json'), summary);

    const runs = [];
    for (const run of summary.individual_runs ?? []) {
      const runFileName = runFileNumbers.get(run.run_number);
      const hasTranscript = Boolean(runFileName);
      if (hasTranscript) {
        try {
          const runData = await readJson(path.join(batchDir, runFileName));
          await writeJsonPretty(path.join(outBatchDir, runFileName), runData);
        } catch (err) {
          console.warn(`[sync-data] WARN: ${batchId}/${runFileName} could not be parsed, marking as no transcript (${err.message})`);
          runs.push({
            runNumber: run.run_number,
            resolved: run.resolved,
            outcome: run.outcome,
            roundsTaken: run.rounds_taken,
            manifestErrorFoundAnyRound: run.manifest_error_found_any_round,
            hasTranscript: false,
            file: null,
            error: run.error,
          });
          continue;
        }
      }
      runs.push({
        runNumber: run.run_number,
        resolved: run.resolved,
        outcome: run.outcome,
        roundsTaken: run.rounds_taken,
        manifestErrorFoundAnyRound: run.manifest_error_found_any_round,
        hasTranscript,
        file: hasTranscript ? `data/batches/${batchId}/${runFileName}` : null,
        error: run.error,
      });
    }

    const timestampIso = parseBatchTimestamp(summary.timestamp) ?? new Date().toISOString();
    batches.push({
      id: batchId,
      dir: `data/batches/${batchId}`,
      scenarioId: summary.scenario_id,
      scenarioTitle: summary.scenario_title,
      timestamp: summary.timestamp,
      timestampIso,
      nRunsRequested: summary.n_runs_requested,
      nRunsSuccessful: summary.n_runs_successful,
      nRunsFailed: summary.n_runs_failed,
      maxRounds: summary.max_rounds,
      metrics: summary.metrics,
      runs,
    });
  }

  batches.sort((a, b) => b.timestampIso.localeCompare(a.timestampIso));
  return batches;
}

async function main() {
  await fs.rm(DATA_OUT_DIR, { recursive: true, force: true });
  await fs.mkdir(CASES_OUT_DIR, { recursive: true });
  await fs.mkdir(BATCHES_OUT_DIR, { recursive: true });

  const cases = await syncRootCases();
  const batches = await syncBatches();

  if (cases.length === 0 && batches.length === 0) {
    console.warn('[sync-data] WARN: no cases or batches found — landing page will show an empty state.');
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    cases,
    batches,
  };
  await writeJsonPretty(path.join(DATA_OUT_DIR, 'manifest.json'), manifest);

  const totalRuns = batches.reduce((sum, b) => sum + b.runs.length, 0);
  console.log(
    `[sync-data] Synced ${cases.length} case(s) and ${batches.length} batch(es) (${totalRuns} runs) -> frontend/public/data`
  );
}

main().catch((err) => {
  console.error('[sync-data] FATAL:', err);
  process.exitCode = 1;
});
