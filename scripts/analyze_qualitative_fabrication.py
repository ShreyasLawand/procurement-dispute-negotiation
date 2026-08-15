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
    return out


def _number_grounded(number: str, description: str) -> bool:
    """Is this number, or a plausible reformatting of it, actually present in the scenario record?"""
    if number in description:
        return True
    # Tolerate "NN%" being cited as bare "NN" in the description or vice versa, and "NN/100" as "NN".
    return re.search(rf"\b{re.escape(number)}\b", description) is not None


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
            if cls != "qualitative":
                continue
            numbers = _extract_score_numbers(reasoning)
            ungrounded = [n for n in numbers if not _number_grounded(n, description)]
            if ungrounded:
                counts["qualitative_with_fabrication_suspect"] += 1
                entry = {
                    "source": source, "round": check.get("round_number"),
                    "ungrounded_numbers": sorted(ungrounded), "reasoning": reasoning,
                }
                suspects.append(entry)
                if verbose:
                    print(f"[SUSPECT] {source} r{check.get('round_number')}: {ungrounded}")
                    print(f"  {reasoning[:300]}")

    n_qual = counts["qualitative"]
    n_suspect = counts["qualitative_with_fabrication_suspect"]
    return {
        "n_logs_scanned": n_logs,
        "counts": dict(counts),
        "qualitative_fabrication_rate": round(n_suspect / n_qual, 4) if n_qual else None,
        "suspects": suspects,
        "method_note": (
            "Ground truth is scenario.description (the authored/verified case record), not the "
            "negotiation dialogue — chosen specifically because CA/Bidder agents have been observed "
            "fabricating factual premises themselves (see the Faraday finding in "
            "evaluation-five-cases.md), so checking against dialogue would let a Court citation pass "
            "by uncritically repeating another agent's fabrication. Screening tool: false negatives "
            "expected (semantic fabrication using a number that happens to appear elsewhere in the "
            "description won't be caught); every listed suspect is worth a human read."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    result = analyze(verbose=args.verbose)

    print(f"\n{'='*70}")
    print("  QUALITATIVE (STEP 2B) FABRICATION SCREEN")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']}")
    for k, v in result["counts"].items():
        print(f"  {k}: {v}")
    print(f"\nQualitative fabrication rate: {result['qualitative_fabrication_rate']}")

    if result["suspects"]:
        print(f"\n{len(result['suspects'])} suspect(s):")
        for s in result["suspects"][:15]:
            print(f"  - {s['source']} r{s['round']}: ungrounded numbers {s['ungrounded_numbers']}")
        if len(result["suspects"]) > 15:
            print(f"  ... and {len(result['suspects']) - 15} more (see --json output)")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
