import sys
import os
import json
import time
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_orchestrator import GraphNegotiationOrchestrator
from src.scenarios.scenario_001 import scoring_challenge


def run_batch(scenario, n_runs: int = 10, max_rounds: int = 3, output_dir: str = "batch_results"):
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

        orchestrator = GraphNegotiationOrchestrator(max_rounds=max_rounds)
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
                "error": str(e),
            })

    # --- Aggregate analysis ---
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

    summary = {
        "scenario_id": scenario.dispute_id,
        "scenario_title": scenario.title,
        "n_runs_requested": n_runs,
        "n_runs_successful": len(successful_runs),
        "n_runs_failed": len(failed_runs),
        "max_rounds": max_rounds,
        "timestamp": timestamp,
        "metrics": {
            "agreement_rate": round(resolved_count / len(successful_runs), 3) if successful_runs else None,
            "deadlock_rate": round(1 - (resolved_count / len(successful_runs)), 3) if successful_runs else None,
            "manifest_error_detection_rate": round(manifest_error_count / len(successful_runs), 3) if successful_runs else None,
            "average_rounds_to_conclusion": round(avg_rounds, 2),
            "average_duration_seconds": round(avg_duration, 1),
            "outcome_distribution": dict(outcome_counts),
        },
        "individual_runs": results,
    }

    summary_path = os.path.join(batch_dir, "batch_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # --- Print a clean report to terminal ---
    print(f"\n\n{'='*70}")
    print(f"  BATCH EVALUATION SUMMARY — {scenario.title}")
    print(f"{'='*70}\n")
    print(f"Runs completed: {len(successful_runs)} / {n_runs} successful ({len(failed_runs)} failed)")
    print(f"\nAgreement rate (resolved without deadlock): {summary['metrics']['agreement_rate']}")
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
    N_RUNS = 8
    MAX_ROUNDS = 5      # adjust as needed — start smaller (e.g. 3) to test the script works, then scale up

    run_batch(scoring_challenge, n_runs=N_RUNS, max_rounds=MAX_ROUNDS)