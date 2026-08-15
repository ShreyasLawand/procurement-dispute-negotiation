"""
Negotiation dynamics — evaluation punch-list items 19 (concession monotonicity / convergence) and 20
(stagnation / repetition), combined into one script since both walk the same per-round message data.

Pure analysis over already-logged data (NegotiationMessage.concession_made, .proposal, .message), no
new LLM calls — same posture as the other analyze_*.py scripts in this directory.

WHAT "MONOTONICITY" MEANS HERE, AND ITS LIMITS: a genuine semantic check ("did round 3's proposal
actually retract what round 1 conceded") would need an LLM judge — out of scope for a free/no-new-calls
pass. What's implemented instead is a narrow, high-precision, low-recall check: does a later round's
message contain explicit retraction language ("withdraw", "retract", "rescind", "no longer offer/stand
by") referring back to an earlier concession from the SAME role. This catches only EXPLICIT reversals,
not implicit backsliding — reported honestly as a lower bound, not a complete monotonicity audit.

STAGNATION here is repetition, not semantic novelty. `src/utils/negotiation_helpers.py::is_repetitive()`
already gates this in production (triggering a same-role regeneration mid-run), so the interesting
evaluation question is not "does repetition happen" (production already suppresses it within a run) but
"how much regeneration did it take" — this script reads that signal off the compliance-metrics-style
retry counters where available, and independently re-measures round-to-round textual similarity within
each role's own message sequence as a cheap proxy for stagnation, using difflib (stdlib, no embedding
model, no new LLM call) rather than true semantic similarity.
"""

import argparse
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_RETRACTION_LANGUAGE = re.compile(
    # Must target an offer/concession/proposal/position THIS ROLE previously made, not a claim,
    # request, objection, or challenge belonging to the other party — "we are willing to withdraw our
    # request/objection/claim" is a settlement offer (a large concession), not a retraction, and an
    # earlier version of this pattern matched bare "withdraw" and flagged four such cases as false
    # positives before this fix. Caught by reading every flag's actual trigger context, not by
    # inspection.
    r"\b(withdraw|retract|rescind)\s+(our\s+)?(earlier|previous|prior)?\s*(offer|concession|proposal|position)\b"
    r"|\bno longer (offer|stand by|willing to (offer|honour|honor))\b"
    r"|\breconsider(ing)? our (earlier|previous|prior) (offer|concession|position)\b",
    re.I,
)


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
    n_logs = 0
    concession_by_role_round = Counter()   # (role, "round1"|"round2+") -> count of rounds with a concession
    total_by_role_round = Counter()
    retraction_suspects = []
    similarity_scores = []   # round-to-round SequenceMatcher ratio within one role's own message sequence

    for source, log in iter_negotiation_logs():
        n_logs += 1
        by_role: dict[str, list[dict]] = {}
        for m in log.get("messages", []):
            by_role.setdefault(m["sender_role"], []).append(m)

        for role, msgs in by_role.items():
            msgs = sorted(msgs, key=lambda m: m["round_number"])
            conceded_so_far = []  # concession texts made earlier by this role in this run

            for i, m in enumerate(msgs):
                bucket = "round1" if m["round_number"] == 1 else "round2+"
                total_by_role_round[(role, bucket)] += 1
                if m.get("concession_made"):
                    concession_by_role_round[(role, bucket)] += 1
                    conceded_so_far.append(m["concession_made"])

                # Explicit-retraction check: only meaningful once this role has conceded at least once.
                if conceded_so_far and _RETRACTION_LANGUAGE.search(m.get("message", "") or ""):
                    entry = {
                        "source": source, "role": role, "round": m["round_number"],
                        "message": (m.get("message") or "")[:300],
                    }
                    retraction_suspects.append(entry)
                    if verbose:
                        print(f"[RETRACTION?] {source} r{m['round_number']} ({role}): {entry['message']}")

                # Stagnation proxy: textual similarity to this role's own immediately preceding message.
                if i > 0:
                    prev_text = msgs[i - 1].get("message", "") or ""
                    cur_text = m.get("message", "") or ""
                    if prev_text and cur_text:
                        ratio = SequenceMatcher(None, prev_text, cur_text).ratio()
                        similarity_scores.append(ratio)

    def rate(role: str, bucket: str) -> float | None:
        total = total_by_role_round[(role, bucket)]
        return round(concession_by_role_round[(role, bucket)] / total, 4) if total else None

    roles = sorted({r for r, _ in total_by_role_round})
    concession_trend = {
        role: {"round1_concession_rate": rate(role, "round1"), "round2plus_concession_rate": rate(role, "round2+")}
        for role in roles
    }

    return {
        "n_logs_scanned": n_logs,
        "concession_rate_by_role_and_stage": concession_trend,
        "explicit_retraction_suspects": retraction_suspects,
        "n_explicit_retraction_suspects": len(retraction_suspects),
        "consecutive_message_similarity": {
            "n_pairs": len(similarity_scores),
            "mean": round(sum(similarity_scores) / len(similarity_scores), 4) if similarity_scores else None,
            "note": "difflib SequenceMatcher ratio between a role's message and its own immediately "
                    "preceding message in the same run — a textual-overlap proxy for stagnation, not "
                    "semantic similarity. is_repetitive() in negotiation_helpers.py already prevents "
                    "near-duplicate messages from being accepted in production, so scores here reflect "
                    "what got THROUGH that gate, not raw model output.",
        },
        "method_note": (
            "Retraction check is high-precision/low-recall: only explicit reversal language is caught, "
            "not implicit backsliding on a concession's substance. Every suspect is worth a human read, "
            "not a final verdict — same posture as the other analyze_*.py scripts in this directory."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    result = analyze(verbose=args.verbose)

    print(f"\n{'='*70}")
    print("  NEGOTIATION DYNAMICS: CONCESSION TREND + STAGNATION PROXY")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']}")
    print("\nConcession rate by role, round 1 vs round 2+:")
    for role, d in result["concession_rate_by_role_and_stage"].items():
        print(f"  {role:24s} round1={d['round1_concession_rate']}  round2+={d['round2plus_concession_rate']}")

    sim = result["consecutive_message_similarity"]
    print(f"\nConsecutive same-role message similarity: mean={sim['mean']} over {sim['n_pairs']} pairs")

    print(f"\nExplicit retraction suspects: {result['n_explicit_retraction_suspects']}")
    for s in result["explicit_retraction_suspects"][:10]:
        print(f"  - {s['source']} r{s['round']} ({s['role']}): {s['message'][:150]}")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
