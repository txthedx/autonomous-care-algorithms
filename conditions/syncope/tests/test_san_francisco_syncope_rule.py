"""Tests for the San Francisco Syncope Rule (CHESS)."""

from __future__ import annotations

import pytest

from conditions.syncope.san_francisco_syncope_rule import (
    SfsrFeatures,
    sfsr_assessment,
    sfsr_positive_criteria,
)

# Baseline with no criteria present (low risk). Each test overrides what it needs.
_DEFAULT: dict[str, object] = {
    "congestive_heart_failure_history": False,
    "hematocrit_percent": 42.0,          # >= 30 -> negative
    "abnormal_ecg": False,
    "shortness_of_breath": False,
    "systolic_bp_mmhg": 120,             # >= 90 -> negative
}


def _features(**overrides: object) -> SfsrFeatures:
    return SfsrFeatures(**(_DEFAULT | overrides))  # type: ignore[arg-type]


class TestIndividualCriteria:
    def test_no_criteria_is_low_risk(self) -> None:
        result = sfsr_assessment(_features())
        assert result.high_risk is False
        assert result.risk_band == "low"
        assert result.positive_criteria == ()

    def test_congestive_heart_failure_is_high_risk(self) -> None:
        result = sfsr_assessment(_features(congestive_heart_failure_history=True))
        assert result.high_risk is True
        assert any("congestive heart failure" in c for c in result.positive_criteria)

    def test_low_hematocrit_is_high_risk(self) -> None:
        result = sfsr_assessment(_features(hematocrit_percent=25.0))
        assert result.high_risk is True
        assert any("hematocrit" in c for c in result.positive_criteria)

    def test_abnormal_ecg_is_high_risk(self) -> None:
        result = sfsr_assessment(_features(abnormal_ecg=True))
        assert result.high_risk is True
        assert any("ECG" in c for c in result.positive_criteria)

    def test_shortness_of_breath_is_high_risk(self) -> None:
        result = sfsr_assessment(_features(shortness_of_breath=True))
        assert result.high_risk is True
        assert any("shortness of breath" in c for c in result.positive_criteria)

    def test_low_systolic_bp_is_high_risk(self) -> None:
        result = sfsr_assessment(_features(systolic_bp_mmhg=85))
        assert result.high_risk is True
        assert any("systolic BP" in c for c in result.positive_criteria)


class TestHematocritThreshold:
    def test_exactly_30_is_negative(self) -> None:
        # Threshold is "< 30", so 30.0 does not count.
        assert sfsr_positive_criteria(_features(hematocrit_percent=30.0)) == ()

    def test_just_below_30_is_positive(self) -> None:
        criteria = sfsr_positive_criteria(_features(hematocrit_percent=29.9))
        assert len(criteria) == 1
        assert "hematocrit" in criteria[0]


class TestSystolicBpThreshold:
    def test_exactly_90_is_negative(self) -> None:
        # Threshold is "< 90", so 90 does not count.
        assert sfsr_positive_criteria(_features(systolic_bp_mmhg=90)) == ()

    def test_just_below_90_is_positive(self) -> None:
        criteria = sfsr_positive_criteria(_features(systolic_bp_mmhg=89))
        assert len(criteria) == 1
        assert "systolic BP" in criteria[0]


class TestMultipleCriteria:
    def test_all_five_criteria_present(self) -> None:
        result = sfsr_assessment(
            _features(
                congestive_heart_failure_history=True,
                hematocrit_percent=20.0,
                abnormal_ecg=True,
                shortness_of_breath=True,
                systolic_bp_mmhg=80,
            )
        )
        assert result.high_risk is True
        assert len(result.positive_criteria) == 5

    def test_two_criteria_present(self) -> None:
        result = sfsr_assessment(
            _features(abnormal_ecg=True, shortness_of_breath=True)
        )
        assert len(result.positive_criteria) == 2


class TestDispositionAndCaveats:
    def test_high_risk_mentions_admission_or_observation(self) -> None:
        result = sfsr_assessment(_features(abnormal_ecg=True))
        action = result.recommended_disposition.lower()
        assert "admission" in action or "observation" in action

    def test_low_risk_mentions_outpatient(self) -> None:
        result = sfsr_assessment(_features())
        assert "outpatient" in result.recommended_disposition.lower()

    def test_low_risk_notes_not_a_discharge_guarantee(self) -> None:
        result = sfsr_assessment(_features())
        assert "discharge guarantee" in result.recommended_disposition.lower()

    def test_caveats_mention_external_validation(self) -> None:
        result = sfsr_assessment(_features())
        assert any("Sun 2007" in c or "Birnbaum 2008" in c
                   for c in result.population_caveats)

    def test_caveats_mention_non_cardiac_exclusion(self) -> None:
        result = sfsr_assessment(_features())
        assert any("seizure" in c.lower() or "intoxication" in c.lower()
                   for c in result.population_caveats)


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = sfsr_assessment(_features())
        assert "Quinn 2004" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = sfsr_assessment(_features())
        assert result.rationale.strip() != ""


class TestValidation:
    def test_hematocrit_over_100_raises(self) -> None:
        with pytest.raises(ValueError):
            sfsr_assessment(_features(hematocrit_percent=101.0))

    def test_negative_hematocrit_raises(self) -> None:
        with pytest.raises(ValueError):
            sfsr_positive_criteria(_features(hematocrit_percent=-1.0))

    def test_negative_systolic_bp_raises(self) -> None:
        with pytest.raises(ValueError):
            sfsr_assessment(_features(systolic_bp_mmhg=-1))
