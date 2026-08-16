"""
Applies the same qualitative-fabrication screen (analyze_qualitative_fabrication.py's
_extract_score_numbers / _number_grounded) to the zero-shot baseline's own reasoning
text, checked against each case's real scenario description.

WHY: the baseline comparison (compare_baselines.py) found zero-shot matches the full
pipeline exactly on direction (6/6 both) at n=6 — raw accuracy is not where an
architectural difference would show up at this sample size. The more likely place a
naive, unhardened prompt (see zeroshot_prompt.py's docstring) actually differs from
court_prompt.py's explicit anti-fabrication discipline is in HOW it gets to a right
answer, not whether the final answer is right — a fabricated number that happens to
support the correct conclusion is still a fabrication.
"""

import sys
import os
import json
import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(__file__))

from analyze_qualitative_fabrication import _extract_score_numbers, _number_grounded
from src.cases.loader import load_real_scenario

CASES = [
    "abbvie-nhs-england", "braceurself-nhs-england", "bromcom-united-learning-trust",
    "lancashire-care", "faraday-west-berkshire", "woods-milton-keynes",
]


def main():
    descriptions = {c: load_real_scenario(c).description for c in CASES}

    total_checked = 0
    suspects = []

    for d in sorted(glob.glob("baseline_results/zeroshot/zeroshot_*")):
        summary_path = os.path.join(d, "batch_summary.json")
        if not os.path.exists(summary_path):
            continue
        s = json.load(open(summary_path, encoding="utf-8"))
        case_slug = s.get("case_slug")
        description = descriptions.get(case_slug)
        if description is None:
            continue
        for r in s["individual_runs"]:
            if r["error"] is not None or not r.get("reasoning"):
                continue
            total_checked += 1
            numbers = _extract_score_numbers(r["reasoning"])
            for n in numbers:
                if not _number_grounded(n, description):
                    suspects.append((case_slug, r["run_number"], n, r["reasoning"]))

    print(f"Reasoning texts checked: {total_checked}")
    print(f"Ungrounded numbers flagged: {len(suspects)}")
    for case, run, n, reasoning in suspects:
        print(f"\n--- {case} run {run}: ungrounded number '{n}' ---")
        print(reasoning[:500])


if __name__ == "__main__":
    main()
