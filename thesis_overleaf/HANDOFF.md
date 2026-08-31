# Thesis handoff — context pack for a new Claude session

Read this first, then the ledger in §4. Everything here is for continuing work on
the MSc report draft in `thesis_overleaf/`.

---

## 1. Paste this as your opening message

> I'm finalising my MSc Data Science dissertation at the University of Manchester
> (supervisor Dr. Tingting Mu, industrial partner Fusion21). The full draft
> already exists as a LaTeX project and I'm uploading it along with the project's
> documentation and the marking guidance.
>
> The project builds a multi-agent LLM system that simulates UK public procurement
> dispute negotiation — a Contracting Authority agent, an Aggrieved Bidder agent,
> a Court agent modelled on the Technology and Construction Court, plus a
> non-negotiating Summary agent — orchestrated with LangGraph over a locally
> hosted Llama 3.1 8B. Behaviour is specified by prompt engineering, not
> fine-tuning. The project's central empirical finding is about model fabrication:
> the Court agent recomputes a scoring calculation only when the case supplies
> both a formula and every input it needs, and is otherwise forbidden from writing
> down an unstated number.
>
> Before you change anything, read `HANDOFF.md`. Section 4 is a ledger of every
> experimental figure in the draft and the command that produced it. **Do not
> change, round, re-derive, or "correct" any number in the draft.** They were all
> re-run against committed logs immediately before the draft was written, and I
> cannot re-verify them from this chat. If you think a number is wrong, say so and
> stop — do not edit it.
>
> Section 5 lists the constraints I'm marked against. Section 6 is what still
> needs doing. Start by reading everything and telling me what you'd tackle first
> and why — don't edit yet.

Then upload the files in §2.

---

## 2. What to upload, in priority order

**Tier 1 — essential (upload all of these).**

| File | Why |
|---|---|
| `thesis_overleaf/HANDOFF.md` | This file. The ledger and the rules. |
| `thesis_overleaf/chapter1.tex` … `chapter4.tex` | The draft body |
| `thesis_overleaf/abstract.tex`, `ai-statement.tex`, `acknowledgements.tex` | Front matter |
| `thesis_overleaf/appendix1.tex` | Appendices A–D |
| `thesis_overleaf/report.tex`, `refs.bib` | Preamble, title metadata, bibliography |
| `MSc_Report_and_Video_Rubric.pdf` | The marking scheme. Everything is graded against this. |
| `DATA72000 Guidance for the Presentation of ERP Reports v1.1.pdf` | Required pages, formatting, word count placement |

**Tier 2 — upload if you're doing substantive rewriting, not just polish.**

| File | Why |
|---|---|
| `CLAUDE.md` | The project bible. 463 lines. Full design history, every bug and its fix, every caveat on every figure. This is where "why is it like that" is answered. |
| `evaluation-five-cases.md` | The V3/V4 ablation in full, with the Faraday fabrication finding |
| `evaluation-baselines.md` | The zero-shot tie and no-Court ablation, in full |
| `evaluation-bailii-expansion.md` + `-round2.md` | How the corpus went 5 → 8 → 23, and the per-case dispositions |
| `deliverable-risk-screen.md` | The Fusion21-facing deliverable, and its honest limits |
| `evaluation-counterfactual-regret.md` | Why the "settlement would have been preferred" claim is *not* made |

**Tier 3 — only if asked for.** `CSDI-14265414-project-plan.docx` (the original
plan; useful for justifying divergences), the five exemplar reports (`Report 1–5.pdf`,
useful only for calibrating tone/structure — the draft already matches them).

Don't upload `muthesis.cls`. A chat session can't compile anyway and it wastes context.

---

## 3. Where things stand

Draft is **complete and internally consistent**: 8,772 words, 4 chapters, 6 TikZ
figures, 10 tables, 25 references, all `\ref` and `\cite` resolving. It has not
been compiled — there is no LaTeX installed locally. Use Overleaf (upload
the contents of this folder, set main document to `report.tex`, compiler pdfLaTeX).

Chapter map and word split:

| File | Words | Rubric component |
|---|---|---|
| `abstract.tex` | 297 | Abstract, 5% |
| `chapter1.tex` | 1,849 | Introductory Material, 20% |
| `chapter2.tex` | 1,993 | Methodology, 20% |
| `chapter3.tex` | 3,176 | Evaluation and/or Reflection, 20% |
| `chapter4.tex` | 1,457 | Conclusion, 10% |

Format and Structure (5%) and Project Achievement (20%) are assessed across the
whole document. Recount after any edit with `python scripts/count_thesis_words.py`,
which writes `thesis_overleaf/word.count` — the file the title page reads from.

---

## 4. Figures ledger — DO NOT ALTER THESE

Every number below was regenerated from committed logs on 24 Aug 2026, at a corpus
size of **299 negotiation logs across 59 batches**. Earlier figures quoted in
`CLAUDE.md` and the `evaluation-*.md` files were computed at 63, 141 and 169 logs
and are **superseded** — if a doc and this ledger disagree, this ledger wins.

### Scale and reliability

| Figure | Value | Source |
|---|---|---|
| Logs analysed | 299 | 283 batch runs + 16 root logs |
| Batches | 59 (50 with compliance instrumentation) | `batch_results/` |
| Structural compliance | **2,861 / 2,865 = 0.9986** | `compliance` key in each `batch_summary.json` |
| Batches clean at 1.00 | 48 of 50; worst 0.906 | same |
| Code size | 33 modules / ~4,900 lines `src/`; 374 `api/`; 3,822 frontend; 92 tests passing | `wc -l`, `pytest` |

### Corpus

| Figure | Value |
|---|---|
| Real UK judgments | **23** (14 merits disposition, 9 interim-only) |
| Merits split | **6 CA won / 8 CA lost** |
| Candidates researched and rejected | 7 |
| Direction-correct on merits cases | **13 of 14** (miss: Turning Point v Norfolk CC) |

### Outcome distribution (299 runs)

re-evaluation 80.6% · no remedy 10.4% · deadlock 5.7% · disclosure ordered 3.0% ·
one outlier, `"request for additional information"`, outside `KNOWN_OUTCOMES`.
Median 1 round, max 5.

### Baselines (`evaluation-baselines.md`, 6 comparable cases)

| System | Runs/case | Result |
|---|---|---|
| Majority-class heuristic | — | 5 / 6 |
| Zero-shot single prompt | 5 | 6 / 6 |
| Full pipeline (V4) | 8 | 6 / 6 |
| No-Court ablation | 3 | **0 of 18 resolved** |

Zero-shot fabrication check: **0 ungrounded numbers across all 30 reasoning texts.**

### V3/V4 ablation (n=8 per cell, Fisher's exact)

| Case | V3 | V4 | V3 avg rounds | p |
|---|---|---|---|---|
| Lancashire Care | 0.875 | 1.000 | 2.75 | 1.000 |
| Faraday | 0.750 | 1.000 | 3.00 | 0.467 |
| Parkingeye | 0.875 | 1.000 | 1.50 | 1.000 |
| Alstom | 0.500 | 1.000 | 4.38 | 0.077 |
| Woods | 1.000 | 1.000 | 1.00 | 1.000 |

**No case reaches p < 0.05.** Alstom manifest-error rate is 0.50 under both.

### Fabrication screens

| Screen | Result |
|---|---|
| Numeric grounding (Step 2B) | 9 flagged of 425 qualitative assessments (2.1%). All nine re-read: **0 are Court-originated fabrications** — 6 are the Alstom pattern (parties invent specificity, Court declines to verify), 2 are the Court quoting attributively, 1 is a party's own negotiating proposal |
| Faraday premise fabrication | 3/8 V3 runs, 6/8 V4 runs (phrase search — a lower bound) |
| Citation, wrong regime | 162 of 702 = **23.1%** |
| Citation, s.12 content | 7 of 21 s.12-specific = **33.3%** |
| Citations too general to classify | 519 (bucketed, not passed as correct) |

### Behaviour and readability

| Figure | Value |
|---|---|
| CA concession rate | 0.013 (round 1) → 0.470 (round 2+) |
| Bidder concession rate | 0.000 → 0.075 |
| Consecutive-message similarity | mean 0.097 over 426 pairs |
| Explicit retractions | 0 |
| BATNA, CA | beats 71% / matches 1% / falls short 2% / unclear 27% |
| BATNA, Bidder | beats 24% / matches 0% / falls short 21% / unclear 56% |
| Flesch Reading Ease | mean **24.7**, median 25.9, range −15.7 to 57.5 |
| Flesch–Kincaid grade | mean 14.7, median 14.4 |

### Configuration

Llama 3.1 8B via Ollama. Temperatures: CA 0.3, Bidder 0.4, Court 0.2, Summary 0.2,
Extraction 0.2. Negotiating agents escalate to 0.8 / 0.9 on a repetition retry.
`MIN_SOURCE_TEXT_CHARS = 200`. Doc 1 taxonomies: 7 CA / 6 supplier / 6 judiciary
categories; risk screen has 16 rules (7 CA-side, 9 bidder-side).

---

## 5. Hard constraints — tell the new session these explicitly

1. **Never change an experimental number.** See §4. If one looks wrong, flag it
   and stop.
2. **Word count 7,000–9,000**, target ~8,000. Currently 8,772, so there is almost
   no headroom. Any addition needs a corresponding cut. References, appendices and
   figure/table captions don't count.
3. **Don't remove the negative results.** The zero-shot tie (§3.5), the readability
   failure (§3.9), the unfixed arithmetic bug (§3.12), the null significance
   (§3.6) and the 23.1% citation error rate (§3.7) are the strongest evidence of
   real experimental work in the whole report. A fresh session will be tempted to
   soften or bury them. Don't let it.
4. **Don't add hedging.** The draft already states its limits precisely. Extra
   "it should be noted that" padding weakens it and burns words.
5. **Keep the prose plain.** No "delve", "leverage" as a verb, "robust",
   "furthermore", "moreover", "it is important to note", "comprehensive". The
   draft was written and checked to avoid these. First-person singular is used
   deliberately and is correct for a solo project.
6. **All `.tex` files are pure ASCII.** Em-dashes are `---`, en-dashes `--`, quotes
   are `` `` '' ``. Don't paste in Unicode punctuation; it can break older LaTeX
   installs.
7. **Every `\cite` key must exist in `refs.bib`; every `\ref` must have a
   `\label`.** Check after editing.
8. **Don't cite a case, statute or figure that isn't already verified.** The
   project's whole argument is about fabrication. A made-up citation in the report
   about fabrication is fatal.

---

## 6. What still needs doing

**Before submission, in rough priority order:**

1. **Compile it.** Upload the contents of this folder to Overleaf, main document
   `report.tex`, compiler pdfLaTeX. Nothing has been rendered yet — expect to nudge
   figure placement and check no table overflows the margin.
2. **The two title-page decisions.** `report.tex` passes the `anon` class option,
   which prints your student ID instead of your name (this matches the DATA72000
   sample title page). The title page now reads School of Social Sciences,
   Faculty of Humanities, changed from the Computer Science / Science and
   Engineering default. Worth one final confirmation against your programme
   handbook, since it is a submission-critical field.
3. **Supervisor review cycle.** Dr. Mu has not seen this draft.
4. **The video — 15% of the overall grade, not started.** 6–8 minutes, must
   *complement* rather than repeat the report: a live demo of the negotiation
   streaming in the browser, the risk screen, and the fabrication findings shown
   on a real transcript. A talking-head overlay is explicitly encouraged by the
   rubric. This is the single highest-value remaining item per hour spent.
5. **Proofread.** University policy: a proofreader may check grammar and spelling
   only.

**Optional strengthening, only if you find words to spare:**

- A short worked transcript excerpt in Chapter 3 (the Faraday "scoring discrepancy
  between our bid and that of St Modwen" exchange) — currently described but not
  quoted. It would make the premise-fabrication finding land harder.
- Chapter 2 is the shortest chapter at 1,820 words and carries 20% of the marks;
  it could absorb ~150 more words on the extraction pipeline if cut from elsewhere.

---

## 7. Known open items in the project itself

These are honestly reported in the draft as limitations. Don't let a new session
"fix" them in prose — they are unresolved in the artefact.

- **Court arithmetic on already-weighted sub-scores.** Found via two documents a
  Fusion21 employee supplied. The Court re-applies a percentage to a sub-score that
  already has it applied, turning a correct evaluation into a false manifest-error
  finding. Three increasingly explicit prompt revisions failed; all were reverted.
  Recorded in §3.12 as open.
- **Premise fabrication by the negotiating agents.** Partially mitigated (commit
  `5ee1b6b` added a "only cite figures you were actually given" instruction to both
  round-response prompts) but not closed.
- **23.1% wrong-regime citation rate.** The strongest argument for the RAG layer
  that was scoped out.
- **Outcome vocabulary** can't express three real remedies in its own corpus:
  declaration of ineffectiveness, financial penalties on the authority, and
  court-determined re-ranking.
- **Risk screen is uncalibrated.** Needs anonymised pre-action data from Fusion21's
  member base, which is the one concrete ask the project makes of them.

---

## 8. Repository state

Branch `frontend-rebuild`, HEAD `5ee1b6b`. `thesis_overleaf/`, `thesis-guidance/` and
`scripts/count_thesis_words.py` are untracked — commit them when you're ready.
Nothing has been pushed to origin.
