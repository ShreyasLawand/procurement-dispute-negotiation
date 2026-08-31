# Thesis build

MSc Data Science ERP report. Uses the University of Manchester `muthesis` class.

## Files

| File | Contents |
|---|---|
| `report.tex` | Master file: preamble, title metadata, front matter, chapter includes |
| `abstract.tex` | Abstract (297 words, under the 300 limit) |
| `ai-statement.tex` | AI statement — a required preliminary page under the DATA72000 guidance |
| `acknowledgements.tex` | Acknowledgements |
| `chapter1.tex` | Introduction (includes the concise literature review) |
| `chapter2.tex` | Methodology |
| `chapter3.tex` | Evaluation and Reflection |
| `chapter4.tex` | Conclusion |
| `appendix1.tex` | Appendices A–D: corpus, prompt extracts, reproduction, ethics |
| `refs.bib` | Bibliography, 25 entries, all cited |
| `word.count` | Body word count, printed under the contents page by the `wordcount` class option |
| `muthesis.cls` | The UoM class file, unmodified |

## Build

Four passes, because the bibliography and the cross-references each need a
resolution round:

```
pdflatex report
bibtex   report
pdflatex report
pdflatex report
```

`latex` also works if you want DVI, but PDF is the norm now.

### Overleaf (recommended)

Upload every file in this directory to a new Overleaf project, set the main
document to `report.tex`, and set the compiler to **pdfLaTeX**. Overleaf runs
the bibtex pass automatically. All packages used are in Overleaf's default TeX
Live distribution; no manual installs are needed.

### MiKTeX on Windows

MiKTeX will offer to install any missing package on the first run — accept.
Packages used: `graphicx`, `booktabs`, `array`, `longtable`, `multirow`, `url`,
`listings`, `amsmath`, `amssymb`, `tikz` (with the `arrows.meta`, `positioning`,
`shapes.geometric`, `calc`, `fit`, `backgrounds` libraries), `caption`,
`xcolor`, `hyperref`, `lmodern`.

All six figures are drawn in TikZ, so there are no external image files to
manage and nothing to go missing.

## Regenerating the word count

The `wordcount` class option prints whatever is in `word.count` underneath the
contents page, which is where the DATA72000 guidance requires it. To recount
after editing:

```
python ../scripts/count_thesis_words.py
```

That script counts the abstract and Chapters 1–4 only, and excludes tables,
figures, captions, listings and appendices, matching the rubric's definition
(references, appendices and figure/table captions are not counted). Current
total: **7,959** against a target of ~8,000 and a permitted range of 7,000–9,000.

## Two things to decide before you submit

1. **`anon` class option.** `report.tex` currently passes `anon`, which prints
   the student ID on the title page instead of your name — this matches the
   sample title page in the DATA72000 presentation guidance, which lists a
   student ID and no name. If your programme wants your name there instead,
   delete `anon` from the `\documentclass` options.
2. **Department vs School.** The title page currently reads *Department of
   Computer Science*. The guidance asks for "the candidate's School". Confirm
   which your programme expects and adjust `\department{}` in `report.tex`.

## Checks that were run

- `check_tex.py` (in the job scratch directory): environment balance, brace
  balance, every `\ref` resolves to a `\label`, every `\cite` key exists in
  `refs.bib`. Clean.
- Every experimental figure quoted in Chapter 3 was regenerated from the
  committed logs immediately before the report was written. See Appendix C for
  the command behind each one.
