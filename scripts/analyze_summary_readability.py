"""
Readability analysis — evaluation item 21. Tests the Summary agent's own explicit
claim (src/prompts/summary_prompt.py: NegotiationSummary.plain_english_summary is
described as "a 3-4 sentence summary a non-lawyer could understand") against the
standard Flesch metrics. Pure analysis over already-logged data, no new LLM calls.

No external dependency: `textstat` is not in requirements.txt, and adding a
dependency for one metric wasn't worth doing without asking, so this implements
Flesch Reading Ease and Flesch-Kincaid Grade Level directly using the standard
vowel-group syllable-counting heuristic. That heuristic is approximate by nature
(it undercounts on words with silent letters it doesn't special-case, overcounts
on some diphthongs) — treat scores as indicative, not exact, same posture as the
other two analyze_*.py scripts in this directory.

Benchmarks quoted below (GOV.UK content style guide, Plain English Campaign) are
general public-writing guidance, not a claim about this specific audience — cited
as context for interpreting the numbers, not as a pass/fail bar this project
committed to.

Usage:
    python scripts/analyze_summary_readability.py
    python scripts/analyze_summary_readability.py --field plain_english_summary
    python scripts/analyze_summary_readability.py --json out.json
"""

import argparse
import json
import re
import sys
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.I)


def count_syllables(word: str) -> int:
    word = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not word:
        return 0
    groups = _VOWEL_GROUPS.findall(word)
    n = len(groups)
    # Silent trailing 'e' (e.g. "practice" -> prac-tice, not prac-ti-ce), except
    # when it's the only vowel group (e.g. "the") or follows an 'l' cluster like
    # "-le" in "table" where the e is NOT silent for syllable-counting purposes.
    if word.endswith("e") and not word.endswith("le") and n > 1:
        n -= 1
    return max(n, 1)


_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")
_WORD_SPLIT = re.compile(r"[A-Za-z']+")


def flesch_scores(text: str) -> dict | None:
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    words = _WORD_SPLIT.findall(text)
    if not sentences or not words:
        return None
    syllables = sum(count_syllables(w) for w in words)
    n_words, n_sentences = len(words), len(sentences)
    words_per_sentence = n_words / n_sentences
    syllables_per_word = syllables / n_words
    reading_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    grade_level = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    return {
        "n_words": n_words,
        "n_sentences": n_sentences,
        "words_per_sentence": round(words_per_sentence, 2),
        "flesch_reading_ease": round(reading_ease, 1),
        "flesch_kincaid_grade": round(grade_level, 1),
    }


def _reading_ease_band(score: float) -> str:
    # Standard Flesch interpretation bands.
    if score >= 90: return "very easy (5th grade)"
    if score >= 80: return "easy (6th grade)"
    if score >= 70: return "fairly easy (7th grade)"
    if score >= 60: return "plain English (8th-9th grade)"
    if score >= 50: return "fairly difficult (10th-12th grade)"
    if score >= 30: return "difficult (college)"
    return "very difficult (graduate)"


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


def analyze(field: str) -> dict:
    rows = []
    n_logs = 0
    n_missing = 0

    for source, log in iter_negotiation_logs():
        n_logs += 1
        summary = log.get("summary")
        text = (summary or {}).get(field)
        if not text:
            n_missing += 1
            continue
        scores = flesch_scores(text)
        if scores is None:
            n_missing += 1
            continue
        rows.append({"source": source, "text": text, **scores})

    if not rows:
        return {"n_logs_scanned": n_logs, "n_missing": n_missing, "rows": [], "aggregate": None}

    ease_vals = [r["flesch_reading_ease"] for r in rows]
    grade_vals = [r["flesch_kincaid_grade"] for r in rows]
    return {
        "n_logs_scanned": n_logs,
        "n_missing": n_missing,
        "field": field,
        "aggregate": {
            "n": len(rows),
            "flesch_reading_ease_mean": round(statistics.mean(ease_vals), 1),
            "flesch_reading_ease_median": round(statistics.median(ease_vals), 1),
            "flesch_reading_ease_min": round(min(ease_vals), 1),
            "flesch_reading_ease_max": round(max(ease_vals), 1),
            "flesch_kincaid_grade_mean": round(statistics.mean(grade_vals), 1),
            "flesch_kincaid_grade_median": round(statistics.median(grade_vals), 1),
        },
        "rows": rows,
        "method_note": (
            "Flesch Reading Ease / Flesch-Kincaid Grade Level computed directly (no "
            "textstat dependency) using a standard vowel-group syllable heuristic — "
            "approximate, not exact. Benchmarks are general public-writing guidance "
            "(GOV.UK style guide, Plain English Campaign), not a threshold this "
            "project formally committed to."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--field", default="plain_english_summary",
                    choices=["plain_english_summary", "concessions_summary", "court_reasoning_summary", "likely_next_steps"])
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    result = analyze(args.field)

    print(f"\n{'='*70}")
    print(f"  READABILITY ANALYSIS — NegotiationSummary.{args.field}")
    print(f"{'='*70}")
    print(f"Logs scanned: {result['n_logs_scanned']} | missing/unparseable: {result['n_missing']}")

    agg = result["aggregate"]
    if agg is None:
        print("No summaries found for this field.")
    else:
        print(f"n = {agg['n']}")
        print()
        print(f"Flesch Reading Ease  — mean {agg['flesch_reading_ease_mean']}  "
              f"median {agg['flesch_reading_ease_median']}  "
              f"range [{agg['flesch_reading_ease_min']}, {agg['flesch_reading_ease_max']}]")
        print(f"  -> {_reading_ease_band(agg['flesch_reading_ease_mean'])} (mean band)")
        print(f"Flesch-Kincaid Grade — mean {agg['flesch_kincaid_grade_mean']}  "
              f"median {agg['flesch_kincaid_grade_median']}")
        print()
        print("Reference bands: 90+ very easy (5th grade) · 60-70 plain English (8th-9th "
              "grade, the commonly-cited target for public-facing writing) · 30-50 "
              "difficult (college) · <30 very difficult (graduate)")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nFull result written to {args.json}")
