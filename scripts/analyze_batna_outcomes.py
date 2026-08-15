"""
BATNA-outcome analysis — Layer 1 per-agent evaluation, item 18 on the evaluation punch
list. Walks every saved negotiation log and reports how each party's stated outcome
compares to the BATNA it declared at the start of the same negotiation.

WHY THIS IS CHEAP: PreNegotiationStatement.batna and WinStatement.outcome_relative_to_batna
are already logged by every run (src/schemas/agent_state.py). No new LLM calls, no new
negotiations — this is pure analysis over data that already exists on disk.

WHAT THIS DOES NOT MEASURE — read before citing this anywhere:

`outcome_relative_to_batna` is free text, not a structured field, so classification here
is a transparent KEYWORD HEURISTIC, not a ground-truth label. It sorts each statement into
beats / matches / falls_short / unclear based on the words the agent itself used to
describe its own outcome. This is NOT the same as "irrationality" in the game-theoretic
sense (accepting a deal worse than walking away to your no-agreement alternative) — this
pipeline has no explicit walk-away action separate from the Court's ruling, so that
stronger claim isn't measurable from this data. What IS measurable, and reported here
honestly under that name, is: how often does an agent's own self-reported outcome fall
short of the BATNA it declared for itself. That's a real signal (a well-behaved agent
should rarely report this), but every "falls_short" case should be spot-read before
being cited as a defect, not taken as proof of one — a badly-behaved CA that stonewalled
and still ended up with a bad outcome deserves a "falls_short" as much as one that
negotiated in good faith and just had a weak hand.

Usage:
    python scripts/analyze_batna_outcomes.py                    # scan everything
    python scripts/analyze_batna_outcomes.py --verbose           # print flagged text
    python scripts/analyze_batna_outcomes.py --json out.json     # machine-readable dump
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered so a statement that hedges ("matched, if not slightly below") lands on the
# more cautious bucket — check falls_short before beats.
_PATTERNS = [
    # "did not (meet|achieve)" was originally unanchored and matched hedges like
    # "we did not achieve a full win" even when the surrounding statement was net
    # positive against BATNA (caught by manual spot-check on the Faraday CA log —
    # see git history for the false-positive this replaced). Anchored to the
    # batna/outcome comparison specifically rather than any negative achievement.
    ("falls_short", re.compile(
        r"\b(fell short of|falls short of|worse than (our|their|its) batna|"
        r"below (our|their|its) batna|did not (meet|achieve) (our|their|its) batna|"
        r"failed to (meet|achieve) (our|their|its) batna|"
        r"less favou?rable than (our|their|its) batna|"
        r"underperformed (our|their|its) batna|did not beat (our|their|its) batna|"
        # "unfavourable [...] compared to/than my BATNA" — degree qualifiers
        # ("slightly", "somewhat") between the adjective and BATNA are common,
        # hence the [^.]{0,40} gap rather than requiring adjacency.
        r"un-?favou?rable[^.]{0,40}(compared to|than) (our|their|its|my) batna)\b", re.I)),
    ("beats", re.compile(
        r"\b(beat(s)? (our|their|its) batna|exceeded (our|their|its) batna|"
        r"better than (our|their|its) batna|more favou?rable than (our|their|its) batna|"
        r"outperformed (our|their|its) batna|surpassed (our|their|its) batna|"
        r"above (our|their|its) batna|"
        # positive "favourable" is only unambiguous once "un-" is ruled out —
        # the falls_short pattern above is checked first, so this is safe.
        r"(?<!un)(?<!un-)favou?rable[^.]{0,40}(compared to|than) (our|their|its|my) batna)\b", re.I)),
    ("matches", re.compile(
        r"\b(matched (our|their|its) batna|matches (our|their|its) batna|"
        r"in line with (our|their|its) batna|consistent with (our|their|its) batna|"
        r"comparable to (our|their|its) batna|roughly equivalent to (our|their|its) batna|"
        r"on par with (our|their|its) batna|acceptable relative to (our|their|its) batna)\b", re.I)),
]


def classify(text: str) -> str:
    if not text:
        return "unclear"
    for label, pattern in _PATTERNS:
        if pattern.search(text):
            return label
    return "unclear"


def iter_negotiation_logs():
    """Yields (source_label, parsed_json) for every negotiation log on disk."""
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
    counts = defaultdict(Counter)  # role -> {beats, matches, falls_short, unclear}
    flagged = []  # falls_short cases, for manual review
    n_logs = 0
    n_missing_win_statements = 0

    for source, log in iter_negotiation_logs():
        n_logs += 1
        any_statement = False
        for role_key, role_label in (("ca_win_statement", "contracting_authority"),
                                      ("bidder_win_statement", "aggrieved_bidder")):
            stmt = log.get(role_key)
            if not stmt or not stmt.get("outcome_relative_to_batna"):
                continue
            any_statement = True
            text = stmt["outcome_relative_to_batna"]
            label = classify(text)
            counts[role_label][label] += 1
            if label == "falls_short":
                flagged.append({"source": source, "role": role_label, "text": text})
                if verbose:
                    print(f"[falls_short] {source} ({role_label}): {text}")

        if not any_statement:
            n_missing_win_statements += 1

    return {
        "n_logs_scanned": n_logs,
        "n_logs_without_win_statements": n_missing_win_statements,
        "by_role": {role: dict(c) for role, c in counts.items()},
        "falls_short_cases": flagged,
        "method_note": (
            "Keyword-heuristic classification of free-text WinStatement.outcome_relative_to_batna "
            "against the same run's declared PreNegotiationStatement.batna context. Not a "
            "ground-truth label — see this script's module docstring before citing."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true", help="print each falls_short case as it's found")
    ap.add_argument("--json", metavar="PATH", help="write the full result as JSON to this path")
    args = ap.parse_args()

    result = analyze(verbose=args.verbose)

    print(f"\n{'='*70}")
    print("  BATNA-OUTCOME ANALYSIS")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']}")
    print(f"Logs with no win statement (deadlock/failed run): {result['n_logs_without_win_statements']}")
    print()
    for role, dist in result["by_role"].items():
        total = sum(dist.values())
        print(f"{role} (n={total}):")
        for label in ("beats", "matches", "falls_short", "unclear"):
            n = dist.get(label, 0)
            pct = f"{100*n/total:.0f}%" if total else "—"
            print(f"    {label:12s} {n:3d}  ({pct})")
        print()

    if result["falls_short_cases"]:
        print(f"{len(result['falls_short_cases'])} falls_short case(s) — review before citing as a defect:")
        for c in result["falls_short_cases"]:
            print(f"  - {c['source']} ({c['role']})")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
