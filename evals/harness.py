"""End-to-end eval harness: note -> features -> engine -> expected outcomes.

Runs each vignette through the extraction adapter and the engine and checks that
the expected algorithms are surfaced with the expected results. By default it
uses `DictExtractor` (deterministic, no LLM), so the whole stack is exercised in
CI; pass an `extractor_factory` to run a live LLM-in-the-loop eval.

Run as a script for a summary:

    python -m evals.harness
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from adapters import DictExtractor, assess_note

from .vignettes import VIGNETTES, Vignette

_MISSING = object()


@dataclass(frozen=True)
class Check:
    description: str
    passed: bool


@dataclass(frozen=True)
class VignetteResult:
    name: str
    passed: bool
    checks: tuple[Check, ...]
    output: dict[str, Any]


def run_vignette(
    vignette: Vignette,
    extractor: Any | None = None,
) -> VignetteResult:
    """Run one vignette end to end and check its expectations."""
    extractor = extractor or DictExtractor(dict(vignette.features))
    output = assess_note(vignette.note, extractor, presentation=vignette.presentation)
    results = {record["key"]: record["result"] for record in output["applicable"]}

    checks: list[Check] = []
    for key in vignette.expect_applicable:
        checks.append(Check(f"{key} is applicable", key in results))
    for condition, field, expected in vignette.expect_results:
        actual = results.get(condition, {}).get(field, _MISSING)
        checks.append(Check(
            f"{condition}.{field} == {expected!r} (got {actual!r})",
            actual == expected,
        ))

    return VignetteResult(
        name=vignette.name,
        passed=all(check.passed for check in checks),
        checks=tuple(checks),
        output=output,
    )


def run_suite(
    vignettes: tuple[Vignette, ...] = VIGNETTES,
    extractor_factory: Callable[[Vignette], Any] | None = None,
) -> dict[str, Any]:
    """Run all vignettes and return a summary.

    Args:
        vignettes: The vignettes to run.
        extractor_factory: Optional `vignette -> Extractor`. Defaults to a
            deterministic `DictExtractor` built from each vignette's features.

    Returns:
        `{total, passed, failed, results}` where `results` is a list of
        `VignetteResult`.
    """
    results = [
        run_vignette(v, extractor_factory(v) if extractor_factory else None)
        for v in vignettes
    ]
    passed = sum(1 for r in results if r.passed)
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def main() -> None:
    summary = run_suite()
    for result in summary["results"]:
        mark = "PASS" if result.passed else "FAIL"
        print(f"[{mark}] {result.name}")
        if not result.passed:
            for check in result.checks:
                if not check.passed:
                    print(f"        - {check.description}")
    print(f"\n{summary['passed']}/{summary['total']} vignettes passed.")
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
