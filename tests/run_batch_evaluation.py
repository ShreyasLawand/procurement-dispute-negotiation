import sys
import os
import json
import time
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_orchestrator import GraphNegotiationOrchestrator
from src.cases.loader import load_real_scenario
from src.cases.real_cases import REAL_CASES
from src.prompts import court_prompt
from src.utils.compliance_metrics import metrics


def _court_prompt_version(active=None) -> str:
    """
    Which Court prompt this batch actually ran under. V3 and V4 differ only in the
    interest taxonomy, so a results table that doesn't record this is unattributable —
    the two versions are a controlled ablation and the whole point is telling them apart.
    """
    active = active or court_prompt.COURT_SYSTEM_PROMPT
    if active == court_prompt.COURT_SYSTEM_PROMPT_V4:
        return "V4"
    if active == court_prompt.COURT_SYSTEM_PROMPT_V3:
        return "V3"
    return "unknown (COURT_SYSTEM_PROMPT matches neither V3 nor V4)"


def _aggregate_compliance(runs: list) -> dict:
    """Sums the per-run compliance counters into one batch-level view."""
    totals = Counter()
    by_site = {}
    for r in runs:
        c = r.get("compliance") or {}
        for k in ("structured_responses", "clean_responses", "json_fallbacks",
                  "field_coercions", "parse_failures", "repetition_retries"):
            totals[k] += c.get(k, 0)
        for site_kind, sites in (c.get("by_site") or {}).items():
            bucket = by_site.setdefault(site_kind, Counter())
            bucket.update(sites)

    total = totals["structured_responses"]
    clean = totals["clean_responses"]
    return {
        **dict(totals),
        "structural_compliance_rate": round(clean / total, 4) if total else None,
        "by_site": {k: dict(v) for k, v in by_site.items()},
    }


def _build_summary(scenario, results, n_runs, max_rounds, timestamp, court_system_prompt,
                   complete: bool) -> dict:
    """Builds the batch summary from whatever runs have finished so far."""
    successful_runs = [r for r in results if r["error"] is None]
    failed_runs = [r for r in results if r["error"] is not None]

    outcome_counts = Counter(r["outcome"] for r in successful_runs)
    resolved_count = sum(1 for r in successful_runs if r["resolved"])
    manifest_error_count = sum(1 for r in successful_runs if r["manifest_error_found_any_round"])
    avg_rounds = (
        sum(r["rounds_taken"] for r in successful_runs) / len(successful_runs)
        if successful_runs else 0
    )
    avg_duration = (
        sum(r["duration_seconds"] for r in successful_runs) / len(successful_runs)
        if successful_runs else 0
    )

    return {
        "scenario_id": scenario.dispute_id,
        "scenario_title": scenario.title,
        "contracting_authority": scenario.contracting_authority_name,
        "bidder": scenario.bidder_name,
        # False until the final run lands. A batch killed part-way leaves a summary
        # with complete=False rather than no summary at all — these runs take hours,
        # and losing every finished run because the last one didn't happen is not
        # an acceptable failure mode. Never cite figures from an incomplete batch.
        "complete": complete,
        "n_runs_requested": n_runs,
        "n_runs_completed_so_far": len(results),
        "n_runs_successful": len(successful_runs),
        "n_runs_failed": len(failed_runs),
        "max_rounds": max_rounds,
        "timestamp": timestamp,
        # Run provenance — what this batch's numbers actually describe.
        "court_prompt_version": _court_prompt_version(court_system_prompt),
        "ca_profile": (
            scenario.ca_profile.model_dump(exclude_none=True) if scenario.ca_profile else None
        ),
        "bidder_profile": (
            scenario.bidder_profile.model_dump(exclude_none=True) if scenario.bidder_profile else None
        ),
        "metrics": {
            # Renamed from agreement_rate (Aug 2026) — this measures whether the
            # negotiation resolved without deadlock, not whether the parties agreed
            # with each other. Two different quantities that used to share a name.
            "resolution_rate": round(resolved_count / len(successful_runs), 3) if successful_runs else None,
            "deadlock_rate": round(1 - (resolved_count / len(successful_runs)), 3) if successful_runs else None,
            "manifest_error_detection_rate": round(manifest_error_count / len(successful_runs), 3) if successful_runs else None,
            "average_rounds_to_conclusion": round(avg_rounds, 2),
            "average_duration_seconds": round(avg_duration, 1),
            "outcome_distribution": dict(outcome_counts),
        },
        "compliance": _aggregate_compliance(successful_runs),
        "individual_runs": results,
    }


def _write_summary(batch_dir: str, summary: dict) -> None:
    with open(os.path.join(batch_dir, "batch_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)


def run_batch(scenario, n_runs: int = 10, max_rounds: int = 3, output_dir: str = "batch_results",
              court_system_prompt=None):
    """
    Runs the same scenario n_runs times, saves each individual log, and
    produces an aggregated evaluation summary — the first real quantitative
    evidence for the dissertation's evaluation chapter.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(output_dir, f"batch_{timestamp}")
    os.makedirs(batch_dir, exist_ok=True)

    results = []

    for i in range(1, n_runs + 1):
        print(f"\n{'#'*70}")
        print(f"#  RUN {i} of {n_runs}")
        print(f"{'#'*70}")

        orchestrator = GraphNegotiationOrchestrator(
            max_rounds=max_rounds, court_system_prompt=court_system_prompt
        )
        metrics.reset()   # counters are per-run, aggregated across the batch below
        start_time = time.time()

        try:
            final_state = orchestrator.run(scenario)
            duration = time.time() - start_time

            log_path = os.path.join(batch_dir, f"run_{i:02d}.json")
            orchestrator.save_log(final_state, log_path)

            # Extract the key metrics we care about for evaluation
            rounds_taken = final_state["round_number"]
            resolved = final_state["resolved"]
            outcome = final_state["resolution_outcome"]

            manifest_error_rounds = [
                c.round_number for c in final_state["compliance_checks"] if c.manifest_error_found
            ]
            process_not_followed_rounds = [
                c.round_number for c in final_state["compliance_checks"] if not c.process_followed
            ]

            results.append({
                "run_number": i,
                "resolved": resolved,
                "outcome": outcome,
                "rounds_taken": rounds_taken,
                "manifest_error_found_any_round": len(manifest_error_rounds) > 0,
                "manifest_error_rounds": manifest_error_rounds,
                "process_not_followed_any_round": len(process_not_followed_rounds) > 0,
                "duration_seconds": round(duration, 1),
                "compliance": metrics.snapshot(),
                "error": None,
            })

            print(f"\n>> RUN {i} COMPLETE — Outcome: {outcome} | Rounds: {rounds_taken} | Duration: {duration:.1f}s")

        except Exception as e:
            duration = time.time() - start_time
            print(f"\n!! RUN {i} FAILED: {e}")
            results.append({
                "run_number": i,
                "resolved": None,
                "outcome": None,
                "rounds_taken": None,
                "manifest_error_found_any_round": None,
                "manifest_error_rounds": [],
                "process_not_followed_any_round": None,
                "duration_seconds": round(duration, 1),
                "compliance": metrics.snapshot(),
                "error": str(e),
            })

        # Persist after every run, not just at the end. These batches run for hours;
        # a kill or crash on run N must not discard runs 1..N-1 (and their compliance
        # counters, which live only in memory until written).
        _write_summary(batch_dir, _build_summary(
            scenario, results, n_runs, max_rounds, timestamp, court_system_prompt,
            complete=(i == n_runs),
        ))

    summary = _build_summary(
        scenario, results, n_runs, max_rounds, timestamp, court_system_prompt, complete=True
    )
    _write_summary(batch_dir, summary)
    successful_runs = [r for r in results if r["error"] is None]
    failed_runs = [r for r in results if r["error"] is not None]
    outcome_counts = Counter(r["outcome"] for r in successful_runs)

    # --- Print a clean report to terminal ---
    print(f"\n\n{'='*70}")
    print(f"  BATCH EVALUATION SUMMARY — {scenario.title}")
    print(f"{'='*70}\n")
    print(f"Runs completed: {len(successful_runs)} / {n_runs} successful ({len(failed_runs)} failed)")
    print(f"Court prompt: {summary['court_prompt_version']}")
    print(f"CA profile: {summary['ca_profile'] or 'none (unprofiled baseline)'}")
    print(f"Bidder profile: {summary['bidder_profile'] or 'none (unprofiled baseline)'}")
    print(f"\nResolution rate (resolved without deadlock): {summary['metrics']['resolution_rate']}")
    print(f"Deadlock rate: {summary['metrics']['deadlock_rate']}")
    print(f"Manifest error detected in at least one round: {summary['metrics']['manifest_error_detection_rate']}")
    print(f"Average rounds to conclusion: {summary['metrics']['average_rounds_to_conclusion']}")
    print(f"Average run duration: {summary['metrics']['average_duration_seconds']}s")
    print(f"\nOutcome distribution:")
    for outcome, count in outcome_counts.items():
        print(f"   {outcome}: {count} / {len(successful_runs)}")

    if failed_runs:
        print(f"\nFailed runs:")
        for r in failed_runs:
            print(f"   Run {r['run_number']}: {r['error']}")

    print(f"\nAll individual logs and summary saved to: {batch_dir}/")
    print(f"{'='*70}\n")

    return summary


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Batch-evaluate a real procurement dispute case."
    )
    ap.add_argument("--case", default="parkingeye-velindre", choices=sorted(REAL_CASES),
                    help="Which real case to evaluate.")
    ap.add_argument("--court-prompt", default="active", choices=["active", "V3", "V4"],
                    help="Which Court prompt to run. 'active' uses COURT_SYSTEM_PROMPT as configured.")
    ap.add_argument("--runs", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--output-dir", default="batch_results")
    ap.add_argument("--refresh-scenario", action="store_true",
                    help="Re-extract the scenario instead of reusing the cached one. "
                         "Breaks comparability with batches already run against the cache.")
    args = ap.parse_args()

    scenario = load_real_scenario(args.case, refresh=args.refresh_scenario)

    court = {
        "active": None,
        "V3": court_prompt.COURT_SYSTEM_PROMPT_V3,
        "V4": court_prompt.COURT_SYSTEM_PROMPT_V4,
    }[args.court_prompt]

    run_batch(scenario, n_runs=args.runs, max_rounds=args.rounds,
              output_dir=args.output_dir, court_system_prompt=court)
