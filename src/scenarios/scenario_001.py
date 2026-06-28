from src.schemas.agent_state import DisputeScenario

scoring_challenge = DisputeScenario(
    dispute_id="F21-001",
    title="Scoring Methodology Challenge — Construction Framework",
    description=(
        "BuildRight Ltd submitted a bid for a £2m construction framework. "
        "They were ranked second and excluded from the framework. "
        "They are challenging the scoring methodology, alleging that the "
        "quality scoring criteria were applied inconsistently and that the "
        "winning bidder received unjustifiably high marks in the 'social value' "
        "category despite providing less detailed evidence."
    ),
    contract_value_gbp=2_000_000,
    dispute_type="scoring_challenge",
    procedural_stage="standstill",
    contracting_authority_name="Fusion21",
    bidder_name="BuildRight Ltd"
)