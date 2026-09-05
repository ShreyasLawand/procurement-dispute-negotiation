"""
Tests for scripts/analyze_qualitative_fabrication.py.

Two generations of regression tests live here. The original set covers the regex bug caught while
building the extractor: a trailing \\b immediately after '%' can never match ordinary text (% is a
non-word character, so no word/non-word transition exists before a following space or end-of-string),
which silently missed every bare "NN%" not preceded by the word "score(d)".

The second set (4 Sep 2026) covers the widening described in the module's own "WIDENED 4 Sep 2026"
docstring: the new bare "A=80" / "Bidder 1: 80" extraction branch, its citation/date rejection, and the
numeric-round input-vs-result distinction that lets "84 - 68 = 16" (real inputs, real arithmetic) pass
while "(80+85+92)/3 = 85.67" (invented inputs, real arithmetic) is caught.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from analyze_qualitative_fabrication import (
    _classify,
    _extract_score_numbers,
    _number_grounded,
    _is_citation_or_date_context,
    _numeric_round_ungrounded,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


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


# --- new 4 Sep 2026: bare "A=80" / "Bidder 1: 80" extraction --------------------------------------

def test_extracts_bare_label_equals_number():
    """The Bromcom shape: a label, '=', 1-3 digits, no unit at all."""
    numbers = _extract_score_numbers("Bidder 1: A=80, B=70, C=90")
    assert numbers == {"80", "70", "90"}


def test_extracts_bare_label_colon_number():
    assert _extract_score_numbers("Bidder 1: 80") == {"80"}


def test_label_number_rejects_section_citation():
    """'s12: 84' looks like a score by shape alone but is a section reference — must not extract."""
    for text in ["s12: 84", "Section 12: 84", "sec 51: 84", "s.12: 84"]:
        assert _extract_score_numbers(text) == set(), f"false positive on {text!r}"


def test_label_number_rejects_year_in_or_near_label():
    for text in ["Act 2023: 84", "the 2018 judgment: 84"]:
        assert _extract_score_numbers(text) == set(), f"false positive on {text!r}"


def test_label_number_accepts_genuine_criterion_labels():
    """The rejection rules must not be so broad they eat legitimate labels."""
    assert _extract_score_numbers("Criterion B: 84") == {"84"}
    assert _extract_score_numbers("Sub-score B: 84") == {"84"}


def test_is_citation_or_date_context_direct():
    assert _is_citation_or_date_context("s12", "") is True
    assert _is_citation_or_date_context("Section 12", "") is True
    assert _is_citation_or_date_context("Act 2023", "") is True
    assert _is_citation_or_date_context("the 2018 judgment", "") is True
    assert _is_citation_or_date_context("Criterion B", "") is False
    assert _is_citation_or_date_context("A", "") is False


def test_bare_four_digit_year_never_matches_score_number():
    """A lone year is excluded by construction (no \\b can land inside a 4-digit run), not by the
    citation filter — this just confirms that construction actually holds."""
    assert _extract_score_numbers("the case was decided in 2018") == set()


def test_does_not_match_contract_values_or_citations_with_label_branch_active():
    """Re-run the original no-colon-or-equals-present cases now that a fourth branch exists."""
    for text in [
        "a £2,000,000 contract",
        "s12(1)(a) of the Procurement Act 2023",
        "Regulation 84(2)",
        "in 2018",
    ]:
        assert _extract_score_numbers(text) == set()


# --- new 4 Sep 2026: numeric-round input-vs-result distinction ------------------------------------

def test_numeric_round_correct_derivation_is_not_flagged():
    """
    The exact shape the module docstring already documents as a false-positive risk: a correctly
    derived difference from two numbers that ARE grounded. Modelled on the historical 79-65=14
    instance (no longer present in the corpus after the F21-001/F21-002 cleanup), constructed here
    since the qualitative-check era's original example predates this corpus.
    """
    description = (
        "Woods' corrected quality score was 79 and EAS's corrected quality score was 65, "
        "a swing of 14 points in Woods' favour."
    )
    reasoning = (
        "This scenario is numeric (Step 2A). Woods' corrected score is 79 and EAS's corrected "
        "score is 65. To verify the margin, I will calculate the difference: 79-65=14. This "
        "confirms the 14-point swing described in the scenario."
    )
    assert _classify(reasoning) == "numeric"
    assert _numeric_round_ungrounded(reasoning, description) == set()


def test_numeric_round_flags_invented_inputs_even_with_correct_arithmetic():
    """
    The Bromcom shape in miniature: arithmetically correct, every input invented. The equation's
    RESULT (85.67) must not itself be required to be grounded; the INPUTS (80, 85, 92, 3) must be.
    """
    description = "UL's procurement was challenged by Bromcom on grounds of unlawful score averaging."
    reasoning = (
        "This scenario is numeric (Step 2A). Let's assume there were three bidders: "
        "Bidder 1: A=80, B=70, C=90. The average for A is (80+85+92)/3 = 85.67."
    )
    assert _classify(reasoning) == "numeric"
    ungrounded = _numeric_round_ungrounded(reasoning, description)
    for invented in ("80", "85", "92"):
        assert invented in ungrounded, f"{invented} should be flagged as an ungrounded input"
    # the correctly-computed result must not be flagged on its own
    assert "85.67" not in ungrounded


def test_numeric_round_bromcom_actual_log():
    """
    Re-tests against the real, committed Bromcom log this widening was built to catch — not a
    synthetic reconstruction. batch_20260816_165719/run_03.json round 1 is the run documented in
    CLAUDE.md and the thesis as the Step 1 fabrication the pre-widening screen could never see,
    because the round self-classified "numeric" and the population gate skipped numeric rounds
    entirely.
    """
    path = os.path.join(
        REPO_ROOT, "batch_results", "batch_20260816_165719", "run_03.json"
    )
    log = json.loads(open(path, encoding="utf-8").read())
    description = log["scenario"]["description"]
    check = next(c for c in log["compliance_checks"] if c["round_number"] == 1)
    reasoning = check["reasoning"]

    assert _classify(reasoning) == "numeric", (
        "this test's whole point is that the run self-classifies numeric; if that ever stops "
        "being true the fixture no longer demonstrates what it's meant to"
    )
    ungrounded = _numeric_round_ungrounded(reasoning, description)
    # every one of the invented per-bidder scores must be caught
    for invented in ("80", "70", "90", "85", "75", "95", "92", "82", "98"):
        assert invented in ungrounded, f"{invented} should be flagged as an ungrounded input"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
