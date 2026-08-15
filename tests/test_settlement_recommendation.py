"""
Tests for src/recommendation/settlement_recommendation.py.

Pure aggregation over an already-loaded batch_summary dict, no LLM call — same reasoning as
tests/test_challenge_risk.py for why this gets real assertions instead of the eyeball-and-print style
the rest of tests/ uses for agents that need a live model.

Written after a manual audit (15 Aug 2026) found one real gap: no minimum-sample guard, so a batch
with n=1 successful run produced confidence=1.0 indistinguishable from a genuinely well-replicated
result. See test_small_sample_caveat_* below.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from src.recommendation.settlement_recommendation import (
    KNOWN_OUTCOMES,
    SMALL_SAMPLE_THRESHOLD,
    _OUTCOME_MEANING,
    synthesize_recommendation,
)


def _batch(outcomes, complete=True, n_requested=None, n_failed=0, metrics_extra=None):
    """Builds a minimal batch_summary dict in the same shape run_batch_evaluation.py writes."""
    n_ok = len(outcomes)
    runs = [{"run_number": i + 1, "outcome": o, "error": None} for i, o in enumerate(outcomes)]
    metrics = {
        "resolution_rate": 1.0,
        "average_rounds_to_conclusion": 2.0,
        "outcome_distribution": {},
    }
    if metrics_extra:
        metrics.update(metrics_extra)
    return {
        "scenario_id": "TEST-001",
        "scenario_title": "Test scenario",
        "complete": complete,
        "n_runs_requested": n_requested if n_requested is not None else n_ok + n_failed,
        "n_runs_successful": n_ok,
        "n_runs_failed": n_failed,
        "metrics": metrics,
        "individual_runs": runs,
    }


# --- vocabulary integrity --------------------------------------------------------------------------

def test_every_known_outcome_has_a_documented_meaning():
    """
    Catches the class of bug where KNOWN_OUTCOMES gains an entry (because court_prompt.py's vocabulary
    changed) without _OUTCOME_MEANING being updated to match — the recommendation would still
    synthesize, just with an undocumented meaning string silently substituted in.
    """
    for outcome in KNOWN_OUTCOMES:
        assert outcome in _OUTCOME_MEANING, f"{outcome!r} has no entry in _OUTCOME_MEANING"


def test_unknown_outcome_raises_rather_than_silently_reporting():
    batch = _batch(["re-evaluation", "an outcome nobody put in KNOWN_OUTCOMES"])
    with pytest.raises(ValueError, match="outside the known vocabulary"):
        synthesize_recommendation(batch)


# --- completeness gate ------------------------------------------------------------------------------

def test_explicit_incomplete_batch_raises():
    batch = _batch(["re-evaluation"] * 3, complete=False, n_requested=8)
    with pytest.raises(ValueError, match="incomplete batch"):
        synthesize_recommendation(batch)


def test_missing_complete_flag_with_matching_counts_is_accepted():
    """Pre-15-Aug-2026 batches never had a `complete` key; run counts summing correctly is the fallback."""
    batch = _batch(["re-evaluation"] * 4)
    del batch["complete"]
    rec = synthesize_recommendation(batch)
    assert rec.n_runs == 4


def test_missing_complete_flag_with_mismatched_counts_raises():
    batch = _batch(["re-evaluation"] * 4, n_requested=8)  # 4 successful + 0 failed != 8 requested
    del batch["complete"]
    with pytest.raises(ValueError, match="predates the 'complete' flag"):
        synthesize_recommendation(batch)


def test_no_successful_runs_raises():
    batch = _batch([], complete=True)
    with pytest.raises(ValueError, match="no successful runs"):
        synthesize_recommendation(batch)


# --- core aggregation --------------------------------------------------------------------------------

def test_modal_outcome_and_confidence():
    batch = _batch(["re-evaluation"] * 6 + ["deadlock - max rounds reached, escalate to formal proceedings"] * 2)
    rec = synthesize_recommendation(batch)
    assert rec.modal_outcome == "re-evaluation"
    assert rec.confidence == 0.75
    assert rec.n_runs == 8


def test_dissenting_outcomes_exclude_modal_and_sum_correctly():
    batch = _batch(
        ["re-evaluation"] * 5
        + ["deadlock - max rounds reached, escalate to formal proceedings"] * 2
        + ["no remedy - decision stands"] * 1
    )
    rec = synthesize_recommendation(batch)
    assert rec.modal_outcome == "re-evaluation"
    dissenting_names = {d.outcome for d in rec.dissenting_outcomes}
    assert "re-evaluation" not in dissenting_names
    assert dissenting_names == {
        "deadlock - max rounds reached, escalate to formal proceedings",
        "no remedy - decision stands",
    }
    total_share = rec.confidence + sum(d.share for d in rec.dissenting_outcomes)
    assert round(total_share, 4) == 1.0


def test_unanimous_batch_has_no_dissent():
    batch = _batch(["re-evaluation"] * 8)
    rec = synthesize_recommendation(batch)
    assert rec.confidence == 1.0
    assert rec.dissenting_outcomes == []
    assert "no dissent" in rec.rationale


def test_resolution_rate_field_rename_backward_compat():
    """
    resolution_rate was renamed from agreement_rate (15 Aug 2026). Old batches on disk still carry the
    old key under metrics; this module must fall back to it rather than reporting None for every
    pre-rename batch.
    """
    batch = _batch(["re-evaluation"] * 4)
    del batch["metrics"]["resolution_rate"]
    batch["metrics"]["agreement_rate"] = 0.9
    rec = synthesize_recommendation(batch)
    assert rec.resolution_rate == 0.9


# --- the fixed gap: small-sample caveat --------------------------------------------------------------

def test_small_sample_caveat_present_below_threshold():
    batch = _batch(["re-evaluation"])  # n=1
    rec = synthesize_recommendation(batch)
    assert rec.n_runs == 1
    assert rec.confidence == 1.0
    assert rec.sample_size_caveat is not None
    assert "1 successful run" in rec.sample_size_caveat
    # Must not be silently absent from a caller that only reads `rationale`.
    assert rec.sample_size_caveat in rec.rationale


def test_small_sample_caveat_present_for_n_four():
    """n=4 batches genuinely exist on disk from earlier in this project — must still be flagged."""
    batch = _batch(["re-evaluation"] * 4)
    rec = synthesize_recommendation(batch)
    assert rec.sample_size_caveat is not None


def test_small_sample_caveat_absent_at_threshold_boundary():
    batch = _batch(["re-evaluation"] * SMALL_SAMPLE_THRESHOLD)
    rec = synthesize_recommendation(batch)
    assert rec.sample_size_caveat is None


def test_small_sample_caveat_absent_above_threshold():
    batch = _batch(["re-evaluation"] * 8)
    rec = synthesize_recommendation(batch)
    assert rec.sample_size_caveat is None


# --- vocabulary constraint (Doc 3: no invented settlement figures) -----------------------------------

def test_modal_outcome_is_always_from_known_vocabulary():
    """
    Doc 3's hard constraint (award-stage disputes cannot be settled by splitting the difference) means
    this module must never synthesize an outcome outside the Court agent's own vocabulary. Covered
    functionally by test_unknown_outcome_raises_rather_than_silently_reporting; this asserts the
    positive case explicitly.
    """
    for outcome in KNOWN_OUTCOMES:
        batch = _batch([outcome] * SMALL_SAMPLE_THRESHOLD)
        rec = synthesize_recommendation(batch)
        assert rec.modal_outcome in KNOWN_OUTCOMES


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
