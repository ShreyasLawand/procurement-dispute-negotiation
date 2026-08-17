"""
The real-case corpus: four UK procurement dispute judgments, each as a dense factual
narrative grounded in verified facts (citation, contract value, dispute type, outcome —
no invented numbers or formulas).

This moved out of scripts/generate_real_case_studies.py so the batch evaluator and the
case-study generator share one corpus rather than duplicating it. It replaces the
deleted src/scenarios/ package as the project's source of evaluation scenarios: the
former F21-001/F21-002 synthetic pair was removed in favour of running everything
against real judgments.

Each entry feeds ScenarioExtractionAgent, which produces the DisputeScenario the
negotiation agents actually see — the same path a live document upload takes.
"""

REAL_CASES = {
    "parkingeye-velindre": {
        "dispute_id": "REAL-PARKINGEYE-2026",
        "contracting_authority_name": "Velindre University NHS Trust / Cardiff and Vale University Health Board",
        "bidder_name": "Parkingeye Ltd",
        "source_text": (
            "Parkingeye Ltd v Velindre University NHS Trust & Cardiff and Vale University "
            "Health Board [2026] EWHC 1019 (TCC) — the first reported judgment under the "
            "Procurement Act 2023.\n\n"
            "The contracting authorities, two NHS bodies in Wales (Velindre University NHS "
            "Trust and Cardiff and Vale University Health Board), ran a competitive tender "
            "for a 5-year car park management services contract covering 59 NHS car parks "
            "across their sites. The incumbent provider, Parkingeye Ltd, had held the "
            "contract previously and bid to retain it.\n\n"
            "The published tender notice stated the contract value as £100,000. The actual "
            "value of the contract, based on the services scope and duration, was materially "
            "higher — reported in the range of £10 million to £20 million over the 5-year "
            "term. This discrepancy between the stated and actual contract value became a "
            "central plank of Parkingeye's challenge, alongside its substantive scoring "
            "complaint.\n\n"
            "The contract was awarded to National Parking Control Group (NPCG), which scored "
            "84% overall against Parkingeye's 68%. Parkingeye alleged: (1) the tender notice's "
            "£100,000 value statement was a material transparency failure that would have "
            "attracted a wider and different field of bidders and scrutiny had the true value "
            "been disclosed; (2) the evaluation methodology used to score technical "
            "submissions was substantially developed or clarified only after the procurement "
            "had commenced, contrary to the requirement to fix and publish evaluation "
            "criteria in advance; and (3) bidders were treated inconsistently during "
            "clarification exchanges, with some given more opportunity than others to "
            "address weaknesses in their submissions.\n\n"
            "Parkingeye, as the unsuccessful incumbent bidder, challenged the award during "
            "the standstill period and sought to maintain the automatic suspension on "
            "contract signature pending a full trial of its claims. The contracting "
            "authorities applied to lift the automatic suspension so they could proceed to "
            "contract with NPCG.\n\n"
            "Because this procurement was conducted under the new Procurement Act 2023 "
            "(rather than the previous Public Contracts Regulations 2015), the court applied "
            "the Act's new statutory test for lifting an automatic suspension under section "
            "101 — a public-interest-weighted balancing test that is a deliberate departure "
            "from the previous American Cyanamid-based approach used under the old regime. "
            "Keyser J refused the contracting authorities' application to lift the "
            "suspension, finding that the balance of public interest favoured allowing "
            "Parkingeye's challenge — including the transparency and evaluation-methodology "
            "complaints — to proceed to a full hearing rather than letting the contract "
            "signature go ahead. This is the first reported judicial application of the "
            "Procurement Act 2023's new suspension test, and is being watched closely as an "
            "early signal that the Act's public-interest test may be more claimant-friendly "
            "than the regime it replaced."
        ),
    },
    "lancashire-care": {
        "dispute_id": "REAL-LANCS-2018",
        "contracting_authority_name": "Lancashire County Council",
        "bidder_name": "Lancashire Care NHS Foundation Trust & Blackpool Teaching Hospitals NHS Foundation Trust",
        "source_text": (
            "Lancashire Care NHS Foundation Trust & Blackpool Teaching Hospitals NHS "
            "Foundation Trust v Lancashire County Council [2018] EWHC 1589 (TCC).\n\n"
            "Lancashire County Council ran a procurement for Public Health Nursing and the "
            "0-19 Healthy Child Programme, a contract worth approximately £104 million over "
            "a 5-year term. The two claimant NHS Foundation Trusts were the incumbent "
            "providers of these services and submitted a joint bid to retain the contract. "
            "The Council instead awarded the contract to Virgin Care Services Ltd.\n\n"
            "The Trusts challenged the award, alleging that the Council's evaluation and "
            "scoring of the competing bids was flawed and, critically, that the reasons the "
            "Council gave for the scores awarded were legally inadequate — too vague and "
            "generic to allow the Trusts to understand why their bid scored lower than "
            "Virgin Care's, and therefore too inadequate to allow a meaningful assessment of "
            "whether a manifest error had occurred. This is a transparency-based challenge: "
            "the core allegation is not that a specific calculation was wrong, but that the "
            "contracting authority failed to discharge its duty to give sufficiently clear "
            "reasons for its evaluation decision, as UK procurement law and general public "
            "law principles require.\n\n"
            "The case proceeded to a full trial before Stuart-Smith J in the Technology and "
            "Construction Court. The judge found in favour of the Trusts: the Council's "
            "stated reasons for the scoring differential were legally insufficient to satisfy "
            "its transparency obligations, such that the Trusts (and the court) could not "
            "properly assess whether the evaluation had actually been conducted rationally "
            "and in accordance with the published criteria. As a result, the court set aside "
            "the contract award to Virgin Care, requiring the Council to reconsider its "
            "decision. This case is a significant illustration of a contracting authority "
            "losing a procurement challenge not on the substance of the scoring itself, but "
            "on a pure transparency and adequacy-of-reasons failure — a distinct category of "
            "manifest error from a numeric miscalculation."
        ),
    },
    "faraday-west-berkshire": {
        "dispute_id": "REAL-FARADAY-2018",
        "contracting_authority_name": "West Berkshire Council",
        "bidder_name": "Faraday Development Ltd",
        "source_text": (
            "Faraday Development Ltd v West Berkshire Council [2018] EWCA Civ 2532 "
            "(overturning the High Court's decision in [2016] EWHC 2166).\n\n"
            "West Berkshire Council wished to bring forward a significant regeneration "
            "development on land it owned. Rather than running a full competitive "
            "procurement under the Public Contracts Regulations, the Council entered into a "
            "development agreement directly with St Modwen Developments Ltd, structured as a "
            "conditional land agreement with options rather than as a public works contract. "
            "The estimated value of the development agreement was approximately £125 "
            "million.\n\n"
            "Faraday Development Ltd, a rival property developer that was not given the "
            "opportunity to bid, challenged the arrangement. Faraday's core allegation was "
            "that the development agreement was, in substance, a public works contract that "
            "should have been competitively procured under the procurement regulations, and "
            "that the Council and St Modwen had deliberately structured the deal (using "
            "options and conditionality) to characterise it as outside the scope of those "
            "regulations — a process-avoidance rather than a scoring-methodology dispute.\n\n"
            "At first instance in 2016, the High Court dismissed Faraday's claim, holding "
            "that the agreement as structured did fall outside the scope of the procurement "
            "rules because the Council was not under an enforceable obligation to proceed "
            "with the development. The Council therefore won at first instance.\n\n"
            "Faraday appealed. In November 2018, the Court of Appeal reversed the High "
            "Court's decision. It held that the agreement, properly characterised by its "
            "substance rather than its form, was in fact a public works contract that should "
            "have been competitively tendered, and that structuring it as an options "
            "agreement did not take it outside the regulations. The Court of Appeal made a "
            "declaration of ineffectiveness in respect of the agreement — the first such "
            "declaration made by an English court since the ineffectiveness remedy was "
            "introduced in 2009 — and imposed a nominal civil financial penalty of £1 (the "
            "statutory alternative penalty regime having limited practical bite on the facts "
            "of this case). This case is a landmark illustration of a contracting authority "
            "losing not on how it scored a competition, but on whether it should have run a "
            "competitive procurement at all."
        ),
    },
    "alstom-london-underground": {
        "dispute_id": "REAL-ALSTOM-2017",
        "contracting_authority_name": "London Underground Ltd",
        "bidder_name": "Alstom Transport UK Ltd",
        "source_text": (
            "Alstom Transport UK Ltd v London Underground Ltd [2017] EWHC 1521 (TCC).\n\n"
            "London Underground Ltd ran a procurement for the supply of AC traction motors "
            "and associated control equipment to re-motor 85 Central Line trains, a contract "
            "with a verified value of £112.1 million. Alstom Transport UK Ltd submitted a "
            "bid but was unsuccessful; the contract was awarded to Bombardier.\n\n"
            "Alstom challenged the award, alleging that Bombardier's winning bid should have "
            "failed a mandatory Stage 3 technical threshold requirement in the evaluation "
            "process, and that London Underground had wrongly allowed Bombardier's bid to "
            "advance and ultimately win despite this alleged failure. Alstom's case was that "
            "this was a manifest error in the application of the stated evaluation "
            "methodology — a bid that should have been excluded was instead scored and "
            "awarded the contract.\n\n"
            "Because Alstom's challenge was brought during the standstill period, an "
            "automatic suspension arose preventing London Underground from signing the "
            "contract with Bombardier while the challenge was live. London Underground "
            "applied to the Technology and Construction Court to lift the automatic "
            "suspension so it could proceed to contract, pending full trial of Alstom's "
            "underlying claim.\n\n"
            "Under the procurement regime applicable at the time (prior to the Procurement "
            "Act 2023), the test for lifting an automatic suspension followed the American "
            "Cyanamid framework used for interim injunctions generally: whether there is a "
            "serious issue to be tried, whether damages would be an adequate remedy for the "
            "claimant if the suspension were lifted and it later succeeded at trial, and "
            "where the balance of convenience lies. Stuart-Smith J found that Alstom's "
            "evidence of irreparable harm — the harm it said it would suffer if the "
            "suspension were lifted and the contract signed before trial — was, in the "
            "judge's words, barely credible. The judge concluded that damages would be an "
            "adequate remedy for Alstom if it ultimately succeeded at trial, and that the "
            "balance of convenience favoured London Underground being able to proceed with "
            "the contract. The automatic suspension was lifted, allowing London Underground "
            "to sign the contract with Bombardier while Alstom's underlying manifest-error "
            "claim remained technically live. This case is a clear illustration of a "
            "contracting authority successfully defending an interim suspension application "
            "even where the claimant's underlying substantive allegation (an alleged manifest "
            "error in applying a threshold requirement) was not itself resolved at this "
            "stage."
        ),
    },
    "woods-milton-keynes": {
        # Added 15 Aug 2026 specifically to restore Step 2A (exact-arithmetic
        # verification) test coverage. This was lost when the synthetic F21-002
        # scenario was deleted in favour of real-case-only evaluation — none of
        # the other four real cases here publishes a scoring formula with
        # sub-scores, so nothing exercised "compute it yourself" until this one.
        # See CLAUDE.md "Evaluation scenarios — real cases only" for the context.
        #
        # IMPORTANT — read before assuming this is a like-for-like replacement:
        # this case is NOT a pure transcription/addition slip the way F21-002 was.
        # The published award formula (60% price / 40% quality) is real and
        # verified, so there IS something to compute. But the manifest error the
        # court actually found was in the RATIONALITY of individual quality
        # sub-scores (irrational/inconsistent marking against the published
        # criteria) — closer to Step 2B reasoning — which the court then
        # recombined through the real 60/40 formula to reach a corrected total.
        # A faithful Court agent here should engage BOTH steps: verify the
        # weighted combination is applied correctly (2A) while assessing whether
        # the underlying quality marks were rationally justified (2B). Don't
        # treat a run that skips straight to "the arithmetic is right" as
        # correct — that would miss the actual manifest error in this case.
        "dispute_id": "REAL-WOODS-MKC-2015",
        "contracting_authority_name": "Milton Keynes Council",
        "bidder_name": "Woods Building Services",
        "source_text": (
            "Woods Building Services v Milton Keynes Council [2015] EWHC 2011 (TCC) "
            "(14 July 2015), with a separate remedies judgment [2015] EWHC 2172 (TCC).\n\n"
            "Milton Keynes Council ran a competitive tender for an asbestos removal and "
            "reinstatement services contract, valued at approximately £8 million over a "
            "4-year term as a single-supplier arrangement. The published award criteria "
            "stated that the most economically advantageous tender would be determined by "
            "a weighting of 60% price and 40% quality, scored against 24 individual "
            "criteria.\n\n"
            "Five tenderers submitted bids. Woods Building Services, the incumbent "
            "provider, submitted the cheapest bid. The Council informed Woods that its bid "
            "had been unsuccessful and that the contract would be awarded to a competitor, "
            "European Asbestos Services (EAS).\n\n"
            "Woods challenged the award, alleging manifest error in the scoring of "
            "individual quality criteria and breach of the Council's transparency and "
            "equal treatment obligations. Woods did not allege a simple arithmetic slip in "
            "combining the published weightings — its case was that several of the "
            "individual criterion scores awarded to EAS and to Woods were themselves "
            "irrational or inconsistent with the published scoring methodology, which then "
            "fed through the real 60/40 formula into an incorrect final ranking.\n\n"
            "The case proceeded to a full trial before Mr Justice Edwards-Stuart. The judge "
            "went through the disputed criteria in detail and found that the Council's "
            "tender evaluation process was fundamentally flawed across multiple scoring "
            "items. Applying the Council's own published methodology and weighting, the "
            "judge concluded that EAS's marks required a substantial downward correction "
            "(a reduction of 40 marks in total across the disputed criteria) while Woods' "
            "marks required a small upward correction (an increase of 6 marks). Once these "
            "corrected marks were recombined through the published 60% price / 40% quality "
            "formula, Woods' bid became the most economically advantageous tender rather "
            "than EAS's.\n\n"
            "In the subsequent remedies judgment, the court ordered the Council to set "
            "aside its contract award decision to EAS, to amend its evaluation records to "
            "reflect the corrected scores as found by the court, and declared that Woods "
            "had in fact submitted the most economically advantageous tender. This case is "
            "a clear illustration of a contracting authority losing a procurement challenge "
            "where an explicit, published scoring formula existed, but the manifest error "
            "lay in the rationality of the underlying criterion-level judgments feeding "
            "into that formula — not in the arithmetic of the formula itself."
        ),
    },
    "braceurself-nhs-england": {
        # Added as part of the BAILII expansion (evaluation punch-list item 14). Verified via
        # WebSearch against bailii.org and multiple law-firm case notes before writing: High Court
        # [2022] EWHC 1532 (TCC) (20 June 2022, O'Farrell J), damages question upheld on appeal in
        # [2024] EWCA Civ 39 (30 Jan 2024) — a SEPARATE 2023 Court of Appeal judgment ([2023] EWCA
        # Civ 837) dealt only with a procedural respondent's-notice point on the earlier
        # suspension-lifting stage, not the merits, so it is not cited as a merits outcome here.
        # Selected specifically because the outcome is stable at both instances (unlike Alstom/
        # Parkingeye, where only an interim ruling exists) and because it is a genuine merits trial
        # with a defined, close numeric score gap — a good fit for Step 2A/2B.
        "dispute_id": "REAL-BRACEURSELF-2022",
        "contracting_authority_name": "NHS England",
        "bidder_name": "Braceurself Ltd",
        "source_text": (
            "Braceurself Ltd v NHS England [2022] EWHC 1532 (TCC) (20 June 2022), damages "
            "question finally determined on appeal in [2024] EWCA Civ 39 (30 January 2024).\n\n"
            "NHS England ran a nationwide re-procurement for orthodontic services structured "
            "into geographic lots. This dispute concerned Lot PR002368 (WSX18), a seven-year "
            "contract covering an area of East Hampshire. Braceurself Ltd was the incumbent "
            "provider for that lot and one of two bidders. The competition was extremely "
            "close: Braceurself scored 80.25% overall against the successful bidder's 82.5%, "
            "a gap of 2.25 percentage points.\n\n"
            "Braceurself challenged the award, alleging a manifest error in the marking of "
            "its response to tender question CSD02 (clinical and service delivery). The "
            "specific error alleged was that NHS England's evaluators misunderstood "
            "Braceurself's answer concerning patient access to first-floor premises: "
            "Braceurself's submission referred to a stair-climber (a portable device used to "
            "carry a patient up stairs), but the evaluators read this as a reference to a "
            "stair lift (a fixed installed platform lift) and marked the response down on "
            "the mistaken basis that suitable access provision was inadequate.\n\n"
            "The case proceeded to a full trial before O'Farrell J in the Technology and "
            "Construction Court. The judge found that NHS England had indeed made a manifest "
            "error in marking question CSD02: the evaluators had misunderstood what "
            "Braceurself's bid actually proposed, and but for that error Braceurself would "
            "have received a higher score on that question — a score sufficient to make "
            "Braceurself, not the incumbent competitor, the successful bidder for the lot.\n\n"
            "Despite finding the manifest error, the judge went on to consider whether the "
            "breach was 'sufficiently serious' to found a claim for Francovich-style damages "
            "(the EU-derived test, applied via the Public Contracts Regulations 2015, for "
            "when a procurement breach gives rise to a damages remedy rather than only "
            "process remedies). Weighing factors including the excusability of the error, "
            "whether it was inadvertent, and the otherwise careful and well-organised conduct "
            "of the procurement, the judge concluded the breach was not sufficiently serious "
            "to warrant damages, and dismissed Braceurself's damages claim despite having "
            "found the underlying manifest error proven.\n\n"
            "Braceurself appealed the damages ruling. In [2024] EWCA Civ 39, the Court of "
            "Appeal upheld the first-instance decision: it held that a breach's effect on the "
            "claimant is not itself decisive of whether the breach is 'sufficiently serious' — "
            "what matters more is the nature and quality of the breach itself, including "
            "whether it was inadvertent and excusable. On that basis the Court of Appeal "
            "confirmed that NHS England's manifest error, though real and outcome-determinative "
            "on liability, did not meet the threshold for a damages award. This case is a "
            "clear illustration that a proven manifest error and a damages remedy are two "
            "separate legal hurdles in UK procurement litigation — a contracting authority can "
            "be found to have made an outcome-changing scoring error and still not be liable "
            "in damages for it."
        ),
    },
    "bromcom-united-learning-trust": {
        # Verified via WebSearch (bailii.org, DLA Piper, DAC Beachcroft, Lexology case notes).
        # Selected as a clean multi-ground merits trial with damages actually awarded — useful
        # contrast to Braceurself (liability found, no damages) and to the mostly single-issue
        # existing corpus (here there are three independent unlawful practices, not one).
        "dispute_id": "REAL-BROMCOM-2022",
        "contracting_authority_name": "United Learning Trust and United Church Schools Trust",
        "bidder_name": "Bromcom Computers plc",
        "source_text": (
            "Bromcom Computers plc v United Learning Trust and United Church Schools Trust "
            "[2022] EWHC 3262 (TCC).\n\n"
            "United Learning Trust (UL), an academy trust operating a group of schools, ran a "
            "procurement for a cloud-based Management Information System (MIS) for use across "
            "57 of its schools, a contract worth approximately £2 million. The incumbent "
            "supplier to 15 of those schools, Arbor Education Partners Ltd, won the "
            "competition. Bromcom Computers plc, an unsuccessful tenderer, challenged the "
            "award on three independent grounds.\n\n"
            "First, Bromcom alleged that UL's scoring methodology was itself unlawful: rather "
            "than convening moderation meetings at which evaluators would discuss and agree a "
            "single consensus mark for each criterion (as procurement good practice and UL's "
            "own published process required), UL simply averaged the individual scores each "
            "evaluator had given independently. Bromcom's case was that an unreconciled "
            "average of divergent individual scores is not a transparent or lawful substitute "
            "for genuine moderated consensus scoring, since it allows outlying or "
            "misunderstood individual marks to silently affect the result without ever being "
            "tested or corrected through discussion.\n\n"
            "Second, Bromcom alleged that UL had unlawfully and unequally adjusted the "
            "financial scores: UL added a notional cost to Bromcom's financial submission to "
            "reflect the cost of transferring pupil data from the incumbent system to "
            "Bromcom's system, but did not apply any equivalent adjustment to Arbor's "
            "financial submission, despite Arbor's bid also requiring data transfer for the "
            "42 schools it did not already serve — an inconsistent, one-sided cost adjustment "
            "applied to only one bidder.\n\n"
            "Third, Bromcom alleged that UL had allowed Arbor to offer a rebate linked to a "
            "separate, non-tendered contract as part of its bid, which Bromcom said amounted "
            "to an unlawful modification of the competition's terms not available to other "
            "bidders and in breach of equal treatment.\n\n"
            "The case proceeded to a full trial in the Technology and Construction Court. The "
            "court found in Bromcom's favour on the claim for damages, upholding all three "
            "grounds: the averaging-without-moderation approach to scoring was found to be "
            "neither transparent nor lawful; the one-sided data-transfer cost adjustment "
            "applied only to Bromcom's bid was found to breach the equal treatment principle; "
            "and permitting Arbor's rebate on a separate contract was found to be an unlawful "
            "modification of the competition. This case illustrates a contracting authority "
            "losing a procurement challenge on multiple independent unlawful-process grounds "
            "simultaneously, rather than a single scoring or arithmetic error — a different "
            "failure pattern from the single-issue manifest-error cases elsewhere in this "
            "corpus."
        ),
    },
    "abbvie-nhs-england": {
        # Verified via WebSearch (bailii.org / caselaw.nationalarchives.gov.uk, Sharpe Pritchard,
        # Monckton Chambers case notes). Selected deliberately as a case where the contracting
        # authority WON outright — the existing five-case (now eight-case) corpus otherwise skews
        # entirely toward cases where the CA lost or a manifest error was found, which risks the
        # Court agent's evaluation looking artificially accurate if it is never tested against a
        # genuine "no violation" ground truth.
        "dispute_id": "REAL-ABBVIE-2019",
        "contracting_authority_name": "NHS England",
        "bidder_name": "AbbVie Ltd",
        "source_text": (
            "AbbVie Ltd v NHS Commissioning Board (operating as NHS England) [2019] EWHC 61 "
            "(TCC).\n\n"
            "NHS England ran what was, at the time, the largest single procurement it had "
            "undertaken: a competitive-dialogue procedure to award up to three contracts for "
            "the supply of medicines to treat and eliminate Hepatitis C (HCV) across England, "
            "with an aggregate value of approximately £1 billion over five years from April "
            "2019. Part of the strategic goal of the procurement was to help England become "
            "the first country to eliminate HCV as a public health concern. AbbVie Ltd, one "
            "of only three pharmaceutical suppliers of HCV medication in the UK market, "
            "submitted a bid but was unsuccessful.\n\n"
            "AbbVie challenged the award methodology itself, not the arithmetic outcome. The "
            "evaluation formula used a mechanism the parties called the Dummy Price Mechanism "
            "(DPM): because not every bidder produced medication for every HCV genotype or "
            "treatment category being procured, the formula imputed, or 'credited', a notional "
            "price to a bidder for any treatment category it did not itself supply — the "
            "credited price being the lowest price offered by any other bidder for that "
            "category. AbbVie's case was that this mechanism was inherently meaningless or "
            "incomprehensible as a basis for comparing bids, and that its practical effect was "
            "to favour certain bidders' product portfolios over others in a way that breached "
            "the equal treatment principle in regulation 18 of the Public Contracts "
            "Regulations 2015.\n\n"
            "The case proceeded to trial in the Technology and Construction Court. Both "
            "parties submitted their own calculations modelling how AbbVie's score would have "
            "changed under alternative pricing assumptions. These calculations demonstrated "
            "that, had AbbVie priced its own bid differently within the DPM's rules, AbbVie "
            "could have beaten the winning bidder (MSD) under the mechanism as designed. On "
            "that basis, the court held that AbbVie's claim of unequal treatment was not made "
            "out: the DPM, however unusual, did not structurally disadvantage AbbVie relative "
            "to competitors — AbbVie's own pricing choices, not an unlawful mechanism, "
            "explained its unsuccessful outcome. The court dismissed AbbVie's challenge and "
            "upheld the award. The judgment also confirmed the wide margin of discretion "
            "available to a contracting authority in designing the technical structure of its "
            "award criteria, provided the criteria as designed do not in fact produce unequal "
            "treatment between bidders. This case is the corpus's clearest example of a "
            "contracting authority successfully defending a procurement on the merits, with no "
            "manifest error or unlawful practice found."
        ),
    },
    # --- Added 17 Aug 2026: scaling the corpus from 8 toward the original 20-30 target
    # (evaluation punch-list item 14). Verified via WebSearch (bailii.org / caselaw
    # .nationalarchives.gov.uk plus law-firm case notes) before writing, same discipline
    # as every other entry in this file. Weighted toward genuine merits-trial dispositions
    # (7 of 13) with a smaller set of well-documented interim-only rulings (6 of 13,
    # roughly the same proportion as the original corpus's Alstom/Parkingeye pair) added
    # for volume and diversity rather than every one being forced into a merits shape it
    # doesn't have. See CLAUDE.md's "BAILII expansion, round 2" for the full methodology
    # note, including which candidates were researched and rejected.
    "bechtel-hs2": {
        "dispute_id": "REAL-BECHTEL-2021",
        "contracting_authority_name": "High Speed Two (HS2) Ltd",
        "bidder_name": "Bechtel Ltd",
        "source_text": (
            "Bechtel Ltd v High Speed Two (HS2) Ltd [2021] EWHC 458 (TCC).\n\n"
            "High Speed Two (HS2) Ltd ran a procurement to select a construction partner "
            "for Old Oak Common station, a complex interchange station development in west "
            "London, under the Utilities Contracts Regulations 2016. The contract was "
            "awarded to a consortium, Balfour Beatty Vinci Systra (BBVS). Bechtel Ltd, an "
            "unsuccessful bidder, challenged the award, alleging manifest error in HS2's "
            "evaluation and selection of BBVS over Bechtel's bid, as well as unequal "
            "treatment and a lack of transparency in the evaluation process.\n\n"
            "The case proceeded to a full trial on liability and causation, held over three "
            "weeks in October 2020 with eighteen witnesses giving evidence. Judgment was "
            "handed down on 4 March 2021 by Mr Justice Fraser. The judge found that HS2 had "
            "not breached the Utilities Contracts Regulations 2016 in its evaluation and "
            "selection of BBVS: Bechtel failed to establish that any of the evaluations were "
            "in error, let alone manifestly in error, and failed to establish unequal "
            "treatment or a lack of transparency in HS2's process. The judgment reiterated "
            "that manifest error is a high threshold to meet, requiring something akin to "
            "irrationality in the Wednesbury sense, not merely a disagreement with the "
            "evaluators' judgment. This case is a clear example of a contracting authority "
            "successfully defending a large, complex procurement on the merits, following a "
            "full trial rather than only an interim application."
        ),
    },
    "inhealth-nhs-england": {
        "dispute_id": "REAL-INHEALTH-2023",
        "contracting_authority_name": "NHS England",
        "bidder_name": "InHealth Intelligence Ltd",
        "source_text": (
            "InHealth Intelligence Ltd v NHS England [2023] EWHC 352 (TCC).\n\n"
            "NHS England ran a procurement, split into four geographical Lots, for the "
            "award of contracts to provide child health information services across the "
            "Greater Manchester, Midlands and East of England regions, with a combined "
            "value of over £140 million across a 6-year term (with an optional 3-year "
            "extension). InHealth Intelligence Ltd (IIL) was bidding for three of the four "
            "Lots.\n\n"
            "The Invitation to Tender required a single bid document, containing the "
            "submission for every Lot tendered for, to be uploaded to a third-party "
            "e-tendering portal by the submission deadline; the rules stated explicitly "
            "that a late or incorrect submission would result in the entire bid across all "
            "Lots being excluded, even where other Lots had been validly completed. An "
            "employee of IIL uploaded the relevant document to the wrong location on the "
            "portal; when the system would not allow the same document to be uploaded a "
            "second time to the correct location, the employee sent a message via the "
            "portal requesting help six minutes before the deadline. NHS England excluded "
            "IIL's entire bid, across all three Lots it was contesting, on this basis.\n\n"
            "IIL challenged the exclusion, arguing the e-portal's software was flawed and "
            "that the error should have been waived or corrected. The case proceeded to a "
            "full trial. Mr Justice Constable found that the portal's error message would "
            "have taken less than a minute to read, understand and act on, was not in any "
            "way problematic, and did not amount to an inherent flaw in the software. The "
            "judge held that IIL had failed to comply with a clearly stated deadline and "
            "clearly stated instructions in the Invitation to Tender, and that there was "
            "nothing in the circumstances to justify waiving a clear exclusion rule. NHS "
            "England successfully defended the claim in full. This case illustrates a "
            "contracting authority successfully defending a procurement exclusion decision "
            "on the merits, in a dispute about compliance with submission rules rather than "
            "about the scoring or evaluation of a bid actually received."
        ),
    },
    "energysolutions-nda": {
        "dispute_id": "REAL-ENERGYSOLUTIONS-2016",
        "contracting_authority_name": "Nuclear Decommissioning Authority",
        "bidder_name": "EnergySolutions EU Ltd",
        "source_text": (
            "EnergySolutions EU Ltd v Nuclear Decommissioning Authority [2016] EWHC 1988 "
            "(TCC), damages question later determined by the Supreme Court in Nuclear "
            "Decommissioning Authority v EnergySolutions EU Ltd [2017] UKSC 34.\n\n"
            "The Nuclear Decommissioning Authority (NDA) ran a competitive-dialogue "
            "procurement, between 2012 and 2014, for a contract to decommission twelve "
            "Magnox nuclear facilities and two research sites across the UK. EnergySolutions "
            "formed a consortium, Reactor Site Solutions (RSS) with Bechtel Management "
            "Company Ltd, and was one of the bidders. The contract was awarded to a rival "
            "consortium, Cavendish Fluor Partnership (CFP). The competition was extremely "
            "close: RSS scored 85.42% against CFP's 86.48%, a gap of just over one "
            "percentage point.\n\n"
            "EnergySolutions challenged the award, alleging manifest error in the "
            "evaluation of both bids. The case proceeded to a full trial on liability "
            "before Mr Justice Fraser. Because the claim was issued after the standstill "
            "period had ended, no automatic suspension arose, and the contract had already "
            "been signed and performance had begun. EnergySolutions therefore sought "
            "damages, claimed in the region of £100 million, rather than a re-run of the "
            "competition.\n\n"
            "The judge found that the NDA's evaluation had fallen short in a number of "
            "significant respects, and that correcting for those errors changed the "
            "competitive outcome in RSS's favour, even before separately considering "
            "whether CFP's bid should have been disqualified. The NDA was found liable in "
            "principle for breach of the procurement regulations. The subsequent question of "
            "whether the breach was 'sufficiently serious' to found a damages award, applying "
            "the Francovich test derived from EU law, was ultimately determined by the "
            "Supreme Court, which held that a breach must reach that threshold before "
            "damages are payable — the same legal question later revisited in Braceurself v "
            "NHS England. This case is a clear illustration of a contracting authority "
            "losing a large, high-value procurement dispute on a narrow scoring margin, at "
            "full trial, with a real, substantial damages claim at stake."
        ),
    },
    "turning-point-norfolk": {
        "dispute_id": "REAL-TURNINGPOINT-2012",
        "contracting_authority_name": "Norfolk County Council",
        "bidder_name": "Turning Point Ltd",
        "source_text": (
            "Turning Point Ltd v Norfolk County Council [2012] EWHC 2121 (TCC).\n\n"
            "Norfolk County Council ran a procurement for the provision of drug and "
            "alcohol treatment services. Turning Point Ltd submitted a tender that included "
            "a covering note qualifying or caveating part of its submission. The Invitation "
            "to Tender had stated clearly that qualifications or caveats to a tender would "
            "not be accepted. The Council rejected Turning Point's tender on this basis.\n\n"
            "Turning Point challenged the rejection, alleging that the Council should have "
            "sought clarification of the caveat before rejecting the tender outright, and "
            "alleging other breaches of the Public Contracts Regulations 2006. The case "
            "proceeded to a full trial before Mr Justice Akenhead. Two separate issues were "
            "considered. First, on limitation: the judge held that Turning Point must have "
            "known of the basis for its complaint no later than the date it submitted its "
            "tender (9 February 2012), but did not issue its claim until 28 March 2012, "
            "well outside the applicable 30-day time limit for bringing a procurement "
            "challenge; the judge declined to extend time, finding no good reason to do so, "
            "and held the claim time-barred on that basis. Second, and in any event, on the "
            "merits: the judge held that Turning Point's covering note was a clear "
            "qualification of its tender, that the no-caveats requirement in the Invitation "
            "to Tender was fair, reasonable and a common feature of public procurement, and "
            "that the Council had not been obliged to seek clarification from Turning Point "
            "before rejecting the qualified tender. Norfolk County Council successfully "
            "defended the claim in full, both on limitation and on the merits. This case is "
            "a clear illustration of a contracting authority successfully defending a "
            "tender-rejection decision grounded in the bidder's own failure to comply with "
            "a clearly stated tender-compliance rule, rather than in a dispute about scoring "
            "or evaluation."
        ),
    },
    "siemens-mobility-hs2": {
        "dispute_id": "REAL-SIEMENSMOBILITY-2023",
        "contracting_authority_name": "High Speed Two (HS2) Ltd",
        "bidder_name": "Siemens Mobility Ltd",
        "source_text": (
            "Siemens Mobility Ltd v High Speed Two (HS2) Ltd [2023] EWHC 2768 (TCC).\n\n"
            "High Speed Two (HS2) Ltd ran a procurement under the Utilities Contracts "
            "Regulations 2016 for (i) a manufacture and supply agreement for a minimum "
            "fleet of 54 rolling stock units for the HS2 rail project, and (ii) an "
            "associated train maintenance and services agreement running for a minimum of "
            "twelve years with optional extensions. Siemens Mobility Ltd was an "
            "unsuccessful bidder.\n\n"
            "Siemens brought a wide-ranging challenge to the award, comprising seventeen "
            "separate claims. These included allegations of manifest error in the scores "
            "awarded and in HS2's exercises of evaluative discretion, breach of general "
            "public law principles, an allegation that the winning bid was abnormally low, "
            "and an allegation of undisclosed conflicts of interest affecting the "
            "evaluation panel.\n\n"
            "The case proceeded to a full trial before Mrs Justice O'Farrell. In a judgment "
            "handed down on 6 November 2023, the judge dismissed all seventeen of Siemens' "
            "claims. The judge held that HS2 had not breached the key procurement "
            "principles of equal treatment, non-discrimination or transparency at any stage "
            "of the evaluation, and rejected each of the specific manifest-error, "
            "abnormally-low-bid and conflict-of-interest allegations individually. HS2 "
            "successfully defended the procurement of one of the largest and most complex "
            "contracts in the project's history in full, at trial, against a wide-ranging "
            "and heavily contested challenge. This case is regarded as one of the most "
            "significant UK procurement judgments of recent years, precisely because of the "
            "breadth of grounds it rejected in a single trial."
        ),
    },
    "tnlc-gambling-commission": {
        "dispute_id": "REAL-TNLC-2026",
        "contracting_authority_name": "The Gambling Commission",
        "bidder_name": "The New Lottery Company Ltd",
        "source_text": (
            "The New Lottery Company Ltd & Anor v The Gambling Commission [2026] EWHC 891 "
            "(TCC).\n\n"
            "The Gambling Commission ran the competition for the Fourth National Lottery "
            "Licence, one of the most financially significant procurement processes in UK "
            "history. The licence was awarded to Allwyn Entertainment Ltd in 2022. The New "
            "Lottery Company Ltd (TNLC) and its parent company, Northern & Shell plc, "
            "challenged the award, alleging that the Commission had wrongly awarded the "
            "licence to Allwyn and that TNLC should have won the competition instead, and "
            "separately alleging that the Commission and Allwyn had entered into "
            "impermissible post-award modifications of the licence arrangements. TNLC "
            "claimed damages of approximately £1.3 billion.\n\n"
            "The case proceeded to a full trial lasting three months, concluding in January "
            "2026, before Mrs Justice Joanna Smith. By the close of trial many of TNLC's "
            "original allegations had been abandoned. In a 280-page judgment, the judge "
            "dismissed the remainder of TNLC's claims in full. The judge found that TNLC "
            "had been properly disqualified from the competition for failing over half of "
            "the 23 mandatory requirements a bid had to satisfy to be eligible for "
            "acceptance, and that there had been an enormous gap of over 30 percentage "
            "points between TNLC's aggregate score and Allwyn's. On TNLC's damages claim, "
            "the judge held that TNLC had suffered no recoverable loss, and had no standing "
            "to claim, because it was 'fanciful to suppose' TNLC would have won any "
            "competition against Allwyn, a recognised world leader in operating lotteries. "
            "The judge separately held that TNLC's post-award modifications claim was "
            "time-barred. The Court of Appeal subsequently refused TNLC permission to "
            "appeal. This is a clear, emphatic example of a contracting authority "
            "successfully defending a procurement award at full trial against an "
            "exceptionally high-value challenge, with a real, large numeric score gap "
            "central to the court's reasoning."
        ),
    },
    "consultant-connect-nhs-banes": {
        "dispute_id": "REAL-CONSULTANTCONNECT-2022",
        "contracting_authority_name": "NHS Bath and North East Somerset, Swindon and Wiltshire Integrated Care Board",
        "bidder_name": "Consultant Connect Ltd",
        "source_text": (
            "Consultant Connect Ltd v NHS Bath and North East Somerset, Swindon and "
            "Wiltshire Integrated Care Board & Ors [2022] EWHC 2037 (TCC).\n\n"
            "A group of NHS bodies, including NHS Bath and North East Somerset, Swindon and "
            "Wiltshire Integrated Care Board and NHS Gloucestershire, wished to procure "
            "communications equipment and referral software for use by medical "
            "practitioners. Rather than running a fresh competitive procurement, or a "
            "proper mini-competition among all suppliers on the relevant framework "
            "agreement, the NHS bodies consulted only a handful of framework suppliers, "
            "identified Cinapsis Ltd as the only supplier they considered suitable, and "
            "then ran what they described as a 'mini-competition' under the framework in "
            "which Cinapsis was the only competitor invited to bid. Cinapsis was duly "
            "awarded the contract.\n\n"
            "Consultant Connect Ltd, a supplier that was not a party to the framework "
            "agreement being used and so was never entitled to be considered at all, "
            "nonetheless challenged the award, arguing that the process used did not "
            "comply with the terms of the framework agreement and breached the "
            "contracting authorities' duties of fairness and transparency under the Public "
            "Contracts Regulations 2015 — this was a case about whether the correct "
            "procurement route was used at all, not about the scoring of competing bids.\n\n"
            "The case proceeded to a full trial. In a judgment handed down on 29 July 2022, "
            "the court found against the NHS defendants, holding that running a "
            "single-supplier 'mini-competition' with no genuine competitor did not comply "
            "with the requirements of the framework agreement or with the regulations' "
            "requirements of fairness and transparency, and that this was, in the judge's "
            "assessment, one of the worst breaches of those requirements the case law had "
            "seen. The court imposed financial penalties directly on the three defendant "
            "NHS bodies individually — £10,000, £8,000 and £4,000 respectively, scaled to "
            "reflect the severity of each body's conduct. This case is a clear illustration "
            "of a contracting authority losing a procurement challenge not on a scoring "
            "dispute but on process-avoidance grounds — misusing an existing framework "
            "agreement to sidestep a genuine competitive process altogether — the same "
            "broad category of failure as Faraday Development Ltd v West Berkshire Council "
            "elsewhere in this corpus, though the remedy here (direct financial penalties "
            "on the contracting authorities) is a distinct remedy shape from anywhere else "
            "in this corpus."
        ),
    },
    "kbr-mopac": {
        "dispute_id": "REAL-KBR-2021",
        "contracting_authority_name": "Mayor's Office for Policing and Crime",
        "bidder_name": "Kellogg Brown & Root Ltd",
        "source_text": (
            "Kellogg Brown & Root Ltd v Mayor's Office for Policing and Crime & Anor "
            "[2021] EWHC 3321 (TCC) — an interim ruling on lifting the automatic "
            "suspension, not a merits trial; the underlying manifest-error allegation was "
            "never itself resolved at this stage.\n\n"
            "The Mayor's Office for Policing and Crime (MOPAC) ran a procurement for a "
            "£400 million framework agreement and call-off contract for facilities "
            "management integrator services, covering contract, financial and operational "
            "management of MOPAC's property supply chain. Kellogg Brown & Root Ltd (KBR) "
            "was the incumbent provider of this role, under a contract originally entered "
            "into in April 2013, and was an unsuccessful bidder in the new competition.\n\n"
            "KBR challenged the award, triggering an automatic suspension on contract "
            "signature. MOPAC applied to the Technology and Construction Court to lift the "
            "suspension so it could proceed to contract with the winning bidder pending "
            "trial of KBR's underlying claim. MOPAC accepted, for the purposes of the "
            "application, that there was a serious issue to be tried on KBR's substantive "
            "allegations, so the application turned on whether damages would be an "
            "adequate remedy for KBR if the suspension were lifted and it later succeeded "
            "at trial.\n\n"
            "Mrs Justice Smith held that damages would be an adequate remedy for KBR. The "
            "judge specifically addressed KBR's argument that redundancies among its staff "
            "working on the existing contract were a form of harm damages could not "
            "compensate, holding that while redundancy is a real detriment to an "
            "individual employee, it was not relevant to the separate legal question of "
            "whether the claimant company itself could be adequately compensated in "
            "damages. The automatic suspension was lifted, allowing MOPAC to proceed to "
            "contract with the winning bidder while KBR's underlying manifest-error "
            "allegation remained technically live and unresolved. This case, like Alstom "
            "and Parkingeye elsewhere in this corpus, is a clear illustration of a "
            "contracting authority successfully defending an interim suspension "
            "application on adequacy-of-damages grounds, without the underlying "
            "substantive dispute ever reaching a merits hearing in this judgment."
        ),
    },
    "sysmex-imperial-college": {
        "dispute_id": "REAL-SYSMEX-2017",
        "contracting_authority_name": "Imperial College Healthcare NHS Trust",
        "bidder_name": "Sysmex (UK) Ltd",
        "source_text": (
            "Sysmex (UK) Ltd v Imperial College Healthcare NHS Trust [2017] EWHC 1824 "
            "(TCC) — an interim ruling on lifting the automatic suspension, not a merits "
            "trial; the underlying allegation was never itself resolved at this stage.\n\n"
            "Imperial College Healthcare NHS Trust ran a procurement, conducted over "
            "roughly fourteen months through several stages of an Invitation to Submit "
            "Detailed Solutions followed by an Invitation to Submit Final Tenders, for a "
            "managed service contract covering pathology equipment and services. By the "
            "final stage only two bidders remained: Abbott and Roche. The Trust notified "
            "Roche that its bid had been rejected and that the Trust intended to award the "
            "contract to Abbott. Sysmex (UK) Ltd, which had a commercial interest in the "
            "outcome, brought proceedings.\n\n"
            "The central allegation was that Abbott's winning bid was based on equipment — "
            "a full blood count analyser referred to as the Alinity Hs — that was, at the "
            "time of the bid, still a prototype product that had not yet received the CE "
            "marking regulatory approval required for clinical use, and that the Trust "
            "could not lawfully accept a bid built around equipment that did not yet have "
            "that approval.\n\n"
            "The dispute reached the Technology and Construction Court on the question of "
            "whether the automatic suspension on contract signature should be lifted "
            "pending trial. Mr Justice Coulson held that damages would be an adequate "
            "remedy for the claimant, quantifiable by reference to the profit margin "
            "reflected in the claimant's own tender, and lifted the suspension so the Trust "
            "could proceed to contract with Abbott. The underlying CE-marking allegation "
            "was never resolved on its merits in this judgment. This case, like Alstom and "
            "Parkingeye elsewhere in this corpus, is an interim suspension ruling, and its "
            "reasoning on the quantifiability of damages by reference to tendered profit "
            "margin became an influential precedent cited in later procurement cases."
        ),
    },
    "vodafone-fcdo": {
        "dispute_id": "REAL-VODAFONE-2021",
        "contracting_authority_name": "Secretary of State for Foreign, Commonwealth and Development Affairs",
        "bidder_name": "Vodafone Ltd",
        "source_text": (
            "Vodafone Ltd v Secretary of State for Foreign, Commonwealth and Development "
            "Affairs & Anor [2021] EWHC 2793 (TCC) — an interim ruling refusing to lift "
            "the automatic suspension, not a merits trial; the underlying allegations were "
            "never themselves resolved at this stage.\n\n"
            "The Foreign, Commonwealth and Development Office and the British Council ran "
            "a procurement for a £184 million framework agreement (referred to as the ECHO "
            "2 contract) for network integration services — a system of secure electronic "
            "communications connecting 532 sites across more than 170 countries. Vodafone "
            "Ltd was an unsuccessful bidder; the contract was awarded to Fujitsu, whose "
            "score was significantly higher than Vodafone's across the evaluation.\n\n"
            "Vodafone's challenge combined two distinct grounds. First, Vodafone argued "
            "that Fujitsu's initial tender had failed to meet a minimum quality threshold "
            "for one specific question, and that although the procurement documents gave "
            "the contracting authorities discretion to exclude a bidder failing such a "
            "threshold, they were not obliged to do so — Vodafone argued this discretion "
            "should have been exercised to exclude Fujitsu regardless of Vodafone's own "
            "score. Second, and separately, Vodafone brought what the parties described as "
            "a 'conventional scoring challenge' disputing the evaluation and scoring of "
            "tenders more generally, notwithstanding the significant gap between the "
            "parties' overall scores.\n\n"
            "Vodafone's challenge triggered an automatic suspension, and the contracting "
            "authorities applied to lift it. Mr Justice Kerr declined to lift the "
            "suspension, allowing Vodafone's underlying claims to proceed to a full "
            "hearing rather than letting the contract signature go ahead. The judgment is "
            "notable for its observations on how trials of preliminary issues should be "
            "conducted in procurement disputes of this kind. This case, like Alstom and "
            "Parkingeye elsewhere in this corpus, is an interim suspension ruling — but "
            "unlike those two cases the ruling favoured the challenger rather than the "
            "contracting authority, mirroring the same interim-stage outcome as Parkingeye "
            "specifically."
        ),
    },
    "draeger-london-fire": {
        "dispute_id": "REAL-DRAEGER-2021",
        "contracting_authority_name": "London Fire Commissioner",
        "bidder_name": "Draeger Safety UK Ltd",
        "source_text": (
            "Draeger Safety UK Ltd v The London Fire Commissioner [2021] EWHC 2221 (TCC) "
            "— an interim ruling refusing to lift the automatic suspension, not a merits "
            "trial; the underlying allegations were never themselves resolved at this "
            "stage.\n\n"
            "The London Fire Commissioner (on behalf of the London Fire Brigade) ran a "
            "procurement, initiated in August 2020, for a ten-year contract for firefighter "
            "respiratory protective equipment (RPE), together with associated repair and "
            "maintenance services. The stated aim of the procurement was to obtain lighter, "
            "easier-to-use equipment to improve both firefighter safety and public service "
            "delivery. Draeger Safety UK Ltd, a company providing medical and safety "
            "technology, was the incumbent supplier of RPE to the Brigade under a contract "
            "originally awarded in 2010, and was an unsuccessful bidder in the new "
            "competition.\n\n"
            "Draeger's challenge to the award triggered an automatic suspension on "
            "contract signature. The London Fire Brigade applied to the Technology and "
            "Construction Court to lift the suspension, while Draeger separately applied "
            "for an expedited trial of its underlying claim.\n\n"
            "Mrs Justice O'Farrell refused the Brigade's application to lift the automatic "
            "suspension, finding that damages would be an inadequate remedy for both "
            "sides — for Draeger, given the loss of the contract and associated business "
            "impact, and for the Brigade, given the operational safety consequences of "
            "delay to introducing improved equipment. The judgment noted that the Court's "
            "practical ability to accommodate an expedited trial on a timetable that would "
            "not itself risk seriously delaying the new equipment's introduction was an "
            "important factor in the decision. This case, like Parkingeye and Vodafone "
            "elsewhere in this corpus, is an interim suspension ruling that favoured the "
            "challenger; the underlying manifest-error and evaluation allegations were not "
            "resolved on their merits in this judgment."
        ),
    },
    "one-medicare-nhs-northants": {
        "dispute_id": "REAL-ONEMEDICARE-2025",
        "contracting_authority_name": "NHS Northamptonshire Integrated Care Board",
        "bidder_name": "One Medicare (t/a One Primary Care)",
        "source_text": (
            "One Medicare (t/a One Primary Care) v NHS Northamptonshire Integrated Care "
            "Board [2025] EWHC 63 (TCC) — an interim ruling on lifting the automatic "
            "suspension, not a merits trial; the underlying allegations were never "
            "themselves resolved at this stage.\n\n"
            "NHS Northamptonshire Integrated Care Board (ICB) issued an Invitation to "
            "Tender for a contract to provide an Urgent Care Centre, published on 23 June "
            "2023 with submissions closing on 27 June 2023. The evaluation criteria "
            "comprised price (assessed pass/fail), quality (weighted 90%, with a minimum "
            "60% score required to pass), and social value (weighted 10%). Tenderers were "
            "notified that DHU Healthcare CIC's bid had been identified as the most "
            "economically advantageous, and the ICB intended to award the contract to DHU. "
            "One Medicare, trading as One Primary Care (OPC), the incumbent provider, was "
            "an unsuccessful bidder.\n\n"
            "OPC challenged the award, alleging breaches of transparency, breaches in how "
            "the bids were scored, and a conflict of interest affecting the evaluation. The "
            "challenge triggered an automatic suspension, and the ICB applied to the "
            "Technology and Construction Court to lift it pending trial of OPC's "
            "underlying claims.\n\n"
            "The court held that the balance of convenience firmly favoured lifting the "
            "suspension. The judge found that if the suspension remained in place, the ICB "
            "would suffer harm extending beyond purely financial loss, including evidence "
            "that the successful bidder's services would improve the quality of patient "
            "care sooner than if the incumbent continued. The judge noted that OPC's "
            "absence of a standard cross-undertaking in damages to the ICB was, if not the "
            "sole reason, then the strongest reason to grant the application. The "
            "suspension was lifted, and OPC's separate application for an expedited trial "
            "was refused. This case, like Alstom and Bechtel-adjacent suspension rulings "
            "elsewhere in this corpus, is an interim ruling favouring the contracting "
            "authority; the underlying transparency, scoring and conflict-of-interest "
            "allegations were not resolved on their merits in this judgment."
        ),
    },
    "robert-heath-heating-orbit": {
        "dispute_id": "REAL-ROBERTHEATHHEATING-2024",
        "contracting_authority_name": "Orbit Group Ltd",
        "bidder_name": "Robert Heath Heating Ltd",
        "source_text": (
            "Robert Heath Heating Ltd v Orbit Group Ltd [2024] EWHC 3039 (TCC) — an "
            "interim ruling on lifting the automatic suspension, not a merits trial; the "
            "underlying allegations were never themselves resolved at this stage.\n\n"
            "Orbit Group Ltd, a housing association, ran a procurement for domestic "
            "heating service contracts. Robert Heath Heating Ltd (RHH) was an unsuccessful "
            "bidder; the contract was awarded to Aaron Services Ltd. RHH challenged the "
            "award on two distinct grounds: first, that a former Orbit employee involved "
            "in the procurement had moved to the parent company of the successful bidder, "
            "creating an undisclosed conflict of interest; and second, that RHH's own "
            "tender had been scored on the basis of opaque reasoning, compounded by "
            "Orbit's withholding of the evaluation disclosure RHH needed to properly assess "
            "its complaint.\n\n"
            "RHH's challenge triggered an automatic suspension. RHH sought early specific "
            "disclosure of the evaluation documents, while Orbit applied to lift the "
            "suspension so it could proceed to contract with Aaron Services pending trial. "
            "The court, applying the American Cyanamid framework used for interim "
            "injunctions generally (this procurement pre-dated the Procurement Act 2023's "
            "new statutory suspension test), found that there were in fact two separate "
            "serious issues to be tried — one relating to the alleged conflict of "
            "interest, and one relating to the tender-scoring complaint. Notwithstanding "
            "that finding, the court held that RHH would not be permitted to freeze the "
            "entire procurement while those issues were resolved at trial, concluding that "
            "damages were an entirely adequate remedy for RHH if it ultimately succeeded. "
            "The suspension was lifted. This case, like Alstom and Bechtel-adjacent "
            "suspension rulings elsewhere in this corpus, is an interim ruling favouring "
            "the contracting authority on adequacy-of-damages grounds; the underlying "
            "conflict-of-interest and scoring allegations were not resolved on their "
            "merits in this judgment."
        ),
    },
}
