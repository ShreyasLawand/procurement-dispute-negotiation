import { useEffect, useState } from 'react';
import type { BatchSummary, Manifest, NegotiationState } from '../types/negotiation';
import { ManifestSchema } from './manifest-schema';
import { BatchSummarySchema, NegotiationStateSchema } from './schema';

export type LoadStatus = 'loading' | 'error' | 'success';

export interface LoadState<T> {
  status: LoadStatus;
  data?: T;
  error?: unknown;
}

async function fetchJson(url: string): Promise<unknown> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function useManifest(): LoadState<Manifest> {
  const [state, setState] = useState<LoadState<Manifest>>({ status: 'loading' });

  useEffect(() => {
    let cancelled = false;
    setState({ status: 'loading' });
    fetchJson('/data/manifest.json')
      .then((json) => {
        const parsed = ManifestSchema.parse(json);
        if (!cancelled) setState({ status: 'success', data: parsed });
      })
      .catch((error) => {
        if (!cancelled) setState({ status: 'error', error });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}

/** caseId is either a manifest case id (root negotiation logs) or
 * "batch:<batchId>:run_01" addressing one run inside a batch. */
export function useCaseData(caseId: string | undefined): LoadState<NegotiationState> {
  const [state, setState] = useState<LoadState<NegotiationState>>({ status: 'loading' });

  useEffect(() => {
    if (!caseId) {
      setState({ status: 'error', error: new Error('No case id provided') });
      return;
    }
    let cancelled = false;
    setState({ status: 'loading' });

    (async () => {
      try {
        let file: string;
        const batchMatch = /^batch:(.+):(run_\d+)$/.exec(caseId);
        if (batchMatch) {
          const [, batchId, runId] = batchMatch;
          const manifest = ManifestSchema.parse(await fetchJson('/data/manifest.json'));
          const batch = manifest.batches.find((b) => b.id === batchId);
          if (!batch) throw new Error(`Batch "${batchId}" not found in manifest`);
          const runNumber = Number(runId.replace('run_', ''));
          const run = batch.runs.find((r) => r.runNumber === runNumber);
          if (!run || !run.file) {
            throw new Error(`Run "${runId}" in batch "${batchId}" has no transcript`);
          }
          file = run.file;
        } else {
          const manifest = ManifestSchema.parse(await fetchJson('/data/manifest.json'));
          const entry = manifest.cases.find((c) => c.id === caseId);
          if (!entry) throw new Error(`Case "${caseId}" not found in manifest`);
          file = entry.file;
        }

        const json = await fetchJson(`/${file}`);
        const parsed = NegotiationStateSchema.parse(json);
        if (!cancelled) setState({ status: 'success', data: parsed });
      } catch (error) {
        if (!cancelled) setState({ status: 'error', error });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [caseId]);

  return state;
}

export function useBatchData(batchId: string | undefined): LoadState<BatchSummary> {
  const [state, setState] = useState<LoadState<BatchSummary>>({ status: 'loading' });

  useEffect(() => {
    if (!batchId) {
      setState({ status: 'error', error: new Error('No batch id provided') });
      return;
    }
    let cancelled = false;
    setState({ status: 'loading' });

    (async () => {
      try {
        const manifest = ManifestSchema.parse(await fetchJson('/data/manifest.json'));
        const entry = manifest.batches.find((b) => b.id === batchId);
        if (!entry) throw new Error(`Batch "${batchId}" not found in manifest`);
        const json = await fetchJson(`/${entry.dir}/batch_summary.json`);
        const parsed = BatchSummarySchema.parse(json);
        if (!cancelled) setState({ status: 'success', data: parsed });
      } catch (error) {
        if (!cancelled) setState({ status: 'error', error });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [batchId]);

  return state;
}

export interface MultiLoadState<T> {
  status: LoadStatus;
  dataById: Map<string, T>;
  errorsById: Map<string, unknown>;
}

/** Fetches several batches in parallel. Kept separate from useBatchData
 * rather than calling that hook in a loop (which would violate the rules of
 * hooks for a dynamic-length list) — re-fetches whenever the id set changes. */
export function useMultipleBatchData(batchIds: string[]): MultiLoadState<BatchSummary> {
  const key = [...batchIds].sort().join(',');
  const [state, setState] = useState<MultiLoadState<BatchSummary>>({
    status: 'loading',
    dataById: new Map(),
    errorsById: new Map(),
  });

  useEffect(() => {
    if (batchIds.length === 0) {
      setState({ status: 'success', dataById: new Map(), errorsById: new Map() });
      return;
    }
    let cancelled = false;
    setState({ status: 'loading', dataById: new Map(), errorsById: new Map() });

    (async () => {
      try {
        const manifest = ManifestSchema.parse(await fetchJson('/data/manifest.json'));
        const dataById = new Map<string, BatchSummary>();
        const errorsById = new Map<string, unknown>();

        await Promise.all(
          batchIds.map(async (batchId) => {
            try {
              const entry = manifest.batches.find((b) => b.id === batchId);
              if (!entry) throw new Error(`Batch "${batchId}" not found in manifest`);
              const json = await fetchJson(`/${entry.dir}/batch_summary.json`);
              dataById.set(batchId, BatchSummarySchema.parse(json));
            } catch (error) {
              errorsById.set(batchId, error);
            }
          })
        );

        if (!cancelled) setState({ status: 'success', dataById, errorsById });
      } catch (error) {
        if (!cancelled) setState({ status: 'error', dataById: new Map(), errorsById: new Map([['*', error]]) });
      }
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return state;
}
