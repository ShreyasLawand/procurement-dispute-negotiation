from src.schemas.agent_state import DisputeScenario

scoring_challenge = DisputeScenario(
    dispute_id="F21-001",
    title="Scoring Methodology Challenge — Construction Framework",
    description=(
        "BuildRight Ltd submitted a bid for a £2m construction framework and was "
        "ranked second, narrowly missing the framework by 1.2 points overall. "
        "\n\nDISPUTED CRITERION: Quality Criterion Q4 - 'Social Value: Community Benefit'\n"
        "- BuildRight Ltd's submission: 14 pages, including a detailed local "
        "employment plan, 3 named subcontractor partnerships, and a 5-year "
        "community investment schedule. Score awarded: 62/100.\n"
        "- Winning bidder (Ironclad Construction): 4 pages, general commitments "
        "to 'support local employment' with no named partnerships or schedule. "
        "Score awarded: 88/100.\n"
        "\nBuildRight Ltd alleges this scoring gap is a manifest error, since the "
        "published evaluation criteria (Framework Document, Section 4.3) state "
        "that Social Value scoring should be based on 'specificity, evidence, "
        "and named commitments.' BuildRight Ltd has formally requested the "
        "evaluator's scoring notes for Q4 for both bids."
    ),
    contract_value_gbp=2_000_000,
    dispute_type="scoring_challenge",
    procedural_stage="standstill",
    contracting_authority_name="Fusion21",
    bidder_name="BuildRight Ltd"
)