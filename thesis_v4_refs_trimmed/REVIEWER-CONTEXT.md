# Examiner context pack

Upload this file alongside the report's `.tex` files. It gives an assessor
everything needed to mark the report strictly: the marking scheme it is graded
against, what the artefact actually is, which figures are verified and which are
not, and the known weaknesses an examiner should probe.

---

## 1. Opening message to paste

> You are an experienced examiner marking an MSc Data Science dissertation at the
> University of Manchester. I am the candidate. Mark my report **strictly**, to
> the standard of a real second marker who is looking for reasons to withhold
> marks, not to encourage me.
>
> Read `REVIEWER-CONTEXT.md` first: it contains the marking scheme with weights,
> the project background, and a ledger of which claims are verified. Then read the
> report itself (`abstract.tex`, `chapter1`–`chapter4.tex`, `appendix1.tex`).
>
> Produce: (a) a percentage mark for each of the seven weighted report
> components, with the specific evidence in the text that justifies each mark;
> (b) an overall percentage against the classification bands in §3; (c) the five
> criticisms most likely to cost marks, ranked by how much they cost; (d) for
> each, the smallest edit that would fix it.
>
> Do not soften. If a claim is over-stated, say so. If a section is thin for its
> weight, say so. Where you disagree with a judgement I made, argue it. Do not
> invent facts about the artefact that are not in these files — if something is
> undeterminable from what you have, say "cannot determine from the supplied
> material" rather than assuming.

---

## 2. The marking scheme (COMP66060 / DATA72000)

Report is **85%** of the unit; video is the other 15% and is not part of this
review.

| Component | Weight | What the rubric asks |
|---|---|---|
| Abstract | 5% | Concise summary of purpose, methods, key results. Executive summary quality. |
| Introductory Material | 20% | Establishes context (why it matters) and subject area (what it is) with proper citations and figures. Objectives clearly stated, coherent, appropriate. Includes a *concise* literature review — depth over breadth. |
| Methodology | 20% | Clear explanation of methods with figures/diagrams/tables. **Justification for why these methods, compared and contrasted with alternatives.** |
| Evaluation and/or Reflection | 20% | Appropriate evaluation/testing/critical reflection. **Justification of evaluation methods and alignment with project goals.** |
| Conclusion | 10% | Clear conclusions supported by outcomes and aligned with stated objectives. Thoughtful analysis of the project process; well-justified future work. |
| Format and Structure | 5% | Logical structure, numbered figures/tables, correctly formatted consistent references, clear expression. |
| Project Achievement | 20% | Complexity, scope and challenge of the artefact; execution quality, reliability, technical accuracy. |

**Hard constraints.** ~8,000 words, penalties outside 7,000–9,000 (references,
appendices and figure/table captions excluded). Abstract ≤300 words. Separate
Abstract and Conclusion sections are mandatory; other headings are not
prescribed. There is deliberately **no separate Background chapter** — the
literature review belongs inside the Introduction.

Presentation requirements (DATA72000): 12pt, 1.5 or double spacing, single
Arabic page sequence with the word count at the foot of the contents page,
left-justified body text, and required preliminary pages in order — title page,
contents, abstract, declaration, copyright, AI statement.

**Current compliance:** body 8,338 words; abstract 298; all preliminary pages
present including the AI statement; word count in `word.count` is what the
`wordcount` class option prints.

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
frontend, 92 passing tests, 23 verified real judgments, 299 logged negotiations,
ten analysis scripts.

---

## 5. Verified figures ledger

Every figure below was regenerated from committed logs immediately before
submission. **An examiner should treat these as accurate and check whether the
report's prose matches them** — not re-derive them.

### Scale and reliability
| Figure | Value |
|---|---|
| Logs analysed | 299 across 59 batches |
| Structural compliance | 2,861 / 2,865 = **0.9986** |
| Batches clean at 1.00 | 48 of 50; worst 0.906 |
| Tests | 92 passing |

### Corpus and agreement
| Figure | Value |
|---|---|
| Real UK judgments | 23 (14 merits disposition, 9 interim-only) |
| Merits split | 6 authority wins / 8 losses |
| **Leak-free agreement** | **7 of 8** (the figure the report defends) |
| Leaked-subset agreement | 6 of 6 (compliance, not prediction) |
| Combined | 13 of 14 (not quoted without the split) |
| Majority-class floor on leak-free subset | 4 of 8 |

### Baselines and ablation
| System | Runs/case | Result |
|---|---|---|
| Majority-class heuristic | — | 5 / 6 |
| Zero-shot single prompt | 5 | 6 / 6 |
| Full pipeline (V4) | 8 | 6 / 6 |
| No-Court ablation | 3 | **0 of 18 resolved** |

V3/V4 ablation, n=8 per cell, Fisher's exact: Lancashire 0.875→1.000 (p=1.000),
Faraday 0.750→1.000 (p=0.467), Parkingeye 0.875→1.000 (p=1.000), Alstom
0.500→1.000 (p=0.077), Woods 1.000→1.000 (p=1.000). **No case reaches p<0.05.**

### Fabrication and citation
| Screen | Result |
|---|---|
| Numeric grounding | 9 flagged of 425 (2.1%); all nine re-read, **none Court-originated** |
| Faraday premise fabrication | 3/8 V3 runs, 6/8 V4 runs (phrase search, a lower bound) |
| Citation, wrong regime | 162 of 702 = **23.1%** |
| Citation, s.12 content | 7 of 21 = **33.3%** |
| Too general to classify | 519 (bucketed, not passed as correct) |

### Behaviour
CA concession 0.013 → 0.470; bidder 0.000 → 0.075; message similarity 0.097 over
426 pairs; 0 retractions. BATNA: CA beats 71% / falls short 2% / unclear 27%;
bidder beats 24% / falls short 21% / unclear 56%. Flesch Reading Ease mean
**24.7** (median 25.9), Flesch–Kincaid grade 14.7.

---

## 6. Where the marks should be contested

An examiner should press hardest on these. They are listed because they are the
genuine weak points, not to pre-empt criticism.

1. **Outcome leakage was measured, not removed.** Six of fourteen merits
   scenarios state the real disposition inside the text the agents reason over,
   and `court_prompt.py` explicitly instructs the Court not to contradict a stated
   outcome. The report re-bases every accuracy claim on the eight clean cases
   (§3.5). *Is measuring-and-excluding sufficient, or should the corpus have been
   re-run after stripping?* Defensible either way — argue it.

2. **The zero-shot tie.** At n=6 a single naive prompt matches the full pipeline
   6/6. The report says so plainly and rests the architecture argument on the
   no-Court ablation (0/18) instead. *Is that a sufficient defence of the
   architecture, or does it concede the accuracy case entirely?*

3. **Nothing is statistically significant.** The V3/V4 ablation is n=8 per cell
   and no case reaches p<0.05. Every rate in the report is a proportion over a
   modest N. *Does the report over-read patterns that could be noise?*

4. **Single model, single configuration.** Llama 3.1 8B at fixed per-role
   temperatures. Nothing separates "this architecture" from "this model under
   these prompts."

5. **Detector limits.** The numeric screen is string-presence matching, not
   fact-checking. There is a documented case (Bromcom) where the Court fabricated
   an entire scoring dataset and the screen missed it on two independent grounds —
   the run was classified numeric so fell outside the screened population, and the
   regex matches `80%` but not `A=80`. *The report discusses the fabrication; check
   whether it is honest enough about the detector's blind spot.*

6. **Unfixed defect.** An arithmetic bug found on the client's own scoring table
   (the Court re-applying an already-applied percentage weighting) resisted three
   prompt revisions and is reported as open. Those revisions were reverted rather
   than shipped.

7. **Corpus bias.** Litigated cases are a filtered minority — most procurement
   disputes settle. The corpus is further filtered toward well-documented cases,
   and the 6:8 balance was achieved by deliberately hunting for authority-win
   cases.

8. **Vocabulary coverage.** The five-outcome remedy vocabulary cannot express
   three real remedies present in its own corpus: declaration of ineffectiveness,
   financial penalties on the authority, court-determined re-ranking.

---

## 7. Structure, and where the weight sits

| File | Words | Component | Weight |
|---|---|---|---|
| `abstract.tex` | 298 | Abstract | 5% |
| `chapter1.tex` | 1,666 | Introductory Material | 20% |
| `chapter2.tex` | 1,882 | Methodology | 20% |
| `chapter3.tex` | 3,227 | Evaluation and Reflection | 20% |
| `chapter4.tex` | 1,265 | Conclusion | 10% |
| **Total** | **8,338** | | |

Format and Structure (5%) and Project Achievement (20%) are assessed across the
whole document. `appendix1.tex` holds the verified case corpus, prompt extracts,
a complete logged prompt/response exchange, the reproduction commands, and the
ethics statement — appendices are outside the word count.

Ten figures, all drawn in TikZ (no external image files); thirteen fully-ruled
tables; 31 references, all cited, author-year via natbib.

**A fair criticism to consider:** chapter 3 is 39% of the body for a component
worth 20%, while chapter 1 (20%) and chapter 2 (20%) are smaller. The defence is
that Evaluation also carries most of the evidence for Project Achievement (20%).
Judge whether that holds.

---

## 8. Supervisor feedback already addressed

Dr Mu reviewed an earlier draft: *"a really strong thesis with strong content,
evaluation, and suitable scope. I genuinely don't have any suggestion on
changes."* She raised two specific points, both now in the report:

1. **Pre-processing to remove court-result text.** Investigated rather than
   assumed: there is none, and it mattered. §3.5 is the resulting leakage audit,
   with the accuracy claim re-based on the clean subset and a future-work item to
   strip dispositions at ingestion.
2. **A JSON example showing how the LLM was prompted.**
   `docs/prompt-example-court.json` holds a complete Court exchange from a
   committed run; Appendix B.4 walks through it.

---

## 9. Rules for the review

1. **Do not re-derive the numbers in §5.** They come from analysis scripts run
   over committed logs. Check that the prose matches them; if you think one is
   wrong, say so and stop rather than substituting your own.
2. **Do not reward the negative results as weaknesses.** The zero-shot tie, the
   null significance, the readability shortfall, the 23.1% citation error rate and
   the leakage audit are deliberate reporting of results that do not favour the
   artefact. Judge whether they are *handled well*, not whether they exist.
3. **Judge the report, not the project's potential.** Marks are for what is
   evidenced on the page.
4. **Be specific.** "The methodology could be clearer" is not usable. "The
   justification for LangGraph over free-form conversation is asserted in one
   sentence and never compared against the alternative on any criterion" is.
