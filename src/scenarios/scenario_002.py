from src.schemas.agent_state import DisputeScenario

# This scenario is deliberately UNAMBIGUOUS — a clear-cut manifest error,
# unlike scenario_001's genuinely debatable judgment call. Used as a
# discriminative validity check: does the Court agent reliably find manifest
# error here, consistently, and faster than in the ambiguous scenario_001?

mathematical_scoring_error = DisputeScenario(
    dispute_id="F21-002",
    title="Mathematical Scoring Error — Facilities Management Contract",
    description=(
        "GreenServe Ltd submitted a bid for a £3.5m facilities management "
        "contract and was ranked third, narrowly missing the award by 0.4 "
        "points overall.\n\n"
        "DISPUTED ISSUE: Arithmetic error in the published scoring calculation.\n"
        "\n"
        "The Framework Document (Section 5.1) states that the final score for "
        "each bidder is calculated as: (Quality Score x 0.6) + (Price Score x 0.4).\n"
        "\n"
        "GreenServe Ltd's individually published sub-scores were:\n"
        "- Quality Score: 85/100\n"
        "- Price Score: 78/100\n"
        "- Correct final score per the published formula: (85 x 0.6) + (78 x 0.4) "
        "= 51.0 + 31.2 = 82.2/100\n"
        "\n"
        "However, the final scorecard issued to GreenServe Ltd by Fusion21 shows "
        "a final score of 78.6/100 — a 3.6 point discrepancy from the correct "
        "arithmetic result. This 3.6 point gap is larger than the 0.4 point "
        "margin by which GreenServe Ltd missed the award.\n"
        "\n"
        "GreenServe Ltd has independently re-calculated the score using the "
        "published formula and the published sub-scores (both of which are "
        "publicly available in the tender documentation) and formally alleges "
        "a manifest arithmetic error in the final score calculation, requesting "
        "immediate correction and re-ranking."
    ),
    contract_value_gbp=3_500_000,
    dispute_type="scoring_challenge",  # kept consistent with scenario_001 for comparability
    procedural_stage="standstill",
    contracting_authority_name="Fusion21",
    bidder_name="GreenServe Ltd"
)