"""Tests for the Wells DVT score (1997 original and 2003 modified).

Coverage targets:
- Each item contributes the documented number of points.
- Alternative-diagnosis item contributes -2.
- Modified (2003) score includes previously_documented_dvt; original
  (1997) score excludes it.
- Two-tier boundary at 1 vs 2.
- Three-tier boundaries at 0 vs 1 and 2 vs 3.
- Score range and outputs at the extremes.
- Output shape: risk band, recommendation, citations, rationale.
"""

from __future__ import annotations

import pytest

from conditions.deep_vein_thrombosis.wells_dvt import (
    WellsDvtFeatures,
    wells_dvt_score_modified,
    wells_dvt_score_original,
    wells_dvt_three_tier,
    wells_dvt_two_tier,
)

_DEFAULT: dict[str, bool] = {
    "active_cancer": False,
    "paralysis_paresis_or_recent_lower_limb_immobilization": False,
    "recently_bedridden_3_days_or_major_surgery_within_12_weeks": False,
    "localized_tenderness_along_deep_venous_system": False,
    "entire_leg_swollen": False,
    "calf_swelling_more_than_3cm": False,
    "pitting_edema_in_symptomatic_leg": False,
    "collateral_superficial_veins_non_varicose": False,
    "previously_documented_dvt": False,
    "alternative_diagnosis_at_least_as_likely": False,
}

_POSITIVE_ITEMS_BOTH_VERSIONS: tuple[str, ...] = (
    "active_cancer",
    "paralysis_paresis_or_recent_lower_limb_immobilization",
    "recently_bedridden_3_days_or_major_surgery_within_12_weeks",
    "localized_tenderness_along_deep_venous_system",
    "entire_leg_swollen",
    "calf_swelling_more_than_3cm",
    "pitting_edema_in_symptomatic_leg",
    "collateral_superficial_veins_non_varicose",
)


def _features(**overrides: bool) -> WellsDvtFeatures:
    return WellsDvtFeatures(**(_DEFAULT | overrides))


class TestModifiedScore:
    def test_no_features_scores_zero(self) -> None:
        assert wells_dvt_score_modified(_features()) == 0

    @pytest.mark.parametrize("field", _POSITIVE_ITEMS_BOTH_VERSIONS)
    def test_each_shared_positive_item_adds_one(self, field: str) -> None:
        assert wells_dvt_score_modified(_features(**{field: True})) == 1

    def test_previously_documented_dvt_adds_one_in_modified(self) -> None:
        assert wells_dvt_score_modified(_features(previously_documented_dvt=True)) == 1

    def test_alternative_diagnosis_subtracts_two(self) -> None:
        assert (
            wells_dvt_score_modified(
                _features(alternative_diagnosis_at_least_as_likely=True)
            )
            == -2
        )

    def test_alternative_diagnosis_offsets_positive_items(self) -> None:
        assert (
            wells_dvt_score_modified(
                _features(
                    active_cancer=True,
                    alternative_diagnosis_at_least_as_likely=True,
                )
            )
            == -1
        )

    def test_maximum_modified_score_is_nine(self) -> None:
        assert wells_dvt_score_modified(
            _features(**{k: True for k in _DEFAULT if k != "alternative_diagnosis_at_least_as_likely"})
        ) == 9

    def test_minimum_modified_score_is_negative_two(self) -> None:
        assert (
            wells_dvt_score_modified(
                _features(alternative_diagnosis_at_least_as_likely=True)
            )
            == -2
        )


class TestOriginalScore:
    def test_no_features_scores_zero(self) -> None:
        assert wells_dvt_score_original(_features()) == 0

    def test_previously_documented_dvt_does_not_count(self) -> None:
        assert wells_dvt_score_original(_features(previously_documented_dvt=True)) == 0

    def test_maximum_original_score_is_eight(self) -> None:
        assert wells_dvt_score_original(
            _features(**{k: True for k in _DEFAULT if k != "alternative_diagnosis_at_least_as_likely"})
        ) == 8

    def test_minimum_original_score_is_negative_two(self) -> None:
        assert (
            wells_dvt_score_original(
                _features(alternative_diagnosis_at_least_as_likely=True)
            )
            == -2
        )

    def test_alternative_diagnosis_offsets_positive_items(self) -> None:
        assert (
            wells_dvt_score_original(
                _features(
                    active_cancer=True,
                    entire_leg_swollen=True,
                    alternative_diagnosis_at_least_as_likely=True,
                )
            )
            == 0
        )


class TestTwoTierBands:
    def test_score_zero_is_unlikely(self) -> None:
        result = wells_dvt_two_tier(_features())
        assert result.score == 0
        assert result.risk_band == "unlikely"

    def test_score_one_is_unlikely(self) -> None:
        result = wells_dvt_two_tier(_features(active_cancer=True))
        assert result.score == 1
        assert result.risk_band == "unlikely"

    def test_score_two_is_likely(self) -> None:
        result = wells_dvt_two_tier(
            _features(active_cancer=True, entire_leg_swollen=True)
        )
        assert result.score == 2
        assert result.risk_band == "likely"

    def test_negative_score_is_unlikely(self) -> None:
        result = wells_dvt_two_tier(
            _features(alternative_diagnosis_at_least_as_likely=True)
        )
        assert result.score == -2
        assert result.risk_band == "unlikely"

    def test_previously_documented_dvt_can_shift_band(self) -> None:
        result_without = wells_dvt_two_tier(_features(active_cancer=True))
        result_with = wells_dvt_two_tier(
            _features(active_cancer=True, previously_documented_dvt=True)
        )
        assert result_without.risk_band == "unlikely"
        assert result_with.risk_band == "likely"


class TestThreeTierBands:
    def test_score_zero_is_low(self) -> None:
        result = wells_dvt_three_tier(_features())
        assert result.score == 0
        assert result.risk_band == "low"

    def test_negative_score_is_low(self) -> None:
        result = wells_dvt_three_tier(
            _features(alternative_diagnosis_at_least_as_likely=True)
        )
        assert result.score == -2
        assert result.risk_band == "low"

    def test_score_one_is_moderate(self) -> None:
        result = wells_dvt_three_tier(_features(active_cancer=True))
        assert result.score == 1
        assert result.risk_band == "moderate"

    def test_score_two_is_moderate(self) -> None:
        result = wells_dvt_three_tier(
            _features(active_cancer=True, entire_leg_swollen=True)
        )
        assert result.score == 2
        assert result.risk_band == "moderate"

    def test_score_three_is_high(self) -> None:
        result = wells_dvt_three_tier(
            _features(
                active_cancer=True,
                entire_leg_swollen=True,
                pitting_edema_in_symptomatic_leg=True,
            )
        )
        assert result.score == 3
        assert result.risk_band == "high"

    def test_previously_documented_dvt_does_not_affect_three_tier(self) -> None:
        result_without = wells_dvt_three_tier(_features(active_cancer=True))
        result_with = wells_dvt_three_tier(
            _features(active_cancer=True, previously_documented_dvt=True)
        )
        assert result_without.score == result_with.score
        assert result_without.risk_band == result_with.risk_band


class TestRecommendations:
    def test_two_tier_unlikely_recommends_d_dimer(self) -> None:
        result = wells_dvt_two_tier(_features())
        assert "D-dimer" in result.recommended_action

    def test_two_tier_likely_recommends_ultrasound(self) -> None:
        result = wells_dvt_two_tier(
            _features(active_cancer=True, entire_leg_swollen=True)
        )
        assert "ultrasound" in result.recommended_action.lower()
        assert "D-dimer is not required" in result.recommended_action

    def test_three_tier_low_recommends_d_dimer(self) -> None:
        result = wells_dvt_three_tier(_features())
        assert "D-dimer" in result.recommended_action

    def test_three_tier_moderate_recommends_ultrasound(self) -> None:
        result = wells_dvt_three_tier(_features(active_cancer=True))
        assert "ultrasound" in result.recommended_action.lower()

    def test_three_tier_high_recommends_ultrasound_and_repeat(self) -> None:
        result = wells_dvt_three_tier(
            _features(
                active_cancer=True,
                entire_leg_swollen=True,
                pitting_edema_in_symptomatic_leg=True,
            )
        )
        assert "ultrasound" in result.recommended_action.lower()
        assert "repeat imaging" in result.recommended_action.lower()


class TestOutputShape:
    def test_two_tier_citations_present(self) -> None:
        result = wells_dvt_two_tier(_features())
        assert "Wells 2003" in result.citations

    def test_three_tier_citations_present(self) -> None:
        result = wells_dvt_three_tier(_features())
        assert "Wells 1997" in result.citations

    def test_two_tier_rationale_non_empty(self) -> None:
        result = wells_dvt_two_tier(_features())
        assert result.rationale.strip() != ""

    def test_three_tier_includes_prevalence_estimate(self) -> None:
        result = wells_dvt_three_tier(_features())
        assert result.estimated_dvt_prevalence_band.strip() != ""
        assert "Wells 1997" in result.estimated_dvt_prevalence_band


class TestClinicalVignettes:
    """Abstract vignettes exercising the rule at decision boundaries."""

    def test_isolated_alternative_diagnosis_is_unlikely_low(self) -> None:
        features = _features(alternative_diagnosis_at_least_as_likely=True)
        assert wells_dvt_two_tier(features).risk_band == "unlikely"
        assert wells_dvt_three_tier(features).risk_band == "low"

    def test_cancer_with_calf_swelling_is_likely_moderate(self) -> None:
        features = _features(active_cancer=True, calf_swelling_more_than_3cm=True)
        assert wells_dvt_two_tier(features).risk_band == "likely"
        assert wells_dvt_three_tier(features).risk_band == "moderate"

    def test_recent_surgery_with_multiple_leg_findings_high_three_tier(self) -> None:
        features = _features(
            recently_bedridden_3_days_or_major_surgery_within_12_weeks=True,
            entire_leg_swollen=True,
            pitting_edema_in_symptomatic_leg=True,
        )
        assert wells_dvt_three_tier(features).risk_band == "high"
        assert wells_dvt_two_tier(features).risk_band == "likely"
