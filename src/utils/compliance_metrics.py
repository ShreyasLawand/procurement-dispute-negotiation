"""
Structural compliance instrumentation.

Llama 3.1 does not reliably return the JSON shape the prompts ask for. The codebase
already absorbs that in three places — Pydantic `mode="before"` validators that coerce
stray dicts/bools into strings, a brace-finding fallback when `json.loads` fails on the
raw response, and a regeneration loop when a round response repeats an earlier one.

All three were silent. They fixed the problem and left no trace, which means the model's
actual structural reliability was invisible: a run where every single response needed
repair looked identical to one where none did.

This module counts them, giving a **structural compliance rate** — the share of
structured LLM responses that parsed and validated with no repair at all. That number is
worth reporting on its own (it characterises an 8B local model doing constrained
generation), and it is the control that tells you whether a prompt change bought its
accuracy at the cost of parseability.

Response scoping
----------------
A single response can trigger several field coercions, so summing repair *events* and
dividing by response count is not a rate — it can exceed 1 and the complement can go
negative. Instead each response gets a scope: `parse_llm_json` opens one, any coercion
during the subsequent model validation marks it dirty, and the next `parse_llm_json`
(or `snapshot`) closes it. `clean_responses / structured_responses` is then a true
proportion in [0, 1].

Scopes are thread-local, because api/sessions.py drives the graph from a background
thread while the main thread serves SSE.
"""

from collections import Counter
import json
import threading

_local = threading.local()


class ComplianceMetrics:
    """Process-wide counters for LLM structural-compliance events."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            # Denominator: every structured response we attempted to parse.
            self.responses = Counter()
            # Responses that needed no repair of any kind.
            self.clean_responses = Counter()
            # A response that failed strict json.loads and needed brace-extraction.
            self.json_fallbacks = Counter()
            # Individual fields that arrived as something other than the requested type.
            self.field_coercions = Counter()
            # A round response regenerated because it repeated an earlier statement.
            self.repetition_retries = Counter()
            # A response that could not be parsed at all, even after fallback.
            self.parse_failures = Counter()
        _local.site = None
        _local.dirty = False

    # --- response scoping -------------------------------------------------

    def _close_scope(self) -> None:
        """Attributes the open response scope, if any, as clean or repaired."""
        site = getattr(_local, "site", None)
        if site is None:
            return
        if not getattr(_local, "dirty", False):
            with self._lock:
                self.clean_responses[site] += 1
        _local.site = None
        _local.dirty = False

    def open_response(self, agent: str, call: str) -> None:
        self._close_scope()
        with self._lock:
            self.responses[f"{agent}.{call}"] += 1
        _local.site = f"{agent}.{call}"
        _local.dirty = False

    def _mark_dirty(self) -> None:
        if getattr(_local, "site", None) is not None:
            _local.dirty = True

    # --- event recording --------------------------------------------------

    def record_json_fallback(self, agent: str, call: str) -> None:
        with self._lock:
            self.json_fallbacks[f"{agent}.{call}"] += 1
        self._mark_dirty()

    def record_parse_failure(self, agent: str, call: str) -> None:
        with self._lock:
            self.parse_failures[f"{agent}.{call}"] += 1
        self._mark_dirty()

    def record_field_coercion(self, model: str, field: str, received: type) -> None:
        with self._lock:
            self.field_coercions[f"{model}.{field}:{received.__name__}"] += 1
        self._mark_dirty()

    def record_repetition_retry(self, agent: str) -> None:
        # Deliberately does NOT mark the scope dirty: a repetitive response is a
        # content-quality problem, not a structural-validity one. Counted separately.
        with self._lock:
            self.repetition_retries[agent] += 1

    # --- reporting --------------------------------------------------------

    def snapshot(self) -> dict:
        """Aggregate view plus per-site breakdowns, safe to serialise into a log."""
        self._close_scope()
        with self._lock:
            total = sum(self.responses.values())
            clean = sum(self.clean_responses.values())
            return {
                "structured_responses": total,
                "clean_responses": clean,
                "structural_compliance_rate": round(clean / total, 4) if total else None,
                "json_fallbacks": sum(self.json_fallbacks.values()),
                "field_coercions": sum(self.field_coercions.values()),
                "parse_failures": sum(self.parse_failures.values()),
                "repetition_retries": sum(self.repetition_retries.values()),
                "structural_compliance_rate_note": (
                    "clean_responses / structured_responses — the share of structured LLM "
                    "responses needing no brace-extraction fallback and no field coercion. "
                    "A true proportion in [0,1]; one response may contribute several "
                    "field_coercions, which is why those are counted separately."
                ),
                "by_site": {
                    "responses": dict(self.responses),
                    "clean_responses": dict(self.clean_responses),
                    "json_fallbacks": dict(self.json_fallbacks),
                    "field_coercions": dict(self.field_coercions),
                    "parse_failures": dict(self.parse_failures),
                    "repetition_retries": dict(self.repetition_retries),
                },
            }


metrics = ComplianceMetrics()


def parse_llm_json(raw_text: str, *, agent: str, call: str) -> dict:
    """
    Parses a structured LLM response, recording whether it needed repair.

    Replaces a try/except brace-finding block that was duplicated at ten call sites
    across the five agents. Behaviour is unchanged — strict parse first, brace
    extraction as fallback — except that failures now raise with the offending text
    attached instead of a bare JSONDecodeError.
    """
    metrics.open_response(agent, call)
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        metrics.record_json_fallback(agent, call)
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start == -1 or end == 0:
            metrics.record_parse_failure(agent, call)
            raise ValueError(
                f"{agent}.{call}: response contained no JSON object. Raw text: {raw_text[:500]!r}"
            )
        try:
            return json.loads(raw_text[start:end])
        except json.JSONDecodeError as e:
            metrics.record_parse_failure(agent, call)
            raise ValueError(
                f"{agent}.{call}: could not parse JSON even after brace extraction "
                f"({e}). Raw text: {raw_text[:500]!r}"
            ) from e
