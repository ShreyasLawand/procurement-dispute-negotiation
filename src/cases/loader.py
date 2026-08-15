"""
Turns a real-case source text into the DisputeScenario the batch evaluator runs against.

WHY THIS CACHES — this is the load-bearing part, not an optimisation:

`ScenarioExtractionAgent` is an LLM call, so extracting the same case twice gives two
slightly different DisputeScenarios. A V3-vs-V4 Court-prompt ablation that extracted
independently for each arm would therefore be comparing two prompts across two
*different* scenarios, confounding the one variable the experiment exists to isolate.

So extraction happens once per case, the result is written to
`batch_results/_scenarios/<slug>.json`, and every subsequent batch reuses that exact
file. Pass `refresh=True` to deliberately re-extract (which invalidates comparability
with any batch already run against the cached version).

The cached file is also the record of *what was actually evaluated*: extraction is
itself a fallible LLM step, so a results table is only interpretable alongside the
scenario it ran on.
"""

import json
from pathlib import Path

from src.agents.extraction_agent import ScenarioExtractionAgent
from src.cases.real_cases import REAL_CASES
from src.schemas.agent_state import DisputeScenario

DEFAULT_CACHE_DIR = Path("batch_results") / "_scenarios"


def cached_scenario_path(slug: str, cache_dir: Path | str = DEFAULT_CACHE_DIR) -> Path:
    return Path(cache_dir) / f"{slug}.json"


def load_real_scenario(
    slug: str,
    cache_dir: Path | str = DEFAULT_CACHE_DIR,
    refresh: bool = False,
) -> DisputeScenario:
    """
    Returns the DisputeScenario for a real case, extracting it only if not already
    cached. Raises KeyError for an unknown slug.
    """
    if slug not in REAL_CASES:
        raise KeyError(f"Unknown case {slug!r}. Available: {', '.join(sorted(REAL_CASES))}")

    path = cached_scenario_path(slug, cache_dir)
    if path.exists() and not refresh:
        return DisputeScenario(**json.loads(path.read_text(encoding="utf-8")))

    case = REAL_CASES[slug]
    print(f"[{slug}] Extracting scenario from source text (this is an LLM call)...")
    scenario = ScenarioExtractionAgent().extract_scenario(
        case["source_text"],
        dispute_id=case["dispute_id"],
        contracting_authority_name=case["contracting_authority_name"],
        bidder_name=case["bidder_name"],
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(scenario.model_dump(), indent=2, default=str), encoding="utf-8"
    )
    print(f"[{slug}] Cached extracted scenario -> {path}")
    return scenario
