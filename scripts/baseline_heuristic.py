"""
Heuristic baseline — evaluation item 22. No LLM call, no reasoning, no case-specific
information beyond what "majority class" means for this exact corpus.

WHY THIS EXISTS: of this project's 6 real cases with a clean merits disposition (see
compare_baselines.py's REAL_DISPOSITIONS — Parkingeye and Alstom are interim-suspension
rulings only and excluded, same reasoning as evaluation-five-cases.md), 5 are cases
where the Contracting Authority lost and only 1 (AbbVie) is a case where the CA won.
A predictor that always says "manifest error found, recommend re-evaluation" — with
literally zero reasoning — gets 5/6 right by base rate alone. Any accuracy number the
full pipeline or the zero-shot baseline reports has to be read against that floor, not
treated as evidence of skill by itself. This is the standard "ZeroR" / majority-class
baseline from ML evaluation practice, applied here explicitly rather than left implicit.

This is deliberately NOT "smarter" (e.g. keying off dispute_type) — a per-dispute_type
rule would need its own justification and its own risk of overfitting to this exact
6-case corpus, and the point of a majority-class baseline is specifically to be dumb.

No test file for this one: the entire "prediction" is a single hardcoded constant,
there is no logic to unit-test that isn't already exercised by running the script.
"""

MAJORITY_CLASS_PREDICTION = {
    "process_followed": False,
    "manifest_error_found": True,
    "recommended_action": "re-evaluation",
    "reasoning": (
        "No case-specific reasoning — this is the majority-class baseline. It always "
        "predicts the outcome that is most common across this project's real-case "
        "corpus, regardless of the facts of the specific case."
    ),
}


def predict(scenario) -> dict:
    """Same shape as a ComplianceAssessment dict, minus fields the other baselines
    don't share a common answer for (round_number, applicable_provisions, deadlock)."""
    return dict(MAJORITY_CLASS_PREDICTION)


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.cases.real_cases import REAL_CASES

    print("Heuristic (majority-class) baseline — same fixed prediction for every case:\n")
    for k, v in MAJORITY_CLASS_PREDICTION.items():
        print(f"  {k}: {v}")
    print(f"\nApplies identically to all {len(REAL_CASES)} cases in the corpus — "
          f"see compare_baselines.py for how this scores against real dispositions.")
