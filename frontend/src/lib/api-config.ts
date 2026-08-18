export const API_BASE: string = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

/**
 * fetch() rejects with a bare `TypeError: Failed to fetch` when the API server itself is
 * unreachable (not running, crashed, wrong port) - indistinguishable at the call site from
 * any other network hiccup, and "Failed to fetch" alone tells a non-technical reader nothing
 * actionable. Reproduced live: this is exactly what a user sees if they open the frontend
 * before starting `python -m uvicorn api.main:app`.
 */
export function describeFetchError(err: unknown): Error {
  if (err instanceof TypeError) {
    return new Error(
      `Could not reach the API server at ${API_BASE}. Make sure it's running — start it with ` +
        `".\\scripts\\start_demo.ps1" or "python -m uvicorn api.main:app --port 8000" — then try again.`
    );
  }
  return err instanceof Error ? err : new Error(String(err));
}
