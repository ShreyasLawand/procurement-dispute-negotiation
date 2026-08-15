"""
Generates board-facing case studies from real UK procurement dispute
judgments. Each case's source_text below is a dense factual narrative,
grounded in verified real facts (case citation, contract value, dispute
type, and outcome — no invented numbers or formulas), fed through the SAME
pipeline a live document upload would use: ScenarioExtractionAgent ->
GraphNegotiationOrchestrator.run() -> save_log(). This dogfoods the exact
code path the live /api/extract + negotiation feature uses.

Usage:
    python scripts/generate_real_case_studies.py                # all 4 cases
    python scripts/generate_real_case_studies.py --only parkingeye-velindre
    python scripts/generate_real_case_studies.py --max-rounds 5
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.extraction_agent import ScenarioExtractionAgent
from src.graph_orchestrator import GraphNegotiationOrchestrator

REPO_ROOT = Path(__file__).resolve().parent.parent

from src.cases.real_cases import REAL_CASES


def run_case(slug: str, max_rounds: int = 3) -> None:
    case = REAL_CASES[slug]
    print(f"\n[{slug}] Extracting scenario from source text...")
    extractor = ScenarioExtractionAgent()
    scenario = extractor.extract_scenario(
        case["source_text"],
        dispute_id=case["dispute_id"],
        contracting_authority_name=case["contracting_authority_name"],
        bidder_name=case["bidder_name"],
    )
    print(f"[{slug}] Extracted: {scenario.title} (£{scenario.contract_value_gbp:,.0f}, {scenario.dispute_type})")

    orchestrator = GraphNegotiationOrchestrator(max_rounds=max_rounds)
    t0 = time.time()
    final_state = orchestrator.run(scenario)
    elapsed = time.time() - t0
    print(f"[{slug}] Done in {elapsed:.0f}s — outcome: {final_state['resolution_outcome']}")

    out_path = REPO_ROOT / f"negotiation_log_realcase_{slug}.json"
    orchestrator.save_log(final_state, str(out_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=list(REAL_CASES), help="Run a single case by slug")
    parser.add_argument("--max-rounds", type=int, default=3)
    args = parser.parse_args()

    slugs = [args.only] if args.only else list(REAL_CASES)
    failed = []
    for slug in slugs:
        try:
            run_case(slug, args.max_rounds)
        except Exception as exc:  # noqa: BLE001 — one bad case shouldn't lose already-completed work
            print(f"[{slug}] FAILED: {exc}")
            failed.append(slug)

    if failed:
        print(f"\n{len(failed)} case(s) failed: {', '.join(failed)}. Re-run with --only <slug> once fixed.")
