"""
Citation validity analysis — evaluation item 15. Walks every ComplianceAssessment
across the log corpus and checks whether Court.applicable_provisions cites law that
actually exists, and cites it correctly.

WHY THIS MATTERS: this project's central finding is that the Court agent must not
fabricate arithmetic. Legal citation is the same failure mode applied to a different
field — a citation that names the wrong regime, or misdescribes what a real section
says, is exactly as fabricated as an invented formula, and just as capable of
poisoning a downstream recommendation. Cheap to check because the data is already
logged (no new LLM calls) — same shape as analyze_batna_outcomes.py.

WHAT IS VERIFIED HERE, AND HOW — every claim this script checks against was verified
via WebSearch on 15 Aug 2026, not assumed:

1. **Regime.** The whole project (CLAUDE.md) is explicitly grounded in the Procurement
   Act 2023, which REPLACED the Public Contracts Regulations 2015 and the underlying
   EU Directive 2014/24/EU for procurements it covers. A citation to PCR2015 or the EU
   Directive in this project's world is citing law that is no longer the operative
   regime for these scenarios — this is checkable with high confidence regardless of
   the citation's internal accuracy.

2. **s12 structure**, per legislation.gov.uk (Procurement Act 2023, s12, "Covered
   procurement: objectives" — verified in full 15 Aug 2026):
     s12(1)(a) — delivering value for money
     s12(1)(b) — maximising public benefit
     s12(1)(c) — sharing information for transparency (NOT integrity)
     s12(1)(d) — acting, and being seen to act, with integrity
     s12(2)    — treat suppliers the same unless a difference justifies otherwise
                 (equal treatment — NOT value for money or public benefit)
   This project's own agent prompts (ca_prompt.py) already state the four s12(1)
   objectives correctly. What this script checks is whether the Court agent's
   *citations* — a separate generation, not copied from the prompt — get the
   subsection numbering right when it references them.

DELIBERATELY NARROW SCOPE: this checks the two things verified above with high
confidence — wrong-regime citation, and s12 structural correctness. It does NOT
attempt to validate every possible citation (Framework Document references, s51
standstill, Part 9 remedies, etc.) because those haven't all been independently
verified against source; a "not_specific_enough_to_check" bucket exists for exactly
that content rather than silently passing it as correct.

Usage:
    python scripts/analyze_citation_validity.py
    python scripts/analyze_citation_validity.py --verbose
    python scripts/analyze_citation_validity.py --json out.json
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_WRONG_REGIME = re.compile(
    r"\b(public contracts regulations|pcr\s*2015|eu (procurement )?directive|"
    r"2014/24/eu|regulation 8[46])\b", re.I,
)

# The real s12(1) limb each letter maps to, per legislation.gov.uk (verified above).
_REAL_S12_1 = {"a": "value for money", "b": "public benefit", "c": "transparency", "d": "integrity"}

_S12_CITE = re.compile(r"s\.?\s*12\s*\(\s*(1|2)\s*\)(?:\s*\(\s*([a-d])\s*\))?", re.I)

# What topic word in the citation text implies which real limb, for cross-checking
# a cited subsection letter against what the citation actually claims it says.
_TOPIC_WORDS = {
    "value for money": "a",
    "public benefit": "b",
    "transparency": "c",
    "sharing information": "c",
    "integrity": "d",
}


def classify(citation: str) -> tuple[str, str]:
    """Returns (bucket, detail). Buckets: wrong_regime, s12_correct, s12_incorrect,
    not_specific_enough_to_check."""
    if _WRONG_REGIME.search(citation):
        return "wrong_regime", citation

    m = _S12_CITE.search(citation)
    if m:
        subsection, letter = m.group(1), m.group(2)
        if subsection == "2":
            # Real s12(2) is equal treatment. Any citation attaching s12(2) to a
            # value-for-money/public-benefit/transparency/integrity topic word is
            # citing the wrong subsection for what it claims.
            lowered = citation.lower()
            if any(topic in lowered for topic in _TOPIC_WORDS if topic != "equal treatment"):
                if "equal treatment" not in lowered and "same" not in lowered:
                    return "s12_incorrect", f"s12(2) is equal treatment, not: {citation}"
            return "s12_correct", citation
        if letter:
            letter = letter.lower()
            lowered = citation.lower()
            claimed_topic = next((topic for topic, l in _TOPIC_WORDS.items() if l == letter), None)
            # Does the citation's own topic word match what that letter really means?
            for topic, real_letter in _TOPIC_WORDS.items():
                if topic in lowered and real_letter != letter:
                    return "s12_incorrect", f"s12(1)({letter}) mislabelled as '{topic}' (real: {_REAL_S12_1[real_letter]}): {citation}"
            return "s12_correct", citation
        return "s12_correct", citation  # bare "s12(1)" or "s12" with no specific limb claimed

    return "not_specific_enough_to_check", citation


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
    flagged = defaultdict(list)  # bucket -> [{source, round, citation}]
    n_logs = 0
    n_citations = 0

    for source, log in iter_negotiation_logs():
        n_logs += 1
        for check in log.get("compliance_checks", []):
            for citation in check.get("applicable_provisions", []) or []:
                n_citations += 1
                bucket, detail = classify(citation)
                counts[bucket] += 1
                if bucket in ("wrong_regime", "s12_incorrect"):
                    entry = {"source": source, "round": check.get("round_number"), "citation": citation, "detail": detail}
                    flagged[bucket].append(entry)
                    if verbose:
                        print(f"[{bucket}] {source} r{check.get('round_number')}: {detail}")

    return {
        "n_logs_scanned": n_logs,
        "n_citations_seen": n_citations,
        "counts": dict(counts),
        "wrong_regime_rate": round(counts["wrong_regime"] / n_citations, 4) if n_citations else None,
        "s12_error_rate": (
            round(counts["s12_incorrect"] / (counts["s12_correct"] + counts["s12_incorrect"]), 4)
            if (counts["s12_correct"] + counts["s12_incorrect"]) else None
        ),
        "flagged": {k: v for k, v in flagged.items()},
        "method_note": (
            "Checks two independently-verified facts (15 Aug 2026, via WebSearch against "
            "legislation.gov.uk): (1) PCR2015/EU Directive citations are wrong-regime for "
            "this project's Procurement Act 2023 world; (2) real s12 structure, so a "
            "citation attaching the wrong topic to a subsection letter is flagged. Does "
            "NOT validate citations outside s12 (Framework Document refs, s51, Part 9, "
            "etc.) — those fall into not_specific_enough_to_check rather than being "
            "silently treated as correct."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    result = analyze(verbose=args.verbose)

    print(f"\n{'='*70}")
    print("  CITATION VALIDITY ANALYSIS")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']}")
    print(f"Citations seen: {result['n_citations_seen']}")
    print()
    for bucket, n in sorted(result["counts"].items(), key=lambda kv: -kv[1]):
        pct = f"{100*n/result['n_citations_seen']:.1f}%" if result["n_citations_seen"] else "—"
        print(f"  {bucket:32s} {n:4d}  ({pct})")
    print()
    print(f"Wrong-regime rate (PCR2015/EU Directive cited in a PA2023-only world): {result['wrong_regime_rate']}")
    print(f"s12 citation error rate (of citations that reference s12 specifically): {result['s12_error_rate']}")

    for bucket, entries in result["flagged"].items():
        print(f"\n{len(entries)} {bucket} citation(s):")
        for e in entries[:15]:
            print(f"  - {e['source']} r{e['round']}: {e['citation']!r}")
        if len(entries) > 15:
            print(f"  ... and {len(entries) - 15} more (see --json output)")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
