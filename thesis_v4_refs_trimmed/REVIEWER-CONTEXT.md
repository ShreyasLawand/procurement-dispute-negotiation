# Examiner context pack

Upload this file alongside the report's `.tex` files. It gives an assessor
everything needed to mark the report strictly: the marking scheme it is graded
against, what the artefact actually is, which figures are verified and which are
not, and the known weaknesses an examiner should probe.

---

## 1. Opening message to paste

> You are an experienced examiner marking an MSc Data Science (DATA72000)
> Extended Research Project at the University of Manchester. I am the
> candidate. Mark my report **strictly**, to the standard of a real second
> marker who is looking for reasons to withhold marks, not to encourage me.
>
> Read `REVIEWER-CONTEXT.md` first: it contains the marking scheme with weights,
> the project background, and a ledger of which claims are verified. Then read the
> report itself (`abstract.tex`, `chapter1`–`chapter4.tex`, `appendix1.tex`).
>
> Produce: (a) a percentage mark against each of the five weighted criteria in
> §2, with the specific evidence in the text that justifies each mark; (b) an
> overall percentage against the classification bands in §3; (c) the five
> criticisms most likely to cost marks, ranked by how much they cost; (d) for
> each, the smallest edit that would fix it.
>
> Do not soften. If a claim is over-stated, say so. If a section is thin for its
> weight, say so. Where you disagree with a judgement I made, argue it. Do not
> invent facts about the artefact that are not in these files — if something is
> undeterminable from what you have, say "cannot determine from the supplied
> material" rather than assuming.

---

## 2. The marking scheme (DATA72000)

This is the MSc Data Science ERP unit, governed by the DSM/ERP Handbook
2025-26 (v1.3), **not** COMP66060 — the two units use different rubrics and
different word-count rules; do not apply the COMP66060 scheme to this report.

The **written report is 60%** of the unit's overall mark (the rest is the
oral/viva component, not part of this review). The report itself is marked
against five criteria, which do **not** map one-to-one onto chapters — each
criterion is assessed across the whole document:

| Criterion | Weight | What it asks |
|---|---|---|
| Intellectual content and originality | 25% | Genuine contribution, quality of the underlying idea, depth of engagement with the problem. |
| Coherence of the overall report | 15% | Does the report read as one connected argument — motivation, method, evidence and conclusion in a consistent line — rather than four loosely-joined chapters. |
| Project design and methods | 25% | Soundness of the technical approach, justification against alternatives considered, appropriateness to the problem. |
| Results and analysis | 25% | Quality and honesty of the evaluation: what was measured, how, and whether the interpretation is supported by the evidence. |
| Overall presentation | 10% | Structure, figures/tables, references, clarity of expression, adherence to the format rules below. |

**Hard constraints (DATA72000, distinct from COMP66060's 7,000–9,000 range).**
Word limit is **7,500 words maximum**, a hard cap, not a target range. The
word count **includes** body text, titles, captions, footnotes, quotations,
tables and figures, and **excludes** the title page, table of contents,
declaration, list of illustrations, acknowledgements, abstract, references and
appendices. Penalty bands: **≤7,500 is clean**; 7,500–8,250 (up to 10% over)
loses marks on conciseness only, with no formal cap; 8,250–11,250 (10–50% over)
caps the report mark at 50%; beyond 11,250 (more than 50% over) is a zero
mark. The abstract is capped **separately** at ≤300 words on a single A4 page.

Presentation requirements: 12pt, 1.5 or double line spacing, single-sided
printing, and the required preliminary-page order (title page, contents,
abstract, declaration, list of illustrations, acknowledgements, then the
report body).

**Current compliance:** body **7,496 words** (4 under the 7,500 cap, per
`word.count` and `scripts/count_thesis_words_data72000.py`); abstract **296
words**; all preliminary pages present including the AI statement.

---

## 3. Classification bands

| Band | Mark | What it means at MSc level |
|---|---|---|
| Distinction | 70–100 | Publishable or near-publishable in part. Genuine contribution, evaluation that could survive external scrutiny, limitations identified by the candidate rather than the examiner. |
| Merit | 60–69 | Solid, competent, well-evidenced. Some real insight but claims may outrun evidence in places, or evaluation is narrower than the artefact warrants. |
| Pass | 50–59 | Requirements met. Descriptive rather than analytical; evaluation present but shallow; limitations acknowledged only generically. |
| Fail | <50 | Missing components, unsupported claims, or no meaningful evaluation. |

Mark the report in front of you, not the project's potential.

---

## 4. What the artefact is

MSc Data Science, University of Manchester. Supervisor Dr Tingting Mu.
Industrial partner **Fusion21**, a social enterprise running procurement
frameworks for housing providers, local authorities and NHS bodies.

A multi-agent LLM system simulating UK public procurement dispute negotiation
under the Procurement Act 2023:

- **Contracting Authority**, **Aggrieved Bidder**, and a **Court** modelled on the
  Technology and Construction Court, plus a fourth non-negotiating **Summary**
  agent, orchestrated as an explicit LangGraph state machine.
- All agents run on a locally hosted **Llama 3.1 8B** via Ollama. Behaviour is
  specified by **prompt engineering and structured context injection, not
  fine-tuning** — a deliberate, defended scope decision.
- A **document extraction agent** turns real judgments and uploaded procurement
  paperwork into validated `DisputeScenario` objects.
- A **rule-based pre-award risk screen** (no model call) is the component the
  client actually asked for; the simulator is the academic contribution.
- FastAPI backend, React frontend, live negotiations streamed over SSE.

**The central concern is fabrication.** The Court agent recomputes a scoring
calculation only when the case supplies both a formula and every input that
formula needs, and is otherwise forbidden from writing down an unstated number,
including when the number is hedged as "illustrative".

Scale: 33 Python modules / ~4,900 lines in `src/`, 374 in `api/`, ~3,800 lines of
frontend, 92 passing tests, 23 verified real judgments, over 400 logged
negotiations, ten analysis scripts.

---

## 5. Verified figures ledger

Every figure below was regenerated from committed logs immediately before
submission. **An examiner should treat these as accurate and check whether the
report's prose matches them** — not re-derive them.

### Scale and reliability
| Figure | Value |
|---|---|
| Logs analysed | over 400 negotiations, 50 batches carrying compliance instrumentation |
| Structural compliance | 2,861 / 2,865 = **0.9986** |
| Batches clean at 1.00 | 48 of 50; worst 0.906 |
| Tests | 92 passing |

### Corpus and agreement
| Figure | Value |
|---|---|
| Real UK judgments | 23 (14 merits disposition, 9 interim-only) |
| Merits split | 6 authority wins / 8 losses |
| Outcome leakage found | 6 of 14 merits scenarios stated the real disposition; rewritten and re-run |
| **Leak-free agreement** | **12 of 14** (found-and-fixed, not merely measured) |
| Misses | Turning Point (genuinely arguable different legal conclusion, not fabrication); AbbVie (Dummy Price Mechanism engaged genuinely, wrong conclusion reached) |
| Outcome distribution, 299 runs | re-evaluation 80.6%, no remedy 10.4%, deadlock 5.7%, disclosure 3.0%, 1 out-of-vocabulary |

### Baselines and ablation
| System | Runs/case | Direction correct |
|---|---|---|
| Majority-class heuristic | — | 5 / 6 (wrong on AbbVie) |
| Zero-shot single prompt | 5 | 5 / 6 (wrong on AbbVie) |
| Full pipeline (V4) | 8 | 5 / 6 (wrong on AbbVie) |
| No-Court ablation | 3 | **0 of 18 resolved** |

**All three methods converge on the identical miss (AbbVie) at 5/6** — the
headline finding is flat, not just negative: architecture cannot be defended
on accuracy. The no-Court ablation is where the architecture's necessity
actually shows.

V3/V4 ablation, Fisher's exact: Lancashire 0.875→1.000 (n=8, p=1.000), Faraday
0.750→1.000 (n=8, p=0.467), Parkingeye 0.875→1.000 (n=8, p=1.000), Woods
1.000→1.000 (n=8, p=1.000), **Alstom 0.310→0.857 (n≈30, p=3.96×10⁻⁵)** — the
only case tested at adequate scale, decisive, and robust to a worst-case
sensitivity check excluding/recoding the fabricated runs (p=0.0014). Alstom's
own n=8→n≈30 rates moving substantially is itself evidence the other four
cells are underpowered, not settled at "no effect".

### Fabrication (four independent screens)
| Screen | Result |
|---|---|
| Numeric grounding (Step 2A/2B) | **13 confirmed** of 784 screened, all Court-originated, all the same shape (invented input numbers, correct arithmetic on them): 1 Bromcom, 1 Parkingeye, **5 Alstom**, 6 Woods (1+1+5+6=13). *(Previously flagged as an unresolved inconsistency against a stale "Alstom (2)" table entry — reconciled against `RESULTS-FOR-THESIS.md`'s per-instance ledger: the count moved 9→12→13 across three verification passes, most recently a scenario-attribution audit that caught a 13th, Alstom-specific instance in a `Label(N/5)` numeric shape the original detector regex didn't cover. Table 3.4 now reflects the correct count.)* |
| Scenario-attribution fabrication | **4 confirmed** of 23 candidates (17.4%), the Court asserting its own scenario said something it did not; 1 of the 4 factually backwards from the real disposition |
| Faraday premise fabrication | 3/8 V3 runs, 6/8 V4 runs (phrase search, a lower bound) — negotiating agents fabricate a scoring dispute in a process-avoidance case where neither party was scored |
| Citation, wrong regime | 162 of 702 = **23.1%** |
| Citation, s.12 content | 7 of 21 = **33.3%** |
| Too general to classify | 519 (bucketed, not passed as correct) |

### Behaviour
CA concession 0.013 → 0.470; bidder 0.000 → 0.075; 0 explicit retractions.
BATNA: CA beats its own BATNA 71% of the time, bidder 24%. Flesch Reading
Ease mean **24.7**, Flesch–Kincaid grade **14.7** ("very difficult, graduate
level"), despite the Summary agent's own schema promising output "a
non-lawyer could understand".

---

## 6. Where the marks should be contested

An examiner should press hardest on these. They are listed because they are the
genuine weak points, not to pre-empt criticism.

1. **The three-way baseline tie.** At n=6, a majority-class heuristic with no
   model call, a naive (deliberately unhardened) zero-shot prompt, and the full
   multi-agent pipeline all score 5/6 and miss the identical case. The report
   states this plainly and redirects the architecture defence entirely to the
   no-Court ablation (0/18 resolved). *Is that redirection sufficient, or does
   it concede the accuracy case entirely?*

2. **Nothing except Alstom reaches statistical significance.** Four of five
   V3/V4 ablation cells are n=8 with no significant result; only Alstom was
   scaled to n≈30 and reaches p=3.96×10⁻⁵. *Does the report over-read the
   pattern across the other four cases, given they remain genuinely
   unresolved at this sample size?*

3. **Outcome leakage was found and fixed, not merely disclosed.** Six of
   fourteen merits scenarios stated the real disposition inside the text the
   agents reason over. The report rewrote them and re-ran every accuracy
   figure against the corrected set — but stripping a disposition at
   ingestion is flagged as future work for any *new* upload, not yet a
   permanent pipeline guarantee. *Is a one-off audit-and-fix sufficient, or
   does the architecture need the check built in?*

4. **Single model, single configuration.** Llama 3.1 8B at fixed per-role
   temperatures. Nothing separates "this architecture" from "this model under
   these prompts."

5. **Detector limits, stated but real.** The numeric screen is
   string-presence matching, not fact-checking; the Faraday premise-fabrication
   count is a phrase search and an explicit lower bound; the BATNA classifier
   is a keyword heuristic. Each limit is disclosed in the text next to its
   own figure — check whether the disclosure is prominent enough at the
   point each number is first cited, not just in the threats-to-validity
   section.

6. **Unfixed defect.** An arithmetic bug found on the client's own scoring
   table (the Court re-applying an already-applied percentage weighting)
   resisted three prompt revisions and is reported as open.

7. **Corpus bias.** Litigated cases are a filtered minority — most
   procurement disputes settle. The corpus is further filtered toward
   well-documented cases, and the 6:8 merits-group balance was achieved by
   deliberately seeking out authority-win cases to get any CA-win ground
   truth into the corpus at all.

8. **Vocabulary coverage.** The five-outcome remedy vocabulary cannot express
   real remedies present in its own corpus: a declaration of ineffectiveness
   (Faraday), financial penalties on the authority (Consultant Connect), or a
   court-determined re-ranking rather than a re-run (Woods).

---

## 7. Structure, and where the weight sits

Unlike COMP66060, DATA72000's five criteria are not assigned per-chapter — each
is judged across the whole report. The chapter breakdown below is for word-count
accounting only, not a weight map:

| File | Words (body + captions + tables) | Chapter |
|---|---|---|
| `abstract.tex` | 296 (separate ≤300 cap, excluded from the 7,500 count) | Abstract |
| `chapter1.tex` | 1,420 | Introduction |
| `chapter2.tex` | 1,968 | Methodology |
| `chapter3.tex` | 3,133 | Evaluation and Reflection |
| `chapter4.tex` | 975 | Conclusion |
| **Total** | **7,496** | (≤7,500 hard limit) |

`appendix1.tex` holds the verified case corpus, prompt extracts, a complete
logged prompt/response exchange, the reproduction commands, agent
configuration, the Court prompt revision history, further plan-change
decisions, and the ethics statement — appendices are excluded from the word
count entirely, which is why supporting detail moved there is more verbose
than the main chapters.

One diagram survives in the main chapters: `fig:architecture` (the
five-layer system stack, in `chapter2.tex`), restored after a check found
the equivalent prose passage was not self-explanatory to a reader without
the original figure — the diagram numbers the layers (L1, L2.5, L2, L3,
L4, L5) in a way a single run-on sentence could not without becoming
harder to follow, not easier. Every other diagram originally planned as a
figure (including the Court agent's Step 1/2A/2B decision procedure, which
a cold read confirmed reads clearly as prose) was converted to prose or
deleted during the word-count compression pass, since figure labels were
the most expensive per-word content under the DATA72000 counting rule.
Tables (booktabs, no vertical rules) carry the compact evidentiary content;
several supporting (non-evidentiary) tables were moved to the appendix,
leaving in the main chapters only the tables directly cited as evidence
(agreement, baselines, ablation, fabrication, objectives).

**A fair criticism to consider:** chapter 3 (Evaluation and Reflection) is
42% of the body, reflecting that Results and analysis (25%) and much of
Project design and methods (25%) both draw on it. Judge whether that
concentration is justified by DATA72000's weighting or simply imbalanced.

---

## 8. Supervisor feedback already addressed

Dr Mu reviewed an earlier draft: *"a really strong thesis with strong content,
evaluation, and suitable scope. I genuinely don't have any suggestion on
changes."* She raised two specific points, both now in the report:

1. **Pre-processing to remove court-result text.** Investigated rather than
   assumed: there was none, and it mattered. §3.4 (Agreement with real
   dispositions) is the resulting leakage audit, with the accuracy claim
   re-based on the leak-free 14-case set and a future-work item to strip
   dispositions at ingestion for any new upload.
2. **A JSON example showing how the LLM was prompted.**
   `docs/prompt-example-court.json` holds a complete Court exchange from a
   committed run; Appendix B ("Prompt extracts") walks through it.

---

## 9. Rules for the review

1. **Do not re-derive the numbers in §5.** They come from analysis scripts run
   over committed logs. Check that the prose matches them; if you think one is
   wrong, say so and stop rather than substituting your own.
2. **Do not reward the negative results as weaknesses.** The three-way
   baseline tie, the null significance on four of five ablation cells, the
   readability shortfall, the 23.1% citation error rate, and the leakage audit
   are deliberate reporting of results that do not favour the artefact. Judge
   whether they are *handled well*, not whether they exist.
3. **Judge the report, not the project's potential.** Marks are for what is
   evidenced on the page.
4. **Be specific.** "The methodology could be clearer" is not usable. "The
   justification for LangGraph over free-form conversation is asserted in one
   sentence and never compared against the alternative on any criterion" is.
