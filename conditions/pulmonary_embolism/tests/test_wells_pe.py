"""Tests for the Wells PE score and its interpretations."""

from __future__ import annotations

import pytest

from conditions.pulmonary_embolism.wells_pe import (
    WellsPeFeatures,
    wells_pe_score,
    wells_pe_three_tier,
    wells_pe_two_tier,
)

_DEFAULT: dict[str, bool] = {
    "clinical_signs_of_dvt": False,
    "pe_at_least_as_likely_as_alternative": False,
    "heart_rate_over_100": False,
    "immobilization_3_days_or_surgery_within_4_weeks": False,
    "previous_dvt_or_pe": False,
    "hemoptysis": False,
    "malignancy": False,
}


def _features(**overrides: bool) -> WellsPeFeatures:
    return WellsPeFeatures(**(_DEFAULT | overrides))


class TestItemPoints:
    def test_no_features_scores_zero(self) -> None:
        assert wells_pe_score(_features()) == 0.0

    def test_clinical_signs_of_dvt_adds_three(self) -> None:
        assert wells_pe_score(_features(clinical_signs_of_dvt=True)) == 3.0

    def test_pe_at_least_as_likely_adds_three(self) -> None:
        assert wells_pe_score(_features(pe_at_least_as_likely_as_alternative=True)) == 3.0

    def test_heart_rate_adds_1_5(self) -> None:
        assert wells_pe_score(_features(heart_rate_over_100=True)) == 1.5

    def test_immobilization_or_surgery_adds_1_5(self) -> None:
        assert (
            wells_pe_score(_features(immobilization_3_days_or_surgery_within_4_weeks=True))
            == 1.5
        )

    def test_previous_dvt_or_pe_adds_1_5(self) -> None:
        assert wells_pe_score(_features(previous_dvt_or_pe=True)) == 1.5

    def test_hemoptysis_adds_one(self) -> None:
        assert wells_pe_score(_features(hemoptysis=True)) == 1.0

    def test_malignancy_adds_one(self) -> None:
        assert wells_pe_score(_features(malignancy=True)) == 1.0

    def test_maximum_score_is_12_5(self) -> None:
        assert wells_pe_score(_features(**{k: True for k in _DEFAULT})) == 12.5


class TestTwoTier:
    def test_score_zero_is_unlikely(self) -> None:
        result = wells_pe_two_tier(_features())
        assert result.score == 0.0
        assert result.risk_band == "unlikely"

    def test_score_exactly_four_is_unlikely(self) -> None:
        # 3 + 1 = 4
        result = wells_pe_two_tier(
            _features(clinical_signs_of_dvt=True, hemoptysis=True)
        )
        assert result.score == 4.0
        assert result.risk_band == "unlikely"

    def test_score_above_four_is_likely(self) -> None:
        # 3 + 1.5 = 4.5
        result = wells_pe_two_tier(
            _features(
                clinical_signs_of_dvt=True,
                heart_rate_over_100=True,
            )
        )
        assert result.score == 4.5
        assert result.risk_band == "likely"

    def test_two_tier_unlikely_mentions_perc_and_d_dimer(self) -> None:
        result = wells_pe_two_tier(_features())
        action = result.recommended_action.lower()
        assert "perc" in action
        assert "d-dimer" in action

    def test_two_tier_likely_mentions_ct_pa(self) -> None:
        result = wells_pe_two_tier(
            _features(
                clinical_signs_of_dvt=True,
                pe_at_least_as_likely_as_alternative=True,
            )
        )
        assert result.score == 6.0
        assert result.risk_band == "likely"
        assert "CT pulmonary angiography" in result.recommended_action


class TestThreeTier:
    def test_score_zero_is_low(self) -> None:
        result = wells_pe_three_tier(_features())
        assert result.score == 0.0
        assert result.risk_band == "low"

    def test_score_1_5_is_low(self) -> None:
        result = wells_pe_three_tier(_features(heart_rate_over_100=True))
        assert result.score == 1.5
        assert result.risk_band == "low"

    def test_score_2_is_moderate(self) -> None:
        result = wells_pe_three_tier(
            _features(heart_rate_over_100=True, hemoptysis=True)
        )
        assert result.score == 2.5
        assert result.risk_band == "moderate"

    def test_score_exactly_2_is_moderate(self) -> None:
        result = wells_pe_three_tier(
            _features(hemoptysis=True, malignancy=True)
        )
        assert result.score == 2.0
        assert result.risk_band == "moderate"

    def test_score_six_is_moderate(self) -> None:
        # 3 + 3 = 6
        result = wells_pe_three_tier(
            _features(
                clinical_signs_of_dvt=True,
                pe_at_least_as_likely_as_alternative=True,
            )
        )
        assert result.score == 6.0
        assert result.risk_band == "moderate"

    def test_score_above_six_is_high(self) -> None:
        # 3 + 3 + 1.5 = 7.5
        result = wells_pe_three_tier(
            _features(
                clinical_signs_of_dvt=True,
                pe_at_least_as_likely_as_alternative=True,
                heart_rate_over_100=True,
            )
        )
        assert result.score == 7.5
        assert result.risk_band == "high"

    def test_three_tier_low_mentions_perc(self) -> None:
        result = wells_pe_three_tier(_features())
        assert "perc" in result.recommended_action.lower()

    def test_three_tier_moderate_does_not_recommend_perc(self) -> None:
        result = wells_pe_three_tier(_features(hemoptysis=True, malignancy=True))
        assert "Do not apply PERC" in result.recommended_action

    def test_three_tier_high_mentions_ct_pa(self) -> None:
        result = wells_pe_three_tier(
            _features(
                clinical_signs_of_dvt=True,
                pe_at_least_as_likely_as_alternative=True,
                heart_rate_over_100=True,
            )
        )
        assert "CT pulmonary angiography" in result.recommended_action

    def test_three_tier_includes_prevalence_estimate(self) -> None:
        result = wells_pe_three_tier(_features())
        assert "Wells 2001" in result.estimated_pe_prevalence_band


class TestOutputShape:
    def test_two_tier_citations_present(self) -> None:
        result = wells_pe_two_tier(_features())
        assert "Wells 2001" in result.citations

    def test_three_tier_citations_present(self) -> None:
        result = wells_pe_three_tier(_features())
        assert "Wells 2000" in result.citations

    def test_two_tier_rationale_non_empty(self) -> None:
        result = wells_pe_two_tier(_features())
        assert result.rationale.strip() != ""
