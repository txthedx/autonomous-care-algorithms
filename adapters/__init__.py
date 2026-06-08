"""Optional note->features extraction adapters.

This package is the bridge from a free-text clinical note to the structured
features the deterministic engine consumes. It is separate from the core, sees
the only PHI in the system, and (for the Claude extractor) depends on the
optional `[adapter]` extra. See docs/architecture.md and docs/adapter.md.
"""

from .extraction import (
    ClaudeExtractor,
    DictExtractor,
    Extractor,
    assess_note,
    union_schema,
)

__all__ = [
    "ClaudeExtractor",
    "DictExtractor",
    "Extractor",
    "assess_note",
    "union_schema",
]
