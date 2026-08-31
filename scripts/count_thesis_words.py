"""Approximate texcount: body words only.

Counts abstract + chapters 1-4. Excludes, per the COMP66060 rubric:
references, appendices, and figure/diagram/table captions. Also excludes
tikzpicture bodies, tabular bodies, lstlisting bodies and LaTeX control
sequences, which are markup rather than prose.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "thesis_overleaf"
FILES = ["abstract.tex", "chapter1.tex", "chapter2.tex", "chapter3.tex", "chapter4.tex"]

ENV_DROP = ["tikzpicture", "tabular", "lstlisting", "table", "figure"]


def strip_env(s, env):
    # non-greedy, handles the fact we never nest the same env
    return re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), " ", s, flags=re.S)


def count(path, verbose=False):
    s = path.read_text(encoding="utf-8")
    s = re.sub(r"(?<!\\)%.*", " ", s)           # comments
    for env in ENV_DROP:
        s = strip_env(s, env)
        s = strip_env(s, env + r"\*")
    s = re.sub(r"\\caption(\[[^\]]*\])?\{", "{", s)  # caption text already gone with figure/table
    s = re.sub(r"\\(cite|ref|label|input|include)\{[^}]*\}", " CITE ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?", " ", s)      # remaining control sequences
    s = re.sub(r"[{}$&~^_\\]", " ", s)
    words = [w for w in re.split(r"\s+", s) if re.search(r"[A-Za-z0-9]", w)]
    if verbose:
        print(f"  {path.name:16s} {len(words):>6}")
    return len(words)


total = 0
print("Body word count (abstract + chapters 1-4):")
for f in FILES:
    total += count(ROOT / f, verbose=True)
print(f"  {'TOTAL':16s} {total:>6}")

(ROOT / "word.count").write_text(str(total), encoding="utf-8")
print(f"\nWrote {ROOT / 'word.count'}")
if not 7000 <= total <= 9000:
    print(f"!! OUTSIDE 7,000-9,000 RANGE by {min(abs(total-7000), abs(total-9000))} words")
else:
    print("Within the 7,000-9,000 range.")
