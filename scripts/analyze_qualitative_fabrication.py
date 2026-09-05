"""
Fabrication-rate detector on qualitative (Step 2B) Court reasoning — evaluation punch-list item 17.

This project's central, hand-won empirical finding is that the Court agent must not invent arithmetic
on qualitative scenarios (CLAUDE.md "Court Agent Design"). That finding has so far been established by
manual spot-checking (the V1->V3 prompt history) and by catching one instance live during the Woods
extraction-fidelity debugging. This script automates the check across the whole corpus: for every
compliance_check that took the Step 2B / qualitative path, extract every score-shaped number
("NN%", "NN/100", "score of NN", "NN points") the reasoning cites, and check whether that number
actually appears anywhere in the scenario's own description — the ground truth the Court agent is
supposed to be reasoning FROM, not inventing.

WHY THE SCENARIO DESCRIPTION IS THE RIGHT GROUND TRUTH, NOT THE NEGOTIATION DIALOGUE: the Faraday
finding (evaluation-five-cases.md) showed the CA/Bidder agents can themselves fabricate a factual
premise. Checking a Court citation against what a CA/Bidder said in dialogue would let the Court's
citation "pass" by uncritically repeating another agent's fabrication. The scenario description is the
one thing in a run that is supposed to be author-verified fact (real cases) or a deliberately-authored
fixture (the deleted synthetic pair) — it is the only defensible ground truth for "did the Court
actually compute/cite something real."

WHAT THIS DOES NOT CATCH: a fabricated number that happens to coincide with a real number elsewhere in
the description (e.g. reusing the real contract value as a fake score) will not be flagged — this is a
string-presence check, not a semantic one. It also does not catch fabrication in Step 2A (numeric)
rounds, which is a different, already-covered concern (see the Woods Step 1 gating fix). This is a
screening tool, same posture as the other analyze_*.py scripts in this directory — false negatives are
expected; every flagged case is worth a human read, not an automated final verdict.

RESULT OF THAT HUMAN READ (15 Aug 2026, full corpus, 190 qualitative rounds, 6 automated flags): every
flag is a false positive FOR COURT FABRICATION SPECIFICALLY, but not a boring one. One is the Court
correctly deriving a simple difference (79-65=14) from two numbers that ARE grounded in the scenario —
this detector checks string presence, not arithmetic, so a correct derived value from real inputs will
always be flagged; that is a known, accepted limitation, not a bug. The other five all follow the same
shape: the Court explicitly attributes the number to a party's claim and declines to treat it as
established fact ("this is not a numeric value that can be independently verified" — an exact quote)
— textbook-correct Step 2B behaviour, not fabrication. But three of those five are on Alstom, whose
real record specifies a binary pass/fail technical threshold with NO percentage scores anywhere — so
the CA/Bidder agents are inventing quantitative specificity ("80%", "a minimum score of 85%... achieved
92%", "a score of 4 out of 10") for a case that has none in reality. That is not Court fabrication —
the Court's caution about it is exactly right — but it is the same failure class as the Faraday finding
(evaluation-five-cases.md §4.2): a fabricated factual premise introduced by the negotiating agents, not
caught because nothing checks a CA/Bidder claim against the scenario record the way the Court's own
Step 1 gate checks its own numeric inputs. Net read: 0/190 confirmed genuine Court fabrications — a
real, positive confirmation of the central finding at corpus scale — plus a second independent sighting
of the CA/Bidder-level fabrication gap this project has not yet built a check for.

WIDENED 4 Sep 2026 — two things fixed together because they were compounding on the same known miss.
First, the population gate used to skip every round the Court self-labelled "numeric" entirely (`if cls
!= "qualitative": continue`), on the theory that Step 2A verification is a separate, already-covered
concern. That theory has a hole: self-labelling "numeric" doesn't require the Court to actually have a
real formula and real inputs — see the Bromcom instance already documented in CLAUDE.md, where the
Court states "This scenario is numeric (Step 2A)" and then invents a complete twelve-number per-bidder
dataset with no formula given at all. That run was never in this screen's population, on either side of
the classify() line, purely because of its own opening sentence.

Second, even if a numeric round HAD been screened by the old logic, the round-3 result the docstring
above already treats as ground truth — a straight string-presence check — is the wrong check for a
correctly-computed Step 2A round: "84 - 68 = 16" is exactly the sanctioned behaviour (real inputs, real
arithmetic), and flagging the result "16" for not appearing verbatim in the scenario would have been a
false positive of the same shape the docstring already accepts for "79-65=14".

The fix distinguishes the two cases properly instead of picking one and living with the other's cost.
_ARITHMETIC_EQUATION finds every "<expression> = <result>" the Court writes, and only the expression's
OWN INPUT numbers are checked for groundedness — never the result, which is legitimately derived and is
not expected to appear in the scenario text. A number appearing outside any such expression (a bare
claim with no arithmetic behind it, which is exactly the Bromcom shape: "Bidder 1: A=80, B=70, C=90" has
no "=result" form at all, it's a declaration) is checked the same way the qualitative path always has
been: flagged if it doesn't appear in the scenario. _SCORE_NUMBER also gained a fourth branch for that
bare-declaration shape (see its own comment below for exactly what it does and doesn't cover).

RESULT OF RE-SCREENING (4 Sep 2026, corrected and finalised 5 Sep 2026): see RESULTS-FOR-THESIS.md for
the full corpus-wide before/after. This widening was originally scoped, and first reported, as closing
the single known Bromcom miss. On completing the human read of every newly-flagged numeric-round
suspect, the true scope is larger: **9 confirmed Court-originated fabrication instances corpus-wide**
(up from the single previously-known Bromcom miss), 1 Bromcom, 1 Parkingeye, 2 Alstom, 5 Woods, listed
here by exact batch/run/round path so this claim is checkable without re-deriving it:

  1. Bromcom     batch_results/batch_20260816_165719/run_03.json   round 1
  2. Parkingeye  batch_results/batch_20260815_221124/run_06.json   round 1
  3. Alstom      batch_results/batch_20260819_205553/run_06.json   round 2
  4. Alstom      batch_results/batch_20260819_205553/run_06.json   round 3
  5. Woods       batch_results/batch_20260819_211359/run_06.json   round 1
  6. Woods       batch_results/batch_20260819_211359/run_07.json   round 1
  7. Woods       batch_results/batch_20260819_213346/run_05.json   round 1
  8. Woods       batch_results/batch_20260819_213346/run_07.json   round 1
  9. Woods       batch_results/batch_20260819_213346/run_11.json   round 1

(Entry 4's path was misattributed in an earlier draft of this note to `batch_20260819_211359/run_07.json`
— that path is actually a Woods batch, not Alstom; corrected 5 Sep 2026 after verifying scenario_id
directly against each batch_summary.json rather than trusting the earlier note.)

**5 of these 9 are on Woods, all under the active V4 Court prompt, all from batches dated 19 August** —
after the 15 August Step 1 gating fix (commit 329848e) this project's own history (CLAUDE.md, this
docstring's own "RESULT OF THAT HUMAN READ" note above) describes as having closed exactly this failure
mode. It has recurred: one instance (`batch_20260819_213346/run_07.json` round 1) contains the almost
verbatim banned phrase — "let's assume the original scores were not provided... a hypothetical score of
60 for EAS and 40 for Woods." This does not contradict the narrower claim that the original 16 post-fix
runs it was measured against were clean; it does mean "the Step 1 fix closed this failure mode" cannot be
cited as an unqualified, permanent claim going forward.

In every one of these 9 instances, the fabrication is INVENTED INPUT NUMBERS with subsequently CORRECT
arithmetic — not incorrect arithmetic. Bromcom and Parkingeye invent a bare declarative dataset with no
formula behind it at all; the Alstom and Woods instances invent a numeric baseline (e.g. "Price = 80%,
Quality = 90%") and then correctly execute the real, stated formula on it (e.g. Woods:
`(0.6 * 85) + (0.4 * 92) = 87.8` — flawless arithmetic on numbers nobody supplied). This means a reader
checking only "is the maths right" would find nothing wrong in any of these 9 cases; the fabrication is
entirely upstream of the arithmetic, in the inputs the Court invented for itself.

Alstom round 3 (`batch_results/batch_20260819_205553/run_06.json` round 3) additionally has a known,
accepted screening gap: it invents a full six-criterion sub-score breakdown ("design and development (15
points)... = 14/15") for a case whose real record has no such breakdown at all. The round IS flagged, but
only via its fabricated point-weights ("15 points" etc., caught by the existing points branch as a
free-standing ungrounded number) — the specific "14/15"-style achieved-score fractions are not, because
their labels ("design and development") exceed _LABEL_NUMBER's length cap and their values aren't the
bare 1-3-digit form that branch targets. Not silently patched by widening scope beyond what a bare-number,
no-unit form covers.

The remaining 1 numeric-branch suspect (Alstom, `batch_results/batch_20260815_192629/run_01.json` round
2, V3) and all 9 qualitative-branch suspects are NOT counted above: read individually, each is the Court
citing a number the CA/Bidder stated in dialogue and explicitly declining to treat it as independently
verified fact — the same pre-existing upstream CA/Bidder-fabrication pattern documented in the "RESULT OF
THAT HUMAN READ" note above, not a new Court-originated instance.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Markers indicating the Court agent classified this round as Step 2B / qualitative — checked against
# the actual phrasing this project's prompts and observed outputs use (court_prompt.py's own Step 2B
# language, plus the phrasings seen across the corpus while building this script).
_QUALITATIVE_MARKERS = re.compile(
    r"\b(step 2b|this scenario is qualitative|scenario is qualitative|assess.{0,20}qualitatively|"
    r"no explicit formula|without explicit (numbers|formula)|no stated (formula|points system))\b",
    re.I,
)

# Markers indicating Step 2A / numeric — a round matching both is ambiguous and excluded rather than
# guessed at (see _classify below).
_NUMERIC_MARKERS = re.compile(
    r"\b(step 2a|this scenario is numeric|scenario is numeric)\b", re.I,
)

# Score-shaped numbers: "NN%", "NN/100", "score of NN", "NN points". Deliberately narrow — a contract
# value ("£2,000,000"), a section number ("s12(1)(a)"), or a round/date is not score-shaped and must
# not match, or every reasoning text would trip this regardless of qualitative-vs-numeric context.
_SCORE_NUMBER = re.compile(
    # NB: the first branch deliberately has NO trailing \b — % and the closing digit of "/100" are
    # non-word characters, so a \b immediately after either can never match ordinary text (a \b
    # requires a word/non-word transition, and "% " or "%<end>" is non-word on both sides). An earlier
    # version had this bug and silently missed every bare "NN%" not preceded by the word "score(d)" —
    # caught only by testing extraction against real text with two percentages, not by inspection.
    r"\b(\d{1,3})\s*(?:%|/\s*100)"
    r"|\bscored?\s+(?:a\s+|an?\s+)?(?:of\s+)?(\d{1,3})\b"
    r"|\b(\d{1,3})\s*points?\b",
    re.I,
)

# Fourth branch, added 4 Sep 2026: a bare "A=80" / "Bidder 1: 80" declaration with no unit at all — the
# exact shape of the Bromcom fabrication ("Bidder 1: A=80, B=70, C=90"), which the three branches above
# could never have matched since none of them require a % sign, "/100", "score(d)", or "points".
#
# WHAT THIS MATCHES: a short label (a single letter, or a letter followed by up to 20 more
# letters/digits/spaces — "A", "Bidder 1", "Criterion B") directly followed by ":" or "=" and then 1-3
# digits with nothing else attached.
#
# WHAT THIS DELIBERATELY DOES NOT MATCH, and why — each of these is rejected by
# _is_citation_or_date_context() below, checked against the matched label AFTER the regex runs, rather
# than folded into the regex itself (a citation-shaped negative lookbehind would need to enumerate every
# citation style and would still miss new ones; checking the actual captured label text is easier to
# read and to extend):
#   - "s12(1)(a)" / "s.12" / "section 12: 84" / "sec 51: 84" — a label that IS a section/paragraph
#     reference, in full or abbreviated form, with or without a trailing period.
#   - "Act 2023: 84" / "the 2018 judgment: 84" — a 4-digit year sitting inside the label, or in the
#     few characters immediately before it, reads as a dated citation, not a score.
#   - a bare 4-digit run ("2023") is already excluded by construction, not by the citation check: \b at
#     the end of \d{1,3} can never satisfy inside a longer digit run, since the boundary test fails
#     while a further digit still follows.
#
# WHAT IT DOES NOT GUARD AGAINST (known gap, same screening-tool posture as the rest of this file): a
# label that is neither a citation nor near a year but still isn't a score — e.g. "Clause: 84" or
# "Item 3: 84" — will be extracted and is then subject to the normal grounding check like any other
# candidate number. It also does not cover a label longer than ~21 characters (multi-word criterion
# names like "design and development") or a fraction-shaped value ("14/15") — see the module docstring's
# "RESULT OF RE-SCREENING" note for a real corpus instance (Alstom round 3) this specifically misses.
_LABEL_NUMBER = re.compile(r"\b([A-Za-z][A-Za-z0-9 ]{0,20})\s*[:=]\s*(\d{1,3})\b")

_CITATION_LABEL = re.compile(r"^s(ec(tion)?)?\.?\s*\d+$", re.I)
_YEAR_NEARBY = re.compile(r"(19|20)\d{2}")

# Finds "<expression> = <result>" spans for the numeric-round check below (79-65=14, (80+85+92)/3 =
# 85.67, (92 x 0.4) = 36.8). Deliberately only requires the expression START with a digit, not end with
# one — an earlier draft required both ends to be digits and silently failed to match any expression
# wrapped in parentheses, since the closing ")" sits between the last digit and "=".
_ARITHMETIC_EQUATION = re.compile(r"(\d[\d\s+\-*/().xX×]*)\s*=\s*(\d+(?:\.\d+)?)")
_NUMBER_IN_EXPR = re.compile(r"\d+(?:\.\d+)?")


def _is_citation_or_date_context(label: str, preceding_text: str) -> bool:
    """True if a _LABEL_NUMBER match looks like a section/paragraph citation or a dated reference
    rather than a score. See _LABEL_NUMBER's own comment for exactly what this does and doesn't cover."""
    label_stripped = label.strip()
    if _CITATION_LABEL.match(label_stripped):
        return True
    if "section" in label_stripped.lower():
        return True
    if _YEAR_NEARBY.search(label_stripped):
        return True
    # A handful of characters immediately before the label, to catch "...Act 2023: 84" where the year
    # sits just outside the captured label rather than inside it.
    if _YEAR_NEARBY.search(preceding_text[-15:]):
        return True
    return False


def _classify(reasoning: str) -> str:
    """'qualitative' / 'numeric' / 'ambiguous_or_neither' — never guess between the first two."""
    is_qual = bool(_QUALITATIVE_MARKERS.search(reasoning))
    is_num = bool(_NUMERIC_MARKERS.search(reasoning))
    if is_qual and not is_num:
        return "qualitative"
    if is_num and not is_qual:
        return "numeric"
    return "ambiguous_or_neither"


def _extract_score_numbers(text: str) -> set[str]:
    out = set()
    for m in _SCORE_NUMBER.finditer(text):
        out.add(next(g for g in m.groups() if g is not None))
    for m in _LABEL_NUMBER.finditer(text):
        label, number = m.group(1), m.group(2)
        if _is_citation_or_date_context(label, text[:m.start()]):
            continue
        out.add(number)
    return out


def _number_grounded(number: str, description: str) -> bool:
    """Is this number, or a plausible reformatting of it, actually present in the scenario record?"""
    if number in description:
        return True
    # Tolerate "NN%" being cited as bare "NN" in the description or vice versa, and "NN/100" as "NN".
    return re.search(rf"\b{re.escape(number)}\b", description) is not None


def _numeric_round_ungrounded(reasoning: str, description: str) -> set[str]:
    """
    The equivalent of "which numbers are fabricated" for a Step 2A / numeric round, where a plain
    string-presence check on every extracted number is the wrong test — see the module docstring's
    "WIDENED 4 Sep 2026" note for why. A correctly-derived result ("84 - 68 = 16") is not itself
    required to be grounded; its OWN INPUTS are. A number with no arithmetic behind it at all (a bare
    declaration like Bromcom's "Bidder 1: A=80, B=70, C=90") is checked exactly like the qualitative
    path always has been: flagged if it doesn't appear in the scenario.
    """
    input_nums, result_nums = set(), set()
    for m in _ARITHMETIC_EQUATION.finditer(reasoning):
        input_nums.update(_NUMBER_IN_EXPR.findall(m.group(1)))
        result_nums.add(m.group(2))

    ungrounded = {n for n in input_nums if not _number_grounded(n, description)}

    for n in _extract_score_numbers(reasoning):
        if n in result_nums or n in input_nums:
            continue  # already decided one way or the other above
        if not _number_grounded(n, description):
            ungrounded.add(n)

    return ungrounded


def iter_negotiation_logs():
    for p in sorted(REPO_ROOT.glob("negotiation_log_*.json")):
        try:
            yield str(p.relative_to(REPO_ROOT)), json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  SKIP {p}: {e}", file=sys.stderr)
    for batch_dir in sorted((REPO_ROOT / "batch_results").glob("batch_*")):
        for run_file in sorted(batch_dir.glob("run_*.json")):
            try:
                yield str(run_file.relative_to(REPO_ROOT)), json.loads(run_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                print(f"  SKIP {run_file}: {e}", file=sys.stderr)


def analyze(verbose: bool = False) -> dict:
    counts = Counter()
    suspects = []
    n_logs = 0

    for source, log in iter_negotiation_logs():
        n_logs += 1
        description = (log.get("scenario") or {}).get("description", "")
        for check in log.get("compliance_checks", []):
            reasoning = check.get("reasoning", "") or ""
            cls = _classify(reasoning)
            counts[cls] += 1

            if cls == "qualitative":
                numbers = _extract_score_numbers(reasoning)
                ungrounded = {n for n in numbers if not _number_grounded(n, description)}
            elif cls == "numeric":
                # Widened 4 Sep 2026 — numeric-classified rounds used to be skipped entirely (see
                # the module docstring). Uses a different check from the qualitative path: only an
                # equation's own INPUTS are required to be grounded, never a correctly-derived
                # result. See _numeric_round_ungrounded's docstring.
                ungrounded = _numeric_round_ungrounded(reasoning, description)
            else:
                continue  # ambiguous_or_neither: never guessed at, same as before

            if ungrounded:
                counts[f"{cls}_with_fabrication_suspect"] += 1
                entry = {
                    "source": source, "round": check.get("round_number"), "classification": cls,
                    "ungrounded_numbers": sorted(ungrounded), "reasoning": reasoning,
                }
                suspects.append(entry)
                if verbose:
                    print(f"[SUSPECT:{cls}] {source} r{check.get('round_number')}: {sorted(ungrounded)}")
                    print(f"  {reasoning[:300]}")

    n_qual = counts["qualitative"]
    n_num = counts["numeric"]
    n_qual_suspect = counts["qualitative_with_fabrication_suspect"]
    n_num_suspect = counts["numeric_with_fabrication_suspect"]
    n_suspect = n_qual_suspect + n_num_suspect
    n_screened = n_qual + n_num
    return {
        "n_logs_scanned": n_logs,
        "counts": dict(counts),
        # Kept for direct before/after comparison against the pre-4-Sep-2026 figure (9/425 = 0.0212):
        # qualitative population only, qualitative check only.
        "qualitative_fabrication_rate": round(n_qual_suspect / n_qual, 4) if n_qual else None,
        # New 4 Sep 2026: numeric population, using the input-grounding check (see
        # _numeric_round_ungrounded). This population was entirely unscreened before.
        "numeric_fabrication_rate": round(n_num_suspect / n_num, 4) if n_num else None,
        # The headline figure going forward: both screened populations combined.
        "combined_screened_fabrication_rate": round(n_suspect / n_screened, 4) if n_screened else None,
        "n_screened": n_screened,
        "suspects": suspects,
        "method_note": (
            "Ground truth is scenario.description (the authored/verified case record), not the "
            "negotiation dialogue — chosen specifically because CA/Bidder agents have been observed "
            "fabricating factual premises themselves (see the Faraday finding in "
            "evaluation-five-cases.md), so checking against dialogue would let a Court citation pass "
            "by uncritically repeating another agent's fabrication. Screening tool: false negatives "
            "expected (semantic fabrication using a number that happens to appear elsewhere in the "
            "description won't be caught); every listed suspect is worth a human read. As of 4 Sep "
            "2026, numeric-classified rounds are screened too, using a different check: only an "
            "equation's own inputs are required to be grounded, never a correctly-derived result — "
            "see _numeric_round_ungrounded's docstring."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    result = analyze(verbose=args.verbose)

    print(f"\n{'='*70}")
    print("  FABRICATION SCREEN — Step 2B (qualitative) + Step 2A (numeric, widened 4 Sep 2026)")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']}")
    for k, v in result["counts"].items():
        print(f"  {k}: {v}")
    print(f"\nScreened population (qualitative + numeric): {result['n_screened']}")
    print(f"Qualitative fabrication rate : {result['qualitative_fabrication_rate']}")
    print(f"Numeric fabrication rate     : {result['numeric_fabrication_rate']}")
    print(f"Combined fabrication rate    : {result['combined_screened_fabrication_rate']}")

    if result["suspects"]:
        print(f"\n{len(result['suspects'])} suspect(s):")
        for s in result["suspects"][:15]:
            print(f"  - [{s['classification']}] {s['source']} r{s['round']}: ungrounded {s['ungrounded_numbers']}")
        if len(result["suspects"]) > 15:
            print(f"  ... and {len(result['suspects']) - 15} more (see --json output)")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
