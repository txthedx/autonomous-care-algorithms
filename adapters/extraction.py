"""Note -> structured features extraction (the optional, PHI-bearing edge).

Phase 5 of the system (see docs/architecture.md). This adapter is the **only**
component that sees a raw clinical note. It turns a note into the structured
features the deterministic engine consumes, then runs the applicable algorithms.

It is deliberately **separate from the core**:
  - It depends on an LLM (the Anthropic SDK, an optional `[adapter]` extra).
  - In real use it sends the note to the model using the **caller's** API key,
    in the **caller's** secure environment. PHI never reaches the open engine.
  - It stores nothing and logs nothing.

The orchestration takes an injected `Extractor`, so it can run with a deterministic
extractor (no LLM) for tests and examples, or with `ClaudeExtractor` in production.

Not a medical device. See DISCLAIMER.md.
"""

from __future__ import annotations

from typing import Any, Protocol

from engine import dispatch, registry


class Extractor(Protocol):
    """Turns a note plus a JSON Schema into a (partial) features dict."""

    def __call__(self, note: str, schema: dict[str, Any]) -> dict[str, Any]: ...


class DictExtractor:
    """A non-LLM extractor that returns preset features (for tests and examples).

    Returns only the keys that appear in the requested schema, so it behaves like
    a real extractor that fills what it can and omits the rest.
    """

    def __init__(self, features: dict[str, Any]):
        self._features = dict(features)

    def __call__(self, note: str, schema: dict[str, Any]) -> dict[str, Any]:
        properties = schema.get("properties", {})
        return {k: v for k, v in self._features.items() if k in properties}


def union_schema(conditions: list[str]) -> dict[str, Any]:
    """Merge the input schemas of several conditions into one object schema.

    The union describes every field any of the conditions might use. Nothing is
    marked required — a note will rarely contain them all; the engine reports the
    gaps. Field names are shared across conditions (vitals, labs, demographics),
    so a collision keeps the first definition.
    """
    properties: dict[str, Any] = {}
    for condition in conditions:
        for name, prop in registry.get_schema(condition)["properties"].items():
            properties.setdefault(name, prop)
    return {
        "type": "object",
        "properties": properties,
        "required": [],
        "additionalProperties": False,
    }


def assess_note(
    note: str,
    extractor: Extractor,
    presentation: str | None = None,
) -> dict[str, Any]:
    """Extract features from a note and run every algorithm they satisfy.

    Args:
        note: Free-text clinical note (PHI — handled in the caller's environment).
        extractor: An `Extractor` (e.g. `ClaudeExtractor` or `DictExtractor`).
        presentation: Optional presentation tag to focus the catalog.

    Returns:
        `extracted_features` plus the dispatch result (`applicable`,
        `needs_more_data`, `errors`, `disclaimer`).
    """
    candidates = (
        dispatch.by_presentation(presentation)
        if presentation is not None
        else list(registry.condition_keys())
    )
    schema = union_schema(candidates)
    features = extractor(note, schema)
    result = dispatch.run_applicable(features, presentation)
    return {"extracted_features": features, **result}


class ClaudeExtractor:
    """An `Extractor` that uses Claude tool-use to fill the feature schema.

    The note is sent to the Anthropic API with the caller's key. The model is
    instructed to report only values explicitly supported by the note and to omit
    anything it cannot confirm — extraction never invents clinical facts. A
    pre-built `client` may be injected (used in tests); otherwise the Anthropic
    SDK is imported lazily and a client is constructed from the environment.
    """

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model or self.DEFAULT_MODEL
        if client is not None:
            self._client = client
        else:
            import anthropic

            self._client = (
                anthropic.Anthropic(api_key=api_key)
                if api_key
                else anthropic.Anthropic()
            )

    @staticmethod
    def _tool(schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "report_features",
            "description": (
                "Report the structured clinical features that are explicitly "
                "supported by the note. Omit any field the note does not state."
            ),
            "input_schema": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": [],
            },
        }

    @staticmethod
    def _system() -> str:
        return (
            "You extract structured clinical features from a clinical note for a "
            "deterministic decision-support engine. Report only values explicitly "
            "stated or unambiguously documented in the note. Do not infer, guess, "
            "or assume defaults. Omit any field the note does not support. Use the "
            "exact enum values and units defined in the tool schema."
        )

    @staticmethod
    def _parse(message: Any, schema: dict[str, Any]) -> dict[str, Any]:
        properties = schema.get("properties", {})
        for block in message.content:
            if getattr(block, "type", None) == "tool_use" and block.name == "report_features":
                return {k: v for k, v in dict(block.input).items() if k in properties}
        return {}

    def __call__(self, note: str, schema: dict[str, Any]) -> dict[str, Any]:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._system(),
            tools=[self._tool(schema)],
            tool_choice={"type": "tool", "name": "report_features"},
            messages=[{"role": "user", "content": note}],
        )
        return self._parse(message, schema)
