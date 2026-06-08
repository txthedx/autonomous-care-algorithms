"""The CDS engine layer: catalog, dispatch, and interfaces over the core.

The deterministic algorithms live in `conditions/`. This package adds the
machine-readable registry and (in later phases) dispatch and the MCP/REST
interfaces. The core is never modified by this layer. See docs/architecture.md.
"""

from .registry import (
    DISCLAIMER,
    condition_keys,
    describe,
    get_schema,
    list_conditions,
    missing_inputs,
    run,
    validate,
)

__all__ = [
    "DISCLAIMER",
    "condition_keys",
    "describe",
    "get_schema",
    "list_conditions",
    "missing_inputs",
    "run",
    "validate",
]
