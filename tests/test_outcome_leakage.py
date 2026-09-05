"""
Regression test for a real measurement gap caught during Phase 3 (RESULTS-FOR-THESIS.md) and fixed
5 Sep 2026: analyze_outcome_leakage.py's vote-counting used to glob every run_*.json ever logged for a
scenario's dispute_id and pool them into one modal vote regardless of which version of the scenario
description generated each run. For abbvie-nhs-england and faraday-west-berkshire specifically - both
had their scenario description rewritten mid-corpus to strip a stated real-world disposition - this
meant old leaked-era votes and new leak-free votes were silently averaged together.

This test uses the actual committed corpus data (not a synthetic fixture) as the regression case, per
the instruction that motivated the fix: confirm the fixed collect_votes() reproduces, without any
manual isolation, the exact per-case vote counts Phase 3 computed by hand by inspecting batch
directories directly. If either scenario file or its post-fix batches are ever deleted or renamed,
this test will fail loudly rather than silently pass on an empty case - that is the intended behaviour,
not a flake to work around.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from pathlib import Path
from analyze_outcome_leakage import collect_votes, MERITS_TRUTH
from src.cases.real_cases import REAL_CASES

REPO_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SCEN_DIR = REPO_ROOT / "batch_results" / "_scenarios"
BATCH_DIR = REPO_ROOT / "batch_results"

ID_TO_SLUG = {REAL_CASES[s]["dispute_id"].upper(): s for s in MERITS_TRUTH if s in REAL_CASES}


def _current_desc():
    out = {}
    for slug in MERITS_TRUTH:
        p = SCEN_DIR / f"{slug}.json"
        if p.exists():
            out[slug] = json.loads(p.read_text(encoding="utf-8")).get("description", "")
    return out


def test_stale_leaked_era_votes_are_excluded_for_abbvie_and_faraday():
    """
    Both cases have historical batches predating the 5 Sep 2026 leak strip (contaminated) and a
    fresh n=8 batch generated against the corrected description (clean). The fixed collect_votes()
    must count only the clean ones - exact figures Phase 3 verified by hand against the real batch
    directories: abbvie 8 leak-free votes (5 lost / 3 won), faraday 7 leak-free votes (5 lost / 2
    won, one deadlock excluded from its 8-run batch).
    """
    votes, n_stale = collect_votes(SCEN_DIR, BATCH_DIR, ID_TO_SLUG, _current_desc())

    assert n_stale > 0, "this test is meaningless if nothing stale was ever excluded"

    abbvie = votes["abbvie-nhs-england"]
    assert len(abbvie) == 8, f"expected exactly 8 leak-free abbvie votes, got {len(abbvie)}: {abbvie}"
    assert abbvie.count("lost") == 5 and abbvie.count("won") == 3

    faraday = votes["faraday-west-berkshire"]
    assert len(faraday) == 7, f"expected exactly 7 leak-free faraday votes, got {len(faraday)}: {faraday}"
    assert faraday.count("lost") == 5 and faraday.count("won") == 2


def test_never_leaked_cases_are_unaffected_by_the_fix():
    """lancashire-care's description was never rewritten - every historical run for it should still
    vote, exactly as before the fix (its scenario file's mtime/content never changed)."""
    votes, _ = collect_votes(SCEN_DIR, BATCH_DIR, ID_TO_SLUG, _current_desc())
    lancashire = votes["lancashire-care"]
    assert len(lancashire) == 31, f"expected 31 votes (unchanged from pre-fix), got {len(lancashire)}"


def test_full_corpus_matches_phase_3_hand_verified_agreement():
    """The end-to-end regression: running the fixed script's own vote-counting over the real corpus
    must reproduce Phase 3's hand-verified 12/14 leak-free agreement figure, without any manual
    per-case isolation - that manual step is exactly what this fix makes unnecessary."""
    from analyze_outcome_leakage import agreement_from_votes  # noqa: local import, see below

    votes, _ = collect_votes(SCEN_DIR, BATCH_DIR, ID_TO_SLUG, _current_desc())
    ok, total = agreement_from_votes(votes, MERITS_TRUTH)
    assert (ok, total) == (12, 14), f"expected 12/14 leak-free agreement, got {ok}/{total}"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
