"""Tests for the HEART score and its risk-banded interpretation."""

from __future__ import annotations

import pytest

from conditions.chest_pain.heart_score import (
    HeartFeatures,
    heart_assessment,
    heart_component_scores,
    heart_score,
)

# A baseline of all-zero-point inputs. Each test overrides only what it needs.
_DEFAULT: dict[str, object] = {
    "history": "slightly_suspicious",
    "ecg": "normal",
    "age_years": 30,
    "hypertension": False,
    "hypercholesterolemia": False,
    "diabetes_mellitus": False,
    "current_or_recent_smoking": False,
    "family_history_of_cad": False,
    "obesity_bmi_over_30": False,
    "history_of_atherosclerotic_disease": False,
    "troponin": "at_or_below_normal_limit",
}


def _features(**overrides: object) -> HeartFeatures:
    return HeartFeatures(**(_DEFAULT | overrides))  # type: ignore[arg-type]


class TestHistoryComponent:
    def test_slightly_suspicious_is_zero(self) -> None:
        assert heart_component_scores(_features()).history == 0

    def test_moderately_suspicious_is_one(self) -> None:
        assert heart_component_scores(_features(history="moderately_suspicious")).history == 1

    def test_highly_suspicious_is_two(self) -> None:
        assert heart_component_scores(_features(history="highly_suspicious")).history == 2


class TestEcgComponent:
    def test_normal_is_zero(self) -> None:
        assert heart_component_scores(_features()).ecg == 0

    def test_nonspecific_is_one(self) -> None:
        result = heart_component_scores(
            _features(ecg="nonspecific_repolarization_disturbance")
        )
        assert result.ecg == 1

    def test_significant_st_deviation_is_two(self) -> None:
        result = heart_component_scores(_features(ecg="significant_st_deviation"))
        assert result.ecg == 2


class TestAgeComponent:
    def test_under_45_is_zero(self) -> None:
        assert heart_component_scores(_features(age_years=44)).age == 0

    def test_exactly_45_is_one(self) -> None:
        assert heart_component_scores(_features(age_years=45)).age == 1

    def test_64_is_one(self) -> None:
        assert heart_component_scores(_features(age_years=64)).age == 1

    def test_exactly_65_is_two(self) -> None:
        assert heart_component_scores(_features(age_years=65)).age == 2

    def test_zero_age_is_zero_points(self) -> None:
        assert heart_component_scores(_features(age_years=0)).age == 0


class TestRiskFactorComponent:
    def test_none_is_zero(self) -> None:
        assert heart_component_scores(_features()).risk_factors == 0

    def test_one_risk_factor_is_one(self) -> None:
        assert heart_component_scores(_features(hypertension=True)).risk_factors == 1

    def test_two_risk_factors_is_one(self) -> None:
        result = heart_component_scores(
            _features(hypertension=True, diabetes_mellitus=True)
        )
        assert result.risk_factors == 1

    def test_three_risk_factors_is_two(self) -> None:
        result = heart_component_scores(
            _features(
                hypertension=True,
                diabetes_mellitus=True,
                obesity_bmi_over_30=True,
            )
        )
        assert result.risk_factors == 2

    def test_all_six_risk_factors_is_two(self) -> None:
        result = heart_component_scores(
            _features(
                hypertension=True,
                hypercholesterolemia=True,
                diabetes_mellitus=True,
                current_or_recent_smoking=True,
                family_history_of_cad=True,
                obesity_bmi_over_30=True,
            )
        )
        assert result.risk_factors == 2

    def test_atherosclerotic_disease_overrides_to_two_with_no_other_factors(self) -> None:
        result = heart_component_scores(
            _features(history_of_atherosclerotic_disease=True)
        )
        assert result.risk_factors == 2

    def test_atherosclerotic_disease_with_one_factor_still_two(self) -> None:
        # Without the override this would be 1 (a single risk factor).
        result = heart_component_scores(
            _features(history_of_atherosclerotic_disease=True, hypertension=True)
        )
        assert result.risk_factors == 2


class TestTroponinComponent:
    def test_at_or_below_normal_is_zero(self) -> None:
        assert heart_component_scores(_features()).troponin == 0

    def test_one_to_three_times_is_one(self) -> None:
        result = heart_component_scores(
            _features(troponin="one_to_three_times_normal_limit")
        )
        assert result.troponin == 1

    def test_above_three_times_is_two(self) -> None:
        result = heart_component_scores(
            _features(troponin="above_three_times_normal_limit")
        )
        assert result.troponin == 2


class TestTotalScore:
    def test_all_zero_is_zero(self) -> None:
        assert heart_score(_features()) == 0

    def test_maximum_score_is_ten(self) -> None:
        result = heart_score(
            _features(
                history="highly_suspicious",
                ecg="significant_st_deviation",
                age_years=80,
                history_of_atherosclerotic_disease=True,
                troponin="above_three_times_normal_limit",
            )
        )
        assert result == 10

    def test_components_sum_to_total(self) -> None:
        features = _features(
            history="moderately_suspicious",
            ecg="nonspecific_repolarization_disturbance",
            age_years=70,
            hypertension=True,
            diabetes_mellitus=True,
            troponin="one_to_three_times_normal_limit",
        )
        components = heart_component_scores(features)
        total = (
            components.history
            + components.ecg
            + components.age
            + components.risk_factors
            + components.troponin
        )
        assert total == heart_score(features)
        # 1 + 1 + 2 + 1 + 1 = 6
        assert total == 6


class TestBands:
    def test_score_zero_is_low(self) -> None:
        result = heart_assessment(_features())
        assert result.score == 0
        assert result.risk_band == "low"

    def test_score_exactly_three_is_low(self) -> None:
        # history 2 + age 1 = 3
        result = heart_assessment(
            _features(history="highly_suspicious", age_years=50)
        )
        assert result.score == 3
        assert result.risk_band == "low"

    def test_score_exactly_four_is_moderate(self) -> None:
        # history 2 + age 1 + one risk factor 1 = 4
        result = heart_assessment(
            _features(history="highly_suspicious", age_years=50, hypertension=True)
        )
        assert result.score == 4
        assert result.risk_band == "moderate"

    def test_score_exactly_six_is_moderate(self) -> None:
        # history 2 + ecg 2 + age 2 = 6
        result = heart_assessment(
            _features(
                history="highly_suspicious",
                ecg="significant_st_deviation",
                age_years=65,
            )
        )
        assert result.score == 6
        assert result.risk_band == "moderate"

    def test_score_exactly_seven_is_high(self) -> None:
        # history 2 + ecg 2 + age 2 + one risk factor 1 = 7
        result = heart_assessment(
            _features(
                history="highly_suspicious",
                ecg="significant_st_deviation",
                age_years=65,
                hypertension=True,
            )
        )
        assert result.score == 7
        assert result.risk_band == "high"

    def test_score_ten_is_high(self) -> None:
        result = heart_assessment(
            _features(
                history="highly_suspicious",
                ecg="significant_st_deviation",
                age_years=80,
                history_of_atherosclerotic_disease=True,
                troponin="above_three_times_normal_limit",
            )
        )
        assert result.score == 10
        assert result.risk_band == "high"


class TestDispositionAndCaveats:
    def test_low_mentions_early_discharge(self) -> None:
        result = heart_assessment(_features())
        assert "early discharge" in result.recommended_disposition.lower()

    def test_moderate_mentions_serial_troponin(self) -> None:
        result = heart_assessment(
            _features(history="highly_suspicious", age_years=50, hypertension=True)
        )
        assert "serial troponin" in result.recommended_disposition.lower()

    def test_high_mentions_admit(self) -> None:
        result = heart_assessment(
            _features(
                history="highly_suspicious",
                ecg="significant_st_deviation",
                age_years=65,
                hypertension=True,
            )
        )
        assert "admit" in result.recommended_disposition.lower()

    def test_low_mace_band_references_backus(self) -> None:
        result = heart_assessment(_features())
        assert "1.7%" in result.estimated_6_week_mace_band
        assert "Backus 2013" in result.estimated_6_week_mace_band

    def test_population_caveats_present(self) -> None:
        result = heart_assessment(_features())
        assert len(result.population_caveats) >= 1
        assert any("STEMI".lower() in c.lower() or "ST-elevation" in c for c in result.population_caveats)

    def test_caveat_mentions_serial_troponin_pathway(self) -> None:
        result = heart_assessment(_features())
        assert any("serial troponin" in c.lower() for c in result.population_caveats)


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = heart_assessment(_features())
        assert "Six 2008" in result.citations
        assert "Backus 2013" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = heart_assessment(_features()).rationale
        assert result.strip() != ""

    def test_components_echoed_in_result(self) -> None:
        result = heart_assessment(
            _features(history="moderately_suspicious", troponin="one_to_three_times_normal_limit")
        )
        assert result.components.history == 1
        assert result.components.troponin == 1


class TestValidation:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError):
            heart_score(_features(age_years=-1))

    def test_negative_age_raises_in_assessment(self) -> None:
        with pytest.raises(ValueError):
            heart_assessment(_features(age_years=-5))
