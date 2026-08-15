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
}
