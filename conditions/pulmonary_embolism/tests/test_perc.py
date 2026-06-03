"""Tests for PERC (Pulmonary Embolism Rule-out Criteria)."""

from __future__ import annotations

import pytest

from conditions.pulmonary_embolism.perc import (
    PercFeatures,
    perc_assessment,
    perc_failure_criteria,
)

_DEFAULT: dict[str, bool] = {
    "age_50_or_older": False,
    "heart_rate_100_or_more": False,
    "spo2_below_95_on_room_air": False,
    "hemoptysis": False,
    "estrogen_use": False,
    "prior_dvt_or_pe": False,
    "unilateral_leg_swelling": False,
    "recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization": False,
}

_FIELDS: tuple[str, ...] = tuple(_DEFAULT.keys())


def _features(**overrides: bool) -> PercFeatures:
    return PercFeatures(**(_DEFAULT | overrides))


class TestApplicabilityGate:
    def test_pretest_not_low_refuses_to_rule_out(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=False)
        assert result.pe_ruled_out is False
        assert result.pretest_probability_is_low is False
        assert "validated only at low pretest probability" in result.recommended_action

    def test_pretest_not_low_with_all_criteria_absent_still_refuses(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=False)
        assert result.pe_ruled_out is False

    def test_pretest_not_low_recommends_wells_d_dimer_pathway(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=False)
        assert "Wells" in result.recommended_action
        assert "D-dimer" in result.recommended_action


class TestAllNegative:
    def test_all_negative_low_pretest_rules_out_pe(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert result.pe_ruled_out is True
        assert result.perc_failure_criteria_present == ()

    def test_all_negative_recommendation_mentions_no_further_testing(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert "excluded" in result.recommended_action.lower()
        assert "no further testing" in result.recommended_action.lower()


class TestFailureCriteria:
    @pytest.mark.parametrize("field", _FIELDS)
    def test_each_positive_field_causes_perc_failure(self, field: str) -> None:
        result = perc_assessment(
            _features(**{field: True}),
            pretest_probability_is_low=True,
        )
        assert result.pe_ruled_out is False
        assert len(result.perc_failure_criteria_present) == 1

    def test_perc_failure_recommends_d_dimer(self) -> None:
        result = perc_assessment(
            _features(hemoptysis=True),
            pretest_probability_is_low=True,
        )
        assert "D-dimer" in result.recommended_action
        assert "CT pulmonary angiography" in result.recommended_action

    def test_multiple_positive_fields_all_listed(self) -> None:
        result = perc_assessment(
            _features(hemoptysis=True, prior_dvt_or_pe=True),
            pretest_probability_is_low=True,
        )
        assert len(result.perc_failure_criteria_present) == 2

    def test_all_positive_fields_yields_eight_failures(self) -> None:
        result = perc_assessment(
            _features(**{k: True for k in _FIELDS}),
            pretest_probability_is_low=True,
        )
        assert len(result.perc_failure_criteria_present) == 8
        assert result.pe_ruled_out is False


class TestCriteriaLabels:
    def test_hemoptysis_label_listed(self) -> None:
        criteria = perc_failure_criteria(_features(hemoptysis=True))
        assert "hemoptysis" in criteria

    def test_unilateral_leg_swelling_label_listed(self) -> None:
        criteria = perc_failure_criteria(_features(unilateral_leg_swelling=True))
        assert "unilateral leg swelling" in criteria


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert "Kline 2004" in result.citations
        assert "Kline 2008" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert result.rationale.strip() != ""

    def test_pretest_flag_echoed_back(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert result.pretest_probability_is_low is True


class TestClinicalVignettes:
    def test_young_well_appearing_patient_with_low_pretest_ruled_out(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=True)
        assert result.pe_ruled_out is True

    def test_patient_on_estrogen_perc_fails_even_with_low_pretest(self) -> None:
        result = perc_assessment(
            _features(estrogen_use=True),
            pretest_probability_is_low=True,
        )
        assert result.pe_ruled_out is False

    def test_perfectly_perc_negative_but_moderate_pretest_not_ruled_out(self) -> None:
        result = perc_assessment(_features(), pretest_probability_is_low=False)
        assert result.pe_ruled_out is False
