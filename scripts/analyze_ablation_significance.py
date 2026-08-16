"""
Statistical rigor layer on the V3/V4 Court-prompt ablation — evaluation punch-list item 29.

Every rate reported in evaluation-five-cases.md and the batch summaries themselves is a bare empirical
proportion from n=8 runs, with no indication of whether a V3-vs-V4 difference is distinguishable from
sampling noise at that sample size. This script is the fix: Fisher's exact test on each case's 2x2
resolution outcome table (resolved vs deadlock, V3 vs V4), and bootstrap 95% confidence intervals on
each cell's resolution rate.

No scipy in this project's dependencies (checked before writing this — not present in requirements.txt
and not installed in .venv), so Fisher's exact test is implemented directly from the hypergeometric
definition rather than adding a dependency for one function. Verified against two independently-derivable
properties before trusting it on real data (see test_fisher_exact_two_tailed.py) — not an appeal to
"scipy would definitely be right", an actual correctness check of this implementation specifically.

HONEST FRAMING: with n=8 per cell, this test has very low power. A non-significant result here does NOT
mean "no real difference" — it means the sample is too small to distinguish a real difference from noise
at conventional confidence levels. Report p-values as p-values, not as verdicts.

Usage:
    python scripts/analyze_ablation_significance.py
    python scripts/analyze_ablation_significance.py --json out.json
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent

CASES = {
    "lancashire-care": ("batch_20260815_213642", "batch_20260815_214210"),
    "faraday-west-berkshire": ("batch_20260815_214543", "batch_20260815_215108"),
    # Superseded 16 Aug 2026: the original pair (batch_20260815_220726 / _221124) ran against a
    # thin extraction that omitted the real 68%/84% score gap and the s101 PA2023 suspension test,
    # and mislabelled dispute_type — see evaluation-bailii-expansion.md's "Parkingeye re-extraction"
    # section for the full comparison and reasoning. Re-run against the corrected scenario cache.
    "parkingeye-velindre": ("batch_20260816_172323", "batch_20260816_172843"),
    "alstom-london-underground": ("batch_20260815_192629", "batch_20260815_193406"),
    "woods-milton-keynes": ("batch_20260815_200902", "batch_20260815_201219"),
}


def fisher_exact_two_tailed(a: int, b: int, c: int, d: int) -> float:
    """
    Two-tailed Fisher's exact test p-value for a 2x2 table:
                col1  col2
        row1     a     b
        row2     c     d

    Sums the hypergeometric probability of every table with the same margins whose probability is
    <= the probability of the observed table — the standard definition of the two-tailed p-value
    (equivalent to what R's fisher.test and scipy.stats.fisher_exact compute).
    """
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    n = row1 + row2
    assert col1 + col2 == n

    def table_prob(x: int) -> float:
        # P(a=x | fixed margins) via the hypergeometric pmf.
        return (
            math.comb(row1, x) * math.comb(row2, col1 - x)
        ) / math.comb(n, col1)

    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    observed = table_prob(a)
    # Tolerance guards against float noise putting the observed table itself just outside its own
    # inclusion band.
    return sum(table_prob(x) for x in range(lo, hi + 1) if table_prob(x) <= observed + 1e-12)


def bootstrap_ci(successes: int, n: int, n_boot: int = 20000, seed: int = 0) -> tuple[float, float]:
    """95% bootstrap CI on a proportion, resampling the n Bernoulli outcomes with replacement."""
    if n == 0:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    data = np.array([1] * successes + [0] * (n - successes))
    resampled_means = rng.choice(data, size=(n_boot, n), replace=True).mean(axis=1)
    lo, hi = np.percentile(resampled_means, [2.5, 97.5])
    return (round(float(lo), 4), round(float(hi), 4))


def _load(batch_id: str) -> dict:
    return json.loads((REPO_ROOT / "batch_results" / batch_id / "batch_summary.json").read_text(encoding="utf-8"))


def analyze() -> dict:
    results = {}
    for case, (v3_id, v4_id) in CASES.items():
        v3 = _load(v3_id)
        v4 = _load(v4_id)

        v3_resolved = sum(1 for r in v3["individual_runs"] if r.get("resolved") is True)
        v3_n = v3["n_runs_successful"]
        v4_resolved = sum(1 for r in v4["individual_runs"] if r.get("resolved") is True)
        v4_n = v4["n_runs_successful"]

        # 2x2: resolved vs deadlocked, V3 vs V4.
        a, b = v3_resolved, v3_n - v3_resolved
        c, d = v4_resolved, v4_n - v4_resolved
        p_resolution = fisher_exact_two_tailed(a, b, c, d)

        v3_manifest = sum(1 for r in v3["individual_runs"] if r.get("manifest_error_found_any_round") is True)
        v4_manifest = sum(1 for r in v4["individual_runs"] if r.get("manifest_error_found_any_round") is True)
        p_manifest = fisher_exact_two_tailed(
            v3_manifest, v3_n - v3_manifest, v4_manifest, v4_n - v4_manifest
        )

        results[case] = {
            "v3": {
                "resolution_rate": round(v3_resolved / v3_n, 4),
                "resolution_ci95": bootstrap_ci(v3_resolved, v3_n),
                "manifest_error_rate": round(v3_manifest / v3_n, 4),
            },
            "v4": {
                "resolution_rate": round(v4_resolved / v4_n, 4),
                "resolution_ci95": bootstrap_ci(v4_resolved, v4_n),
                "manifest_error_rate": round(v4_manifest / v4_n, 4),
            },
            "fisher_exact_p_resolution": round(p_resolution, 4),
            "fisher_exact_p_manifest_error": round(p_manifest, 4),
            "n": v3_n,  # both arms are n=8 throughout this ablation
        }
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    results = analyze()

    print(f"\n{'='*78}")
    print("  V3 vs V4 SIGNIFICANCE — Fisher's exact test, 95% bootstrap CIs (n=8 per arm)")
    print(f"{'='*78}\n")
    for case, r in results.items():
        print(f"{case}")
        print(f"  resolution rate   V3 {r['v3']['resolution_rate']:.2f}  95% CI {r['v3']['resolution_ci95']}"
              f"   |   V4 {r['v4']['resolution_rate']:.2f}  95% CI {r['v4']['resolution_ci95']}")
        print(f"  Fisher's exact p (resolution):      {r['fisher_exact_p_resolution']}"
              f"{'  *' if r['fisher_exact_p_resolution'] < 0.05 else ''}")
        print(f"  manifest-error rate   V3 {r['v3']['manifest_error_rate']:.2f}   V4 {r['v4']['manifest_error_rate']:.2f}")
        print(f"  Fisher's exact p (manifest error):  {r['fisher_exact_p_manifest_error']}"
              f"{'  *' if r['fisher_exact_p_manifest_error'] < 0.05 else ''}")
        print()

    print("* = p < 0.05. At n=8 per arm this test has low power — a non-significant p-value means")
    print("  'not distinguishable from noise at this sample size', not 'no real difference'.")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
