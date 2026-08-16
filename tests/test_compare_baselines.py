"""
Regression test for a real bug caught while building scripts/compare_baselines.py:
the violation-rate functions originally checked manifest_error_found, which undercounts
correct outcomes on cases like Lancashire (a transparency/adequacy-of-reasons failure,
not a scoring/arithmetic one) — both the full pipeline (2/8 runs) and the zero-shot
baseline (5/5 runs) recommended the correct remedy ("re-evaluation") while leaving
manifest_error_found=False, a defensible reading of that field name for a violation
that genuinely isn't a manifest error in the calculation sense. Fixed by switching to
recommended_action/outcome against _REMEDY_ACTIONS, which is what these tests lock in.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from compare_baselines import _full_pipeline_violation_rate, _zeroshot_violation_rate, _REMEDY_ACTIONS


def _full_pipeline_summary(*outcomes_and_errors):
    """outcomes_and_errors: list of (outcome, manifest_error_found_any_round, error)."""
    return {
        "individual_runs": [
            {"outcome": o, "manifest_error_found_any_round": m, "error": e}
            for o, m, e in outcomes_and_errors
        ]
    }


def test_remedy_actions_are_exactly_reevaluation_and_damages():
    assert _REMEDY_ACTIONS == {"re-evaluation", "damages"}


def test_full_pipeline_counts_remedy_outcome_even_without_manifest_error_flag():
    """The Lancashire case, reproduced directly: recommended_action is the correct
    remedy despite manifest_error_found_any_round being False."""
    summary = _full_pipeline_summary(
        ("re-evaluation", False, None),
        ("re-evaluation", True, None),
    )
    assert _full_pipeline_violation_rate(summary) == 1.0


def test_full_pipeline_no_remedy_outcomes_score_zero():
    summary = _full_pipeline_summary(
        ("no remedy - decision stands", False, None),
        ("continue negotiation", False, None),
    )
    assert _full_pipeline_violation_rate(summary) == 0.0


def test_full_pipeline_ignores_failed_runs():
    summary = _full_pipeline_summary(
        ("re-evaluation", True, None),
        (None, None, "some LLM error"),
    )
    assert _full_pipeline_violation_rate(summary) == 1.0  # 1/1 successful, not 1/2


def test_zeroshot_counts_remedy_action_even_without_manifest_error_flag():
    summary = {
        "individual_runs": [
            {"recommended_action": "re-evaluation", "manifest_error_found": False, "error": None},
        ]
    }
    assert _zeroshot_violation_rate(summary) == 1.0


def test_zeroshot_damages_action_counts_as_violation():
    summary = {
        "individual_runs": [
            {"recommended_action": "damages", "manifest_error_found": False, "error": None},
        ]
    }
    assert _zeroshot_violation_rate(summary) == 1.0


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
