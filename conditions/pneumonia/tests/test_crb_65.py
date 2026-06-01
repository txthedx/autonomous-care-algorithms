"""Tests for the CRB-65 severity score.

Coverage targets:
- Each of the four criteria contributes one point independently.
- Threshold boundaries score correctly.
- Total score range 0 to 4.
- Severity bands and dispositions at each score.
- Invalid input raises.
"""

from __future__ import annotations

import pytest

from conditions.pneumonia.crb_65 import (
    Crb65Features,
    crb_65_assessment,
    crb_65_criteria,
    crb_65_score,
)


def _features(
    *,
    age_years: int = 40,
    confusion: bool = False,
    respiratory_rate_per_minute: int = 16,
    systolic_bp_mmhg: int = 120,
    diastolic_bp_mmhg: int = 80,
) -> Crb65Features:
    return Crb65Features(
        age_years=age_years,
        confusion=confusion,
        respiratory_rate_per_minute=respiratory_rate_per_minute,
        systolic_bp_mmhg=systolic_bp_mmhg,
        diastolic_bp_mmhg=diastolic_bp_mmhg,
    )


class TestCriteriaContribution:
    def test_no_criteria_scores_zero(self) -> None:
        assert crb_65_score(_features()) == 0

    def test_confusion_alone_scores_one(self) -> None:
        assert crb_65_score(_features(confusion=True)) == 1

    def test_respiratory_rate_alone_scores_one(self) -> None:
        assert crb_65_score(_features(respiratory_rate_per_minute=32)) == 1

    def test_low_systolic_bp_alone_scores_one(self) -> None:
        assert crb_65_score(_features(systolic_bp_mmhg=85)) == 1

    def test_low_diastolic_bp_alone_scores_one(self) -> None:
        assert crb_65_score(_features(diastolic_bp_mmhg=55)) == 1

    def test_age_alone_scores_one(self) -> None:
        assert crb_65_score(_features(age_years=70)) == 1


class TestThresholdBoundaries:
    def test_respiratory_rate_29_does_not_score(self) -> None:
        assert crb_65_score(_features(respiratory_rate_per_minute=29)) == 0

    def test_respiratory_rate_30_scores(self) -> None:
        assert crb_65_score(_features(respiratory_rate_per_minute=30)) == 1

    def test_systolic_90_does_not_score(self) -> None:
        assert crb_65_score(_features(systolic_bp_mmhg=90)) == 0

    def test_systolic_89_scores(self) -> None:
        assert crb_65_score(_features(systolic_bp_mmhg=89)) == 1

    def test_diastolic_60_scores(self) -> None:
        assert crb_65_score(_features(diastolic_bp_mmhg=60)) == 1

    def test_diastolic_61_does_not_score(self) -> None:
        assert crb_65_score(_features(diastolic_bp_mmhg=61)) == 0

    def test_age_64_does_not_score(self) -> None:
        assert crb_65_score(_features(age_years=64)) == 0

    def test_age_65_scores(self) -> None:
        assert crb_65_score(_features(age_years=65)) == 1


class TestTotalScoreRange:
    def test_minimum_score_is_zero(self) -> None:
        assert crb_65_score(_features()) == 0

    def test_maximum_score_is_four(self) -> None:
        score = crb_65_score(
            _features(
                age_years=80,
                confusion=True,
                respiratory_rate_per_minute=36,
                systolic_bp_mmhg=80,
            )
        )
        assert score == 4


class TestSeverityBands:
    def test_score_zero_is_low(self) -> None:
        result = crb_65_assessment(_features())
        assert result.score == 0
        assert result.severity_band == "low"
        assert "Outpatient" in result.recommended_disposition

    def test_score_one_is_moderate(self) -> None:
        result = crb_65_assessment(_features(confusion=True))
        assert result.score == 1
        assert result.severity_band == "moderate"
        assert "hospital referral" in result.recommended_disposition.lower()

    def test_score_two_is_moderate(self) -> None:
        result = crb_65_assessment(
            _features(confusion=True, respiratory_rate_per_minute=32)
        )
        assert result.score == 2
        assert result.severity_band == "moderate"

    def test_score_three_is_high(self) -> None:
        result = crb_65_assessment(
            _features(
                confusion=True,
                respiratory_rate_per_minute=32,
                systolic_bp_mmhg=80,
            )
        )
        assert result.score == 3
        assert result.severity_band == "high"
        assert "Urgent hospital admission" in result.recommended_disposition

    def test_score_four_is_high(self) -> None:
        result = crb_65_assessment(
            _features(
                age_years=80,
                confusion=True,
                respiratory_rate_per_minute=32,
                systolic_bp_mmhg=80,
            )
        )
        assert result.score == 4
        assert result.severity_band == "high"


class TestDispositionAlwaysAcknowledgesUncapturedFactors:
    def test_low_severity_mentions_oxygenation(self) -> None:
        result = crb_65_assessment(_features())
        assert "oxygenation" in result.recommended_disposition.lower()

    def test_high_severity_mentions_oxygenation(self) -> None:
        result = crb_65_assessment(
            _features(
                confusion=True,
                respiratory_rate_per_minute=32,
                systolic_bp_mmhg=80,
            )
        )
        assert "oxygenation" in result.recommended_disposition.lower()


class TestInvalidInput:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError, match="age_years must be non-negative"):
            crb_65_score(_features(age_years=-1))

    def test_negative_respiratory_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="respiratory_rate_per_minute must be non-negative"):
            crb_65_score(_features(respiratory_rate_per_minute=-1))

    def test_negative_blood_pressure_raises(self) -> None:
        with pytest.raises(ValueError, match="blood pressure values must be non-negative"):
            crb_65_score(_features(systolic_bp_mmhg=-1))


class TestCriteriaLabels:
    def test_criteria_present_lists_only_met_components(self) -> None:
        criteria = crb_65_criteria(
            _features(confusion=True, age_years=70)
        )
        assert "confusion" in criteria
        assert "age >= 65 years" in criteria
        assert len(criteria) == 2


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = crb_65_assessment(_features())
        assert "Lim 2003" in result.citations
        assert "BTS 2009" in result.citations
