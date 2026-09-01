"""Outcome-leakage audit: does the scenario tell the agents the answer?

Raised by the supervisor on the v1 draft: is there any pre-processing that strips
the real court result from the input, so the simulated negotiation is not biased
by the disposition it is being scored against?

There is not. The real-case source texts in src/cases/real_cases.py are written as
complete case summaries, and for some cases the extraction agent carries the
disposition through into scenario.description - the field that is inserted verbatim
into every agent's system prompt. Worse, court_prompt.py contains an explicit
instruction (GROUNDING AGAINST A STATED REAL OUTCOME) telling the Court agent that
its recommended_action "must not end up contradicting an outcome the scenario itself
already tells you occurred".

Those two facts together mean an agreement figure computed over all merits cases is
not a figure about independent prediction. This script splits the corpus into the
leaked and leak-free subsets and reports agreement separately for each, so the
defensible number can be quoted instead.

Detection is a deliberately broad regex over scenario.description. It errs toward
calling a scenario leaked: a false "leaked" only shrinks the clean subset the
headline claim rests on, whereas a false "clean" would inflate that claim.

Run:  python scripts/analyze_outcome_leakage.py
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The 14 cases with a genuine merits disposition, and what the real court held.
# "lost" = the authority lost, a remedy was granted. Interim-only cases are absent
# by design: there is no merits disposition to compare a merits prediction against.
MERITS_TRUTH = {
    "lancashire-care": "lost",
    "faraday-west-berkshire": "lost",
    "woods-milton-keynes": "lost",
    "braceurself-nhs-england": "lost",
    "bromcom-united-learning-trust": "lost",
    "energysolutions-nda": "lost",
    "consultant-connect-nhs-banes": "lost",
    "optima-health-dwp": "lost",
    "abbvie-nhs-england": "won",
    "bechtel-hs2": "won",
    "inhealth-nhs-england": "won",
    "turning-point-norfolk": "won",
    "siemens-mobility-hs2": "won",
    "tnlc-gambling-commission": "won",
}

_LEAK = re.compile(
    r"(the court (found|held|ruled|ordered|dismissed|concluded|rejected|allowed)"
    r"|court of appeal"
    r"|judge (found|held|ruled)"
    r"|was (upheld|dismissed|allowed)"
    r"|declaration of ineffectiveness|declaring its ineffectiveness"
    r"|damages were awarded"
    r"|claim (was )?dismissed"
    r"|found in favour"
    r"|ultimately lost|reversed on appeal"
    r"|should have been awarded)",
    re.I,
)

# recommended_action -> which party the simulation came down on
_REMEDY = {"re-evaluation", "damages"}
_NO_REMEDY = {"no remedy - decision stands"}


def leak_sentences(description: str):
    out = []
    for sent in re.split(r"(?<=\.)\s+", description):
        if _LEAK.search(sent):
            out.append(sent.strip())
    return out


def simulated_direction(outcome: str):
    if not outcome:
        return None
    o = outcome.strip().lower()
    if o in _REMEDY:
        return "lost"
    if o in _NO_REMEDY:
        return "won"
    return None  # deadlock, disclosure, or anything outside the merits vocabulary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true", help="print the leaking sentences")
    args = ap.parse_args()

    scen_dir = REPO_ROOT / "batch_results" / "_scenarios"
    leaked, clean, missing = {}, {}, []
    for slug in MERITS_TRUTH:
        p = scen_dir / f"{slug}.json"
        if not p.exists():
            missing.append(slug)
            continue
        desc = json.loads(p.read_text(encoding="utf-8")).get("description", "")
        sents = leak_sentences(desc)
        (leaked if sents else clean)[slug] = sents

    # Map slug -> dispute_id from the corpus itself rather than guessing from the
    # slug: "lancashire-care" carries dispute_id REAL-LANCS-2018, so a prefix match
    # silently drops that case's runs and reports it as unmeasured.
    sys.path.insert(0, str(REPO_ROOT))
    from src.cases.real_cases import REAL_CASES
    id_to_slug = {REAL_CASES[s]["dispute_id"].upper(): s
                  for s in MERITS_TRUTH if s in REAL_CASES}

    votes = defaultdict(list)
    for run in sorted((REPO_ROOT / "batch_results").glob("batch_*/run_*.json")):
        try:
            d = json.loads(run.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        sid = str(d.get("scenario", {}).get("dispute_id", "")).upper()
        slug = id_to_slug.get(sid)
        if slug:
            dirn = simulated_direction(d.get("resolution_outcome"))
            if dirn:
                votes[slug].append(dirn)

    def agreement(subset):
        ok = total = 0
        rows = []
        for slug in subset:
            v = votes.get(slug, [])
            if not v:
                rows.append((slug, MERITS_TRUTH[slug], "no runs", "-"))
                continue
            modal = max(set(v), key=v.count)
            hit = modal == MERITS_TRUTH[slug]
            ok += hit
            total += 1
            rows.append((slug, MERITS_TRUTH[slug],
                         f"{modal} ({v.count(modal)}/{len(v)})",
                         "correct" if hit else "WRONG"))
        return ok, total, rows

    print("=" * 78)
    print("  OUTCOME LEAKAGE AUDIT - does the scenario state the answer?")
    print("=" * 78)
    if missing:
        print(f"  no cached scenario for: {', '.join(missing)}\n")

    for name, subset in (("LEAKED - description states the real disposition", leaked),
                         ("LEAK-FREE - description states facts only", clean)):
        ok, total, rows = agreement(subset)
        print(f"\n{name}  ({len(subset)} cases)")
        for slug, truth, modal, verdict in rows:
            print(f"    {slug:32s} real={truth:5s} simulated={modal:22s} {verdict}")
        if total:
            print(f"    -> agreement {ok}/{total}")
        if args.verbose:
            for slug in subset:
                for s in subset[slug]:
                    print(f"       [{slug}] {s[:150]}")

    ok_l, tot_l, _ = agreement(leaked)
    ok_c, tot_c, _ = agreement(clean)
    print("\n" + "-" * 78)
    print(f"  Combined       : {ok_l + ok_c}/{tot_l + tot_c}")
    print(f"  Leak-free only : {ok_c}/{tot_c}   <- the defensible figure")
    print(f"  Leaked         : {ok_l}/{tot_l}   <- the Court was told, and instructed not to contradict")
    print("-" * 78)
    print("\nNote: court_prompt.py's GROUNDING AGAINST A STATED REAL OUTCOME block")
    print("instructs the Court agent not to contradict a disposition the scenario")
    print("states, so agreement on the leaked subset is partly compliance, not")
    print("prediction. Quote the leak-free figure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
