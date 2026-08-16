"""
Compares the full multi-agent pipeline against three simpler baselines — evaluation
item 22. Answers the question a dissertation examiner is most likely to ask: does the
multi-agent architecture actually earn its complexity, or would something simpler get
you the same answers?

Comparable on only 6 of this project's 8 real cases: Parkingeye and Alstom are interim-
suspension rulings only (the real court never reached the merits question this system
evaluates), same reasoning already applied in evaluation-five-cases.md and
evaluation-bailii-expansion.md. Comparing a merits prediction against a real disposition
that was never itself a merits ruling would not be a meaningful check.

Usage:
    python scripts/compare_baselines.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ground truth: whether the real court found a manifest error / process failure (True)
# or upheld the CA's process (False), for the 6 cases with a clean merits disposition.
# Sourced from evaluation-five-cases.md and evaluation-bailii-expansion.md — not
# re-derived here, just referenced, so this file is never the first place a disposition
# claim is made.
REAL_DISPOSITIONS = {
    "abbvie-nhs-england": {"violation_found": False, "note": "CA won outright, no manifest error"},
    "braceurself-nhs-england": {"violation_found": True, "note": "Manifest error found (liability), though no damages awarded"},
    "bromcom-united-learning-trust": {"violation_found": True, "note": "CA lost on 3 independent grounds, damages awarded"},
    "lancashire-care": {"violation_found": True, "note": "CA lost on transparency/adequacy-of-reasons"},
    "faraday-west-berkshire": {"violation_found": True, "note": "CA lost on appeal (process avoidance) — note known CA/Bidder premise-fabrication on this case"},
    "woods-milton-keynes": {"violation_found": True, "note": "CA lost, scores corrected by the court"},
}

# Most recent full-pipeline (active/V4 prompt, Court included) batch per case — see
# CLAUDE.md's "BAILII expansion" / "Fix Parkingeye scenario extraction gap" sections for
# how these specific batches were chosen and verified.
FULL_PIPELINE_BATCHES = {
    "abbvie-nhs-england": "batch_results/batch_20260816_162426",
    "braceurself-nhs-england": "batch_results/batch_20260816_165512",
    "bromcom-united-learning-trust": "batch_results/batch_20260816_165719",
    "lancashire-care": "batch_results/batch_20260815_214210",
    "faraday-west-berkshire": "batch_results/batch_20260815_215108",
    "woods-milton-keynes": "batch_results/batch_20260815_201219",
}


def _load_summary(path: str) -> dict | None:
    p = os.path.join(path, "batch_summary.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# A remedy was actually recommended — this is the primary comparison basis, NOT
# manifest_error_found. Found while building this comparison: on Lancashire (a
# transparency/adequacy-of-reasons case, not a scoring/arithmetic one),
# manifest_error_found=False shows up on 2/8 full-pipeline runs AND on all 5 zero-shot
# runs, in every case alongside a correct recommended_action of "re-evaluation" — the
# reasoning identifies the real transparency failure and recommends the right remedy,
# it just doesn't tick a box literally labelled "manifest error" for a violation that
# isn't a manifest error in the scoring-calculation sense. That's a real, defensible
# reading of the field name, not a reasoning failure — using manifest_error_found as
# the "did this system get it right" metric would have penalised both baselines and
# the full pipeline for a labelling nuance rather than an actual mistake.
_REMEDY_ACTIONS = {"re-evaluation", "damages"}


def _full_pipeline_violation_rate(summary: dict) -> float | None:
    """Fraction of successful runs whose outcome was a substantive remedy
    (re-evaluation/damages) rather than no-remedy/continue-negotiation."""
    runs = [r for r in summary["individual_runs"] if r["error"] is None]
    if not runs:
        return None
    return round(sum(1 for r in runs if r["outcome"] in _REMEDY_ACTIONS) / len(runs), 3)


def _zeroshot_violation_rate(summary: dict) -> float | None:
    """Same _REMEDY_ACTIONS basis as the full pipeline, not manifest_error_found —
    see the comment on _REMEDY_ACTIONS above for why."""
    runs = [r for r in summary["individual_runs"] if r["error"] is None]
    if not runs:
        return None
    return round(sum(1 for r in runs if r["recommended_action"] in _REMEDY_ACTIONS) / len(runs), 3)


def _find_latest_zeroshot(case: str, zeroshot_dir: str = "baseline_results/zeroshot") -> dict | None:
    if not os.path.isdir(zeroshot_dir):
        return None
    candidates = []
    for d in os.listdir(zeroshot_dir):
        s = _load_summary(os.path.join(zeroshot_dir, d))
        if s and s.get("case_slug") == case:
            candidates.append((d, s))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]


def main():
    from src.cases.real_cases import REAL_CASES  # noqa: F401 (import kept for parity/consistency checks)

    rows = []
    for case, disposition in REAL_DISPOSITIONS.items():
        real = disposition["violation_found"]

        heuristic_pred = True  # scripts/baseline_heuristic.py's fixed majority-class prediction

        full = _load_summary(FULL_PIPELINE_BATCHES[case])
        full_rate = _full_pipeline_violation_rate(full) if full else None

        zeroshot = _find_latest_zeroshot(case)
        zeroshot_rate = _zeroshot_violation_rate(zeroshot) if zeroshot else None

        rows.append({
            "case": case,
            "real_violation_found": real,
            "note": disposition["note"],
            "heuristic_correct": (heuristic_pred == real),
            "full_pipeline_violation_rate": full_rate,
            "full_pipeline_matches_direction": (
                None if full_rate is None else
                ((full_rate >= 0.5) == real)
            ),
            "zeroshot_violation_rate": zeroshot_rate,
            "zeroshot_matches_direction": (
                None if zeroshot_rate is None else
                ((zeroshot_rate >= 0.5) == real)
            ),
        })

    print("=" * 100)
    print("  BASELINE COMPARISON — evaluation item 22 (n=6 cases with a clean merits disposition)")
    print("=" * 100)
    print(f"{'Case':<32} {'Real':<6} {'Heuristic':<10} {'Full pipeline':<16} {'Zero-shot':<16}")
    for r in rows:
        real_s = "VIOL" if r["real_violation_found"] else "clean"
        heur_s = "correct" if r["heuristic_correct"] else "WRONG"
        full_s = "N/A" if r["full_pipeline_violation_rate"] is None else (
            f"{r['full_pipeline_violation_rate']:.0%} ({'ok' if r['full_pipeline_matches_direction'] else 'WRONG'})"
        )
        zs_s = "N/A" if r["zeroshot_violation_rate"] is None else (
            f"{r['zeroshot_violation_rate']:.0%} ({'ok' if r['zeroshot_matches_direction'] else 'WRONG'})"
        )
        print(f"{r['case']:<32} {real_s:<6} {heur_s:<10} {full_s:<16} {zs_s:<16}")

    heur_correct = sum(1 for r in rows if r["heuristic_correct"])
    full_correct = sum(1 for r in rows if r["full_pipeline_matches_direction"])
    zs_correct = sum(1 for r in rows if r["zeroshot_matches_direction"])
    n = len(rows)
    print()
    print(f"Heuristic (majority-class, zero reasoning):  {heur_correct}/{n} direction-correct")
    print(f"Full multi-agent pipeline (active/V4):        {full_correct}/{n} direction-correct" if full_correct is not None else "Full pipeline: not run")
    print(f"Single-LLM zero-shot:                         {zs_correct}/{n} direction-correct" if any(r['zeroshot_violation_rate'] is not None for r in rows) else "Zero-shot: no data found — run scripts/run_baseline_zeroshot.py for each case first")
    print()
    print("No-Court ablation is reported separately, not in this table — it cannot express a")
    print("violation-found prediction at all (see graph_orchestrator.py::no_court_check_node);")
    print("every run ends in deadlock by design. Check its batch_summary.json's resolution_rate")
    print("(should be 0.0 across every case) as the qualitative finding this ablation exists for.")
    print(f"\nn={n} — this has essentially no statistical power. Read the pattern, not a percentage.")

    return rows


if __name__ == "__main__":
    main()
