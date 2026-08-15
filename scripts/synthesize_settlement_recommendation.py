"""
CLI for the settlement recommendation synthesizer (src/recommendation/settlement_recommendation.py).

Pure aggregation over an already-completed batch — run tests/run_batch_evaluation.py first. No LLM call;
see that module's docstring for exactly what this does and does not do, and why it's scoped this narrowly.

Usage:
    python scripts/synthesize_settlement_recommendation.py batch_results/batch_20260815_150210
    python scripts/synthesize_settlement_recommendation.py batch_results/batch_20260815_150210 --json out.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.recommendation.settlement_recommendation import synthesize_recommendation

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("batch_dir", help="Path to a batch_results/batch_<timestamp>/ directory")
    ap.add_argument("--json", metavar="PATH", help="write the full recommendation as JSON to this path")
    args = ap.parse_args()

    summary_path = Path(args.batch_dir) / "batch_summary.json"
    if not summary_path.exists():
        print(f"No batch_summary.json found at {summary_path}", file=sys.stderr)
        sys.exit(1)

    batch_summary = json.loads(summary_path.read_text(encoding="utf-8"))

    try:
        rec = synthesize_recommendation(batch_summary)
    except ValueError as e:
        print(f"Cannot synthesize a recommendation: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'=' * 70}")
    print("  SETTLEMENT RECOMMENDATION (non-binding decision support)")
    print(f"{'=' * 70}")
    print(f"{rec.scenario_title}  ({rec.scenario_id})")
    print(f"Based on {rec.n_runs} completed simulated negotiations\n")
    print(f"RECOMMENDED: {rec.modal_outcome}")
    print(f"  {rec.modal_outcome_meaning}")
    print(f"  Confidence: {rec.confidence:.0%}\n")

    if rec.dissenting_outcomes:
        print("Dissenting outcomes (do not ignore these):")
        for d in rec.dissenting_outcomes:
            print(f"  {d.share:.0%} ({d.n_runs}/{rec.n_runs}) reached: {d.outcome}")
        print()

    print("Rationale:")
    print(f"  {rec.rationale}\n")
    print("Framing:")
    print(f"  {rec.framing_caveat}")

    if args.json:
        Path(args.json).write_text(rec.model_dump_json(indent=2), encoding="utf-8")
        print(f"\nFull recommendation written to {args.json}")
