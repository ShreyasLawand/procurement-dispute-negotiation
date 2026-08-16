"""
Runs the single-LLM zero-shot baseline (evaluation item 22) over a real case, n times.

Usage:
    python scripts/run_baseline_zeroshot.py --case abbvie-nhs-england --runs 5
    python scripts/run_baseline_zeroshot.py --case abbvie-nhs-england --runs 5 --output-dir baseline_results/zeroshot

Output shape is deliberately parallel to batch_results/batch_*/batch_summary.json (same
scenario_id/scenario_title, same n_runs_successful/failed, same outcome_distribution) so
scripts/compare_baselines.py can read both without a special case per baseline.
"""

import sys
import os
import json
import time
from datetime import datetime
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.zeroshot_agent import ZeroShotAgent
from src.cases.loader import load_real_scenario
from src.cases.real_cases import REAL_CASES
from src.utils.compliance_metrics import metrics


def run_zeroshot_batch(scenario, n_runs: int, output_dir: str, case_slug: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(output_dir, f"zeroshot_{scenario.dispute_id}_{timestamp}")
    os.makedirs(batch_dir, exist_ok=True)

    agent = ZeroShotAgent()
    results = []

    for i in range(1, n_runs + 1):
        print(f"\n{'#'*70}\n#  ZERO-SHOT RUN {i} of {n_runs} — {scenario.title}\n{'#'*70}")
        metrics.reset()
        start = time.time()
        try:
            assessment = agent.assess(scenario)
            duration = time.time() - start
            results.append({
                "run_number": i,
                "process_followed": assessment.process_followed,
                "manifest_error_found": assessment.manifest_error_found,
                "recommended_action": assessment.recommended_action,
                "reasoning": assessment.reasoning,
                "applicable_provisions": assessment.applicable_provisions,
                "duration_seconds": round(duration, 1),
                "compliance": metrics.snapshot(),
                "error": None,
            })
            print(f"   process_followed={assessment.process_followed}  manifest_error_found={assessment.manifest_error_found}")
            print(f"   recommended_action={assessment.recommended_action}")
        except Exception as e:
            duration = time.time() - start
            print(f"   !! RUN {i} FAILED: {e}")
            results.append({
                "run_number": i, "process_followed": None, "manifest_error_found": None,
                "recommended_action": None, "reasoning": None, "applicable_provisions": [],
                "duration_seconds": round(duration, 1), "compliance": metrics.snapshot(),
                "error": str(e),
            })

    successful = [r for r in results if r["error"] is None]
    failed = [r for r in results if r["error"] is not None]
    outcome_counts = Counter(r["recommended_action"] for r in successful)
    manifest_error_count = sum(1 for r in successful if r["manifest_error_found"])

    summary = {
        "baseline": "zeroshot",
        "case_slug": case_slug,  # exact REAL_CASES key — used by compare_baselines.py, more
                                  # robust than reconstructing it from scenario_id/title
        "scenario_id": scenario.dispute_id,
        "scenario_title": scenario.title,
        "complete": True,
        "n_runs_requested": n_runs,
        "n_runs_successful": len(successful),
        "n_runs_failed": len(failed),
        "timestamp": timestamp,
        "metrics": {
            "manifest_error_detection_rate": round(manifest_error_count / len(successful), 3) if successful else None,
            "outcome_distribution": dict(outcome_counts),
            "average_duration_seconds": round(sum(r["duration_seconds"] for r in successful) / len(successful), 1) if successful else 0,
        },
        "individual_runs": results,
    }

    with open(os.path.join(batch_dir, "batch_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n{'='*70}\n  ZERO-SHOT SUMMARY — {scenario.title}\n{'='*70}")
    print(f"Runs: {len(successful)}/{n_runs} successful")
    print(f"Manifest error detection rate: {summary['metrics']['manifest_error_detection_rate']}")
    print(f"Outcome distribution: {dict(outcome_counts)}")
    print(f"Saved to: {batch_dir}/")

    return summary


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Single-LLM zero-shot baseline (evaluation item 22).")
    ap.add_argument("--case", default="abbvie-nhs-england", choices=sorted(REAL_CASES))
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--output-dir", default="baseline_results/zeroshot")
    ap.add_argument("--refresh-scenario", action="store_true")
    args = ap.parse_args()

    scenario = load_real_scenario(args.case, refresh=args.refresh_scenario)
    run_zeroshot_batch(scenario, n_runs=args.runs, output_dir=args.output_dir, case_slug=args.case)
