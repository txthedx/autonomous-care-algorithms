"""Tests for qSOFA."""

from __future__ import annotations

import pytest

from conditions.sepsis.qsofa import QsofaFeatures, qsofa_assessment, qsofa_score

_DEFAULT = {"respiratory_rate_per_minute": 16, "glasgow_coma_scale": 15, "systolic_bp_mmhg": 120}


def _f(**o: int) -> QsofaFeatures:
    return QsofaFeatures(**(_DEFAULT | o))


class TestCriteria:
    def test_all_normal_zero(self) -> None:
        assert qsofa_score(_f()) == 0

    def test_rr_22_scores(self) -> None:
        assert qsofa_score(_f(respiratory_rate_per_minute=22)) == 1

    def test_rr_21_does_not_score(self) -> None:
        assert qsofa_score(_f(respiratory_rate_per_minute=21)) == 0

    def test_gcs_14_scores(self) -> None:
        assert qsofa_score(_f(glasgow_coma_scale=14)) == 1

    def test_gcs_15_does_not_score(self) -> None:
        assert qsofa_score(_f(glasgow_coma_scale=15)) == 0

    def test_sbp_100_scores(self) -> None:
        assert qsofa_score(_f(systolic_bp_mmhg=100)) == 1

    def test_sbp_101_does_not_score(self) -> None:
        assert qsofa_score(_f(systolic_bp_mmhg=101)) == 0

    def test_max_three(self) -> None:
        assert qsofa_score(_f(respiratory_rate_per_minute=24, glasgow_coma_scale=13, systolic_bp_mmhg=90)) == 3


class TestBands:
    def test_one_is_lower_risk(self) -> None:
        r = qsofa_assessment(_f(respiratory_rate_per_minute=22))
        assert r.score == 1 and r.risk_band == "lower_risk"

    def test_two_is_higher_risk(self) -> None:
        r = qsofa_assessment(_f(respiratory_rate_per_minute=22, systolic_bp_mmhg=100))
        assert r.score == 2 and r.risk_band == "higher_risk"

    def test_higher_risk_action_mentions_organ_dysfunction(self) -> None:
        r = qsofa_assessment(_f(glasgow_coma_scale=13, systolic_bp_mmhg=90))
        assert "organ dysfunction" in r.recommended_action.lower()

    def test_lower_risk_notes_not_ruled_out(self) -> None:
        r = qsofa_assessment(_f())
        assert "not rule out" in r.recommended_action.lower()


class TestOutputAndValidation:
    def test_citations(self) -> None:
        assert "Singer 2016" in qsofa_assessment(_f()).citations

    def test_caveats_not_a_diagnosis(self) -> None:
        text = " ".join(qsofa_assessment(_f()).population_caveats).lower()
        assert "not a diagnosis" in text

    def test_negative_rr_raises(self) -> None:
        with pytest.raises(ValueError):
            qsofa_score(_f(respiratory_rate_per_minute=-1))

    def test_bad_gcs_raises(self) -> None:
        with pytest.raises(ValueError):
            qsofa_score(_f(glasgow_coma_scale=2))
