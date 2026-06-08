"""MCP server exposing the CDS engine as agent-callable tools.

Phase 3 of the engine (see docs/architecture.md). A Claude-based clinical
assistant can call these tools in real time while drafting a note: list the
catalog, fetch a condition's input schema, run one algorithm, or hand the engine
a bag of features and ask which algorithms apply.

The Model Context Protocol SDK is an **optional** dependency (`pip install
".[mcp]"`). The tool logic below is plain functions over `engine.registry` and
`engine.dispatch` — importable and testable without the SDK. Only `build_server`
and `main` touch `mcp`, and they import it lazily, so importing this module never
requires the SDK.

Stateless: nothing is stored and no inputs are logged. Not a medical device;
every result carries the disclaimer. See DISCLAIMER.md.
"""

from __future__ import annotations

from typing import Any

from . import dispatch, registry

SERVER_NAME = "autonomous-care-algorithms"


# --- Tool logic (plain functions, no MCP dependency) ------------------------


def list_conditions() -> list[dict[str, Any]]:
    """Return the catalog: each algorithm's key, label, and presentation tags."""
    return registry.list_conditions()


def list_presentations() -> list[str]:
    """Return the presentation tags the catalog is indexed by."""
    return dispatch.presentations()


def get_condition_schema(condition: str) -> dict[str, Any]:
    """Return the JSON Schema of input features for one condition."""
    return registry.get_schema(condition)


def describe_condition(condition: str) -> dict[str, Any]:
    """Return a condition's full record: label, presentations, input schema, citations note."""
    return registry.describe(condition)


def run_algorithm(condition: str, features: dict[str, Any]) -> dict[str, Any]:
    """Run one algorithm over its structured features.

    Returns `{"ok": True, "result": ..., "disclaimer": ...}` on success, or
    `{"ok": False, "error": ..., "missing_inputs": [...]}` so the caller can ask
    the clinician for what's missing rather than failing hard.
    """
    if condition not in registry.condition_keys():
        return {"ok": False, "error": f"unknown condition '{condition}'",
                "missing_inputs": []}
    errors = registry.validate(condition, features)
    if errors:
        return {"ok": False, "error": "; ".join(errors),
                "missing_inputs": registry.missing_inputs(condition, features)}
    try:
        result = registry.run(condition, features)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "missing_inputs": []}
    return {"ok": True, "result": result, "disclaimer": registry.DISCLAIMER}


def suggest_algorithms(
    features: dict[str, Any],
    presentation: str | None = None,
) -> list[dict[str, Any]]:
    """Rank algorithms by how close they are to runnable on the given features."""
    return dispatch.suggest(features, presentation)


def run_applicable(
    features: dict[str, Any],
    presentation: str | None = None,
) -> dict[str, Any]:
    """Run every algorithm whose inputs the given features satisfy.

    Returns `applicable` (results), `needs_more_data` (missing inputs per
    algorithm), `errors`, and a disclaimer. Optionally narrowed to a clinical
    presentation tag (e.g. "chest pain").
    """
    return dispatch.run_applicable(features, presentation)


# --- MCP wiring (lazy import of the optional SDK) ---------------------------


def build_server() -> Any:
    """Build and return the FastMCP server with all tools registered.

    Imports the MCP SDK lazily; requires `pip install ".[mcp]"`.
    """
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(SERVER_NAME)
    server.add_tool(list_conditions)
    server.add_tool(list_presentations)
    server.add_tool(get_condition_schema)
    server.add_tool(describe_condition)
    server.add_tool(run_algorithm)
    server.add_tool(suggest_algorithms)
    server.add_tool(run_applicable)
    return server


def main() -> None:
    """Run the MCP server over stdio."""
    build_server().run()


if __name__ == "__main__":
    main()
