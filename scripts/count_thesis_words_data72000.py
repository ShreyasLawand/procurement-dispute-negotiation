"""Word count under the DATA72000 (MSc Data Science) definition, section 3.4.

Superseded 5 Sep 2026: the programme is DATA72000, not COMP66060, per
DSM+ERP+Handbook+25-26+v1.3.pdf. That handbook's word-count definition differs
from what count_thesis_words.py (the old COMP66060-era script) implements in
two material ways:

  INCLUDES (handbook wording): "all text, from the title of chapter one to the
  end of the last chapter, including the body of text, chapter and section
  titles, table and figure captions, chapter footnotes and endnotes,
  quotations, tables, and figures."

  EXCLUDES: report title, table of contents pages, declaration of originality,
  lists of tables/figures, acknowledgements, ABSTRACT, reference list,
  appendices.

Two differences from the old script, both checked directly against the .tex
source before writing this, not assumed:
  1. The old script counted the abstract. The new definition explicitly
     excludes it ("the word count does not include ... abstract").
  2. The old script stripped table/figure/tikzpicture environments (and their
     captions) entirely -- ENV_DROP = [tikzpicture, tabular, table, figure].
     The new definition explicitly includes captions, tables, and figures.

Tables (tabularx/tabular, booktabs-styled): the pure markup (\\toprule,
\\midrule, \\bottomrule, \\cmidrule, the \\begin{tabularx}{width}{colspec}
column spec) is not prose and is dropped; actual cell content (text and
numbers, split on & and \\\\) is counted, matching the handbook's explicit
"tables ... will be included in the word count" and its ban on tables-as-
images.

Figures (all ten in this report are TikZ, no external image files): raw TikZ
markup (coordinates, draw commands, style keys, foreach loops) is not prose
and is dropped. Only the visible label text inside \\node{...} commands is
counted, on the reasoning in section 3.5 of the handbook that what's checked
for a graphical element is "the use of words in graphical elements", i.e.
what a reader actually sees on the page, not the source code that draws it.
This is the one part of this script that is a judgment call rather than a
mechanical extraction -- verified by hand against several figures (see the
module's own test/verification run) but flagged here rather than presented
as unambiguously exact.

Captions: \\caption[short]{long} -- only the mandatory {long} argument is
counted. The optional [short] form is what appears in the List of Figures/
Tables, which the handbook explicitly excludes from the count.

Footnotes: none exist in chapters 1-4 as of this run (checked directly via
grep, not assumed) -- so no footnote-specific handling was needed this time,
but \\footnote{...} content would already be counted correctly by the generic
command-stripping pass below (the command name is dropped, the braces are
stripped, the text inside survives), same as any other one-argument command.

Usage:
    python scripts/count_thesis_words_data72000.py
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "thesis_v4_refs_trimmed"
FILES = ["chapter1.tex", "chapter2.tex", "chapter3.tex", "chapter4.tex"]
WORD_LIMIT = 7500


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", " ", s)


def _find_balanced(s: str, start: int) -> tuple[int, int]:
    """Given s[start] == '{', return (start, end) spanning the balanced group
    (end is the index of the matching '}')."""
    assert s[start] == "{"
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i
        i += 1
    return start, len(s) - 1  # unbalanced (shouldn't happen); take rest of string


def extract_captions(s: str) -> list[str]:
    """Every \\caption[...]{LONG} -> LONG (the mandatory argument only)."""
    out = []
    for m in re.finditer(r"\\caption(\[[^\]]*\])?\{", s):
        brace_start = m.end() - 1
        _, brace_end = _find_balanced(s, brace_start)
        out.append(s[brace_start + 1:brace_end])
    return out


def extract_tikz_node_labels(tikz_body: str) -> str:
    """Visible label text from every \\node...{LABEL} in one tikzpicture body.
    \\node is always followed by an optional [style] and/or (coord) group, neither
    of which use curly braces, so the first '{' after \\node is reliably the
    label's opening brace."""
    out = []
    for m in re.finditer(r"\\node\b", tikz_body):
        brace_start = tikz_body.find("{", m.end())
        if brace_start == -1 or brace_start - m.end() > 200:
            # no label on this node (e.g. a bare anchor point), or the next '{'
            # belongs to something else entirely -- skip rather than guess
            continue
        _, brace_end = _find_balanced(tikz_body, brace_start)
        out.append(tikz_body[brace_start + 1:brace_end])
    return " ".join(out)


def extract_table_cell_text(table_body: str) -> str:
    """Strip booktabs/column-spec markup from a table body, keep cell content.
    Caption text is stripped here too (not just the command name) -- it's already
    counted separately by extract_captions(); this function receives the WHOLE
    \\begin{table}...\\end{table} float (caption included), so without this the
    caption's prose would be double-counted once directly and once as leftover
    words when \\caption is treated as a generic one-argument command."""
    s = table_body
    for m in list(re.finditer(r"\\caption(\[[^\]]*\])?\{", s))[::-1]:
        brace_start = m.end() - 1
        _, brace_end = _find_balanced(s, brace_start)
        s = s[:m.start()] + " " + s[brace_end + 1:]
    # \begin{tabularx}{width}{colspec} / \begin{tabular}{colspec} -> drop the
    # environment opener and its argument(s) entirely, they're not prose.
    # The colspec argument commonly contains its own nested braces (e.g.
    # p{3.3cm}), which a non-nested regex like \{[^{}]*\} silently fails to
    # match past the first inner brace -- caught by inspecting the actual
    # extracted output before trusting it, not assumed correct from the regex
    # alone. Balanced-brace scan instead, for however many {...} groups
    # (1 for plain tabular, 2 for tabularx's extra {width}) follow \begin{...}.
    for begin_m in list(re.finditer(r"\\begin\{tabular[x*]?\*?\}", s))[::-1]:
        pos = begin_m.end()
        n_groups = 0
        while pos < len(s) and s[pos] == "{" and n_groups < 2:
            _, brace_end = _find_balanced(s, pos)
            pos = brace_end + 1
            n_groups += 1
        s = s[:begin_m.start()] + " " + s[pos:]
    s = re.sub(r"\\end\{tabular[x*]?\*?\}", " ", s)
    s = re.sub(r"\\(toprule|midrule|bottomrule)\b", " ", s)
    s = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", " ", s)
    s = re.sub(r"\\multicolumn\{[^}]*\}\{[^}]*\}", " ", s)  # keep the {content} that follows
    s = re.sub(r"\\multirow\{[^}]*\}\{[^}]*\}", " ", s)
    s = s.replace("&", " ").replace(r"\\", " ")
    return s


def process_prose(s: str) -> str:
    """Final common pass: strip remaining LaTeX control sequences and punctuation
    markup, leaving plain words. Same approach as the pre-existing
    count_thesis_words.py, reused rather than reinvented for the parts that
    were already correct there."""
    s = re.sub(r"\\(cite|ref|label|eqref)\{[^}]*\}", " CITE ", s)
    # \begin{table}[htbp] / \begin{figure}[htbp]: strip the wrapper AND its
    # placement-spec bracket group together -- NOT a blanket bracket strip.
    # \item[RQ1]/\item[O1] elsewhere in chapter1 are genuine content labels
    # (research-question and objective tags), not markup, and must survive.
    s = re.sub(r"\\begin\{(table|figure)\*?\}(\[[^\[\]]*\])?", " ", s)
    s = re.sub(r"\\end\{(table|figure)\*?\}", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?", " ", s)
    s = re.sub(r"[{}$&~^_\\]", " ", s)
    return s


def count_words(s: str) -> int:
    return len([w for w in re.split(r"\s+", s) if re.search(r"[A-Za-z0-9]", w)])


def count_file(path: pathlib.Path, verbose: bool = False) -> dict:
    raw = strip_comments(path.read_text(encoding="utf-8"))

    caption_text = " ".join(extract_captions(raw))

    figure_label_text = []
    for m in re.finditer(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", raw, flags=re.S):
        figure_label_text.append(extract_tikz_node_labels(m.group(0)))
    figure_label_text = " ".join(figure_label_text)

    table_cell_text = []
    for m in re.finditer(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", raw, flags=re.S):
        table_cell_text.append(extract_table_cell_text(m.group(0)))
    table_cell_text = " ".join(table_cell_text)

    # Body text: everything with tikzpicture/table environments and captions
    # removed wholesale (captions and table cell content are counted above,
    # from their own dedicated extraction, so counting them again here would
    # double-count them).
    body = raw
    body = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", body, flags=re.S)
    body = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", " ", body, flags=re.S)
    body = re.sub(r"\\caption(\[[^\]]*\])?\{", "{DROP_CAPTION", body)  # remove caption's own text
    body = re.sub(r"\{DROP_CAPTION.*?\}", " ", body, flags=re.S)

    n_body = count_words(process_prose(body))
    n_captions = count_words(process_prose(caption_text))
    n_figures = count_words(process_prose(figure_label_text))
    n_tables = count_words(process_prose(table_cell_text))
    total = n_body + n_captions + n_figures + n_tables

    if verbose:
        print(f"  {path.name:16s} body={n_body:>5}  captions={n_captions:>4}  "
              f"figure labels={n_figures:>4}  table cells={n_tables:>4}  -> {total:>5}")

    return {"body": n_body, "captions": n_captions, "figures": n_figures,
            "tables": n_tables, "total": total}


def main():
    print("Word count under the DATA72000 definition (handbook section 3.4):")
    print("Chapters 1-4 (abstract EXCLUDED); captions, tables and figures INCLUDED.\n")
    grand = {"body": 0, "captions": 0, "figures": 0, "tables": 0, "total": 0}
    for f in FILES:
        r = count_file(ROOT / f, verbose=True)
        for k in grand:
            grand[k] += r[k]

    print(f"\n  {'TOTAL':16s} body={grand['body']:>5}  captions={grand['captions']:>4}  "
          f"figure labels={grand['figures']:>4}  table cells={grand['tables']:>4}  "
          f"-> {grand['total']:>5}")

    over = grand["total"] - WORD_LIMIT
    pct_over = 100 * over / WORD_LIMIT
    print(f"\nHard limit: {WORD_LIMIT}")
    if over <= 0:
        print(f"UNDER the limit by {-over} words.")
    else:
        print(f"OVER the limit by {over} words ({pct_over:.1f}%).")
        if pct_over <= 10:
            print("Within the 10% tolerance markers may exercise discretion on -- not automatic, still risky.")
        elif pct_over <= 50:
            print("10-50% over: report mark CAPPED AT 50% regardless of quality.")
        else:
            print("MORE THAN 50% OVER: work will not be marked. Mark of zero.")

    return grand


if __name__ == "__main__":
    main()
