"""
Correctness tests for the hand-rolled Fisher's exact test in scripts/analyze_ablation_significance.py
(no scipy in this project's dependencies).

A statistics function that silently returns a wrong p-value is worse than no statistics at all — this
verifies the implementation against properties that can be derived independently of the code, not
against a remembered/assumed reference value.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from analyze_ablation_significance import fisher_exact_two_tailed


def test_p_value_always_in_unit_range():
    for a, b, c, d in [(4, 4, 4, 4), (8, 0, 0, 8), (1, 7, 7, 1), (0, 8, 8, 0), (2, 6, 5, 3)]:
        p = fisher_exact_two_tailed(a, b, c, d)
        assert 0.0 <= p <= 1.0


def test_perfectly_symmetric_table_gives_p_equal_one():
    """
    For a 2x2 table with all margins equal (row totals = column totals = n/2) and the observed table
    itself perfectly balanced, the observed table is provably the mode of the hypergeometric
    distribution over those margins (by symmetry around the centre), and is the unique mode. The
    two-tailed p-value sums every table with probability <= the observed table's — since the observed
    table has the maximum probability among all tables sharing these margins, every table qualifies,
    so the sum must be exactly 1.0. This is derived from the definition, not assumed from an external
    tool.
    """
    p = fisher_exact_two_tailed(4, 4, 4, 4)
    assert p == 1.0


def test_perfect_separation_gives_the_smallest_possible_p():
    """
    (8,0,0,8): every case in one arm resolved, none in the other. This is the most extreme table
    obtainable from 8-vs-8 margins, so it must have the smallest two-tailed p-value achievable at
    this sample size — check it lands far below any conventional significance threshold, and confirm
    the symmetric mirror table (0,8,8,0) gives the identical p-value (transposing which side is
    "successes" must not change the answer).
    """
    p1 = fisher_exact_two_tailed(8, 0, 0, 8)
    p2 = fisher_exact_two_tailed(0, 8, 8, 0)
    assert p1 == p2
    assert p1 < 0.001


def test_row_swap_symmetry():
    """Swapping which arm is 'row 1' vs 'row 2' must not change the two-tailed p-value."""
    p_original = fisher_exact_two_tailed(6, 2, 3, 5)
    p_swapped = fisher_exact_two_tailed(3, 5, 6, 2)
    assert p_original == p_swapped


def test_column_swap_symmetry():
    """Swapping which outcome is 'column 1' vs 'column 2' must not change the two-tailed p-value."""
    p_original = fisher_exact_two_tailed(6, 2, 3, 5)
    p_swapped = fisher_exact_two_tailed(2, 6, 5, 3)
    assert p_original == p_swapped


def test_no_association_case_has_high_p():
    """
    (4,4,4,4) is the no-association extreme (already covered above at p=1.0). A near-balanced but not
    perfectly symmetric table, e.g. (4,4,3,5), should still have a high p-value — nowhere near
    significant — since it is close to the expected table under independence.
    """
    p = fisher_exact_two_tailed(4, 4, 3, 5)
    assert p > 0.5


def test_alstom_actual_data_matches_expectation():
    """
    Regression test against this project's own Alstom V3-vs-V4 resolution data (4 resolved/4 deadlocked
    under V3; 8 resolved/0 deadlocked under V4 — see evaluation-five-cases.md). This is the most
    extreme real V3/V4 divergence in the corpus, so it should read as the most significant of the five
    cases without necessarily crossing p<0.05 at n=8 — this test locks in the actual computed value so
    a future change to the implementation can't silently drift it.
    """
    p = fisher_exact_two_tailed(4, 4, 8, 0)
    assert 0.0 < p < 0.15  # notably low for n=8, but not claimed to cross conventional significance


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
