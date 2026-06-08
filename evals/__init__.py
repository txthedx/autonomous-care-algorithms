"""End-to-end evaluation of the full stack: note -> features -> engine.

Synthetic primary-care vignettes run through the extraction adapter and the
engine, asserting the right algorithms surface with the right results. See
docs/architecture.md (Phase 6).
"""

from .harness import Check, VignetteResult, run_suite, run_vignette
from .vignettes import VIGNETTES, Vignette

__all__ = [
    "VIGNETTES",
    "Check",
    "Vignette",
    "VignetteResult",
    "run_suite",
    "run_vignette",
]
