"""
Tests for scripts/analyze_qualitative_fabrication.py, focused on the regex bug caught while building
it: a trailing \\b immediately after '%' can never match ordinary text (% is a non-word character, so
no word/non-word transition exists before a following space or end-of-string), which silently missed
every bare "NN%" not preceded by the word "score(d)".
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from analyze_qualitative_fabrication import _classify, _extract_score_numbers, _number_grounded


def test_classify_qualitative():
    assert _classify("This scenario is qualitative, as it involves no explicit formula") == "qualitative"


def test_classify_numeric():
    assert _classify("This scenario is numeric (Step 2A). The formula is a 60/40 split") == "numeric"


def test_classify_ambiguous_when_neither_marker_present():
    assert _classify("The parties disagree about the outcome") == "ambiguous_or_neither"


def test_classify_ambiguous_when_both_markers_present():
    """Never guess between qualitative and numeric — a round mentioning both stays unclassified."""
    text = "This scenario is numeric (Step 2A) but also qualitative in places, as it involves no explicit formula"
    assert _classify(text) == "ambiguous_or_neither"


# --- regression test for the caught bug: bare "NN%" not preceded by "score(d)" -----------------------

def test_extracts_both_percentages_not_preceded_by_score_word():
    """
    Regression test: an earlier version of _SCORE_NUMBER had a trailing \\b after '%' that could never
    match, so only the FIRST of two percentages in 'scored 84% against 68%' was extracted (the second,
    bare '68%', was silently missed). Caught by testing against real two-percentage text, not by
    inspection.
    """
    numbers = _extract_score_numbers("the overall percentage was 84%, well above the 68% threshold")
    assert numbers == {"84", "68"}


def test_extracts_fraction_scores():
    assert _extract_score_numbers("62/100 vs 88/100") == {"62", "88"}


def test_extracts_score_of_n_phrasing():
    assert _extract_score_numbers("awarded a score of 91 for this criterion") == {"91"}


def test_does_not_match_contract_values_or_citations():
    for text in [
        "a £2,000,000 contract",
        "s12(1)(a) of the Procurement Act 2023",
        "Regulation 84(2)",
        "in 2018",
    ]:
        assert _extract_score_numbers(text) == set()


# --- grounding check ------------------------------------------------------------------------------

def test_grounded_number_is_not_flagged():
    desc = "BuildRight scored 62/100 while Ironclad scored 88/100 on Q4."
    assert _number_grounded("62", desc) is True
    assert _number_grounded("88", desc) is True


def test_ungrounded_number_is_flagged():
    desc = "BuildRight scored 62/100 while Ironclad scored 88/100 on Q4."
    assert _number_grounded("99", desc) is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
