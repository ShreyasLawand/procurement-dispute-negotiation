# Frontend

React + Vite + TypeScript + Tailwind dashboard for the procurement dispute
negotiation simulator. Visualizes negotiation transcripts, Court compliance
assessments, and batch evaluation metrics produced by the Python backend
(`../src`, `../tests`). Does **not** call Ollama or any Python process
directly — it only reads static JSON.

## Setup

```bash
npm install
npm run sync-data   # required — see below
npm run dev
```

## Data

`npm run sync-data` copies JSON output from the backend into `public/data/`
and writes `public/data/manifest.json`, which the app fetches at runtime:

- root `../negotiation_log_*.json` files → `public/data/cases/`
- `../batch_results/batch_<timestamp>/` dirs → `public/data/batches/`

Run it manually whenever the backend has produced new logs or batch runs —
it is **not** wired into `npm run dev` automatically, so a stale sync during
dev iteration is never silently masked. `public/data/` is gitignored; it's a
generated copy, not source of truth.

If no data has been synced yet (or `batch_results/` is empty), the landing
page still boots to an empty state rather than crashing.

You can also drag and drop a raw `negotiation_log_*.json` or
`batch_summary.json` file onto the landing page's dropzone to view it
directly, without running the sync script — useful for a one-off file during
a live demo.

## Scripts

- `npm run dev` — start the Vite dev server
- `npm run sync-data` — refresh `public/data/` from the backend's JSON output
- `npm run build` — typecheck (`tsc -b`) and production build
- `npm run preview` — serve the production build locally
- `npm run lint` — oxlint
