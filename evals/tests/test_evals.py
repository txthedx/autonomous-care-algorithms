"""Tests for the end-to-end eval harness."""

from __future__ import annotations

import pytest

from evals import VIGNETTES, run_suite, run_vignette
from evals.vignettes import Vignette


class TestSuite:
    def test_suite_all_pass(self) -> None:
        summary = run_suite()
        assert summary["failed"] == 0, [
            (r.name, [c.description for c in r.checks if not c.passed])
            for r in summary["results"] if not r.passed
        ]
        assert summary["passed"] == summary["total"] == len(VIGNETTES)

    def test_meaningful_coverage(self) -> None:
        assert len(VIGNETTES) >= 8
        # The suite touches a spread of domains, not just one.
        covered = {v.expect_applicable[0] for v in VIGNETTES}
        assert len(covered) >= 6


class TestPerVignette:
    @pytest.mark.parametrize("vignette", VIGNETTES, ids=lambda v: v.name)
    def test_vignette_passes(self, vignette: Vignette) -> None:
        result = run_vignette(vignette)
        failures = [c.description for c in result.checks if not c.passed]
        assert result.passed, failures

    def test_multi_algorithm_vignette_runs_both(self) -> None:
        multi = next(v for v in VIGNETTES if v.name == "multi_renal_and_syncope")
        result = run_vignette(multi)
        applicable = {r["key"] for r in result.output["applicable"]}
        assert {"kdigo", "sfsr"} <= applicable


class TestHarnessActuallyChecks:
    """A wrong expectation must fail — proving the harness isn't a no-op."""

    def test_bad_expectation_fails(self) -> None:
        good = VIGNETTES[0]
        broken = Vignette(
            name="broken",
            presentation=good.presentation,
            note=good.note,
            features=good.features,
            expect_applicable=good.expect_applicable,
            expect_results=(("heart", "score", 999),),  # wrong on purpose
        )
        assert run_vignette(broken).passed is False

    def test_missing_field_reported_not_crashed(self) -> None:
        good = VIGNETTES[0]
        broken = Vignette(
            name="broken_field",
            presentation=good.presentation,
            note=good.note,
            features=good.features,
            expect_results=(("heart", "no_such_field", 1),),
            expect_applicable=(),
        )
        result = run_vignette(broken)
        assert result.passed is False  # missing field -> failed check, no crash
