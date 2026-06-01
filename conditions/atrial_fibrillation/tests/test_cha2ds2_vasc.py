"""Tests for the CHA2DS2-VASc score.

Coverage targets:
- Each component contributes the correct number of points.
- Age bands are mutually exclusive (65 to 74 vs >= 75).
- Score range 0 to 9.
- Sex-stratified ESC 2020 recommendation thresholds (male 0/1/>=2,
  female 0-1/2/>=3).
- Invalid input raises.
"""

from __future__ import annotations

import pytest

from conditions.atrial_fibrillation.cha2ds2_vasc import (
    Cha2ds2VascFeatures,
    cha2ds2_vasc_assessment,
    cha2ds2_vasc_criteria,
    cha2ds2_vasc_score,
)


def _features(
    *,
    age_years: int = 50,
    sex: str = "male",
    congestive_heart_failure: bool = False,
    hypertension: bool = False,
    diabetes: bool = False,
    prior_stroke_tia_or_thromboembolism: bool = False,
    vascular_disease: bool = False,
) -> Cha2ds2VascFeatures:
    return Cha2ds2VascFeatures(
        age_years=age_years,
        sex=sex,  # type: ignore[arg-type]
        congestive_heart_failure=congestive_heart_failure,
        hypertension=hypertension,
        diabetes=diabetes,
        prior_stroke_tia_or_thromboembolism=prior_stroke_tia_or_thromboembolism,
        vascular_disease=vascular_disease,
    )


class TestComponentContribution:
    def test_no_factors_male_scores_zero(self) -> None:
        assert cha2ds2_vasc_score(_features()) == 0

    def test_no_factors_female_scores_one_for_sex(self) -> None:
        assert cha2ds2_vasc_score(_features(sex="female")) == 1

    def test_chf_adds_one(self) -> None:
        assert cha2ds2_vasc_score(_features(congestive_heart_failure=True)) == 1

    def test_hypertension_adds_one(self) -> None:
        assert cha2ds2_vasc_score(_features(hypertension=True)) == 1

    def test_diabetes_adds_one(self) -> None:
        assert cha2ds2_vasc_score(_features(diabetes=True)) == 1

    def test_vascular_disease_adds_one(self) -> None:
        assert cha2ds2_vasc_score(_features(vascular_disease=True)) == 1

    def test_prior_stroke_adds_two(self) -> None:
        assert cha2ds2_vasc_score(
            _features(prior_stroke_tia_or_thromboembolism=True)
        ) == 2

    def test_age_75_adds_two(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=75)) == 2

    def test_age_70_adds_one(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=70)) == 1


class TestAgeBands:
    def test_age_64_scores_zero(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=64)) == 0

    def test_age_65_scores_one(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=65)) == 1

    def test_age_74_scores_one(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=74)) == 1

    def test_age_75_scores_two(self) -> None:
        assert cha2ds2_vasc_score(_features(age_years=75)) == 2

    def test_age_bands_are_mutually_exclusive(self) -> None:
        criteria = cha2ds2_vasc_criteria(_features(age_years=80))
        age_components = [label for label, _ in criteria if "age" in label]
        assert age_components == ["age >= 75"]


class TestScoreRange:
    def test_maximum_score_is_nine(self) -> None:
        score = cha2ds2_vasc_score(
            _features(
                age_years=80,
                sex="female",
                congestive_heart_failure=True,
                hypertension=True,
                diabetes=True,
                prior_stroke_tia_or_thromboembolism=True,
                vascular_disease=True,
            )
        )
        assert score == 9


class TestMaleAnticoagulationThresholds:
    def test_male_score_zero_not_recommended(self) -> None:
        result = cha2ds2_vasc_assessment(_features(sex="male"))
        assert result.score == 0
        assert "not recommended" in result.recommended_anticoagulation.lower()

    def test_male_score_one_consider(self) -> None:
        result = cha2ds2_vasc_assessment(
            _features(sex="male", hypertension=True)
        )
        assert result.score == 1
        assert "Consider anticoagulation" in result.recommended_anticoagulation
        assert "IIa" in result.recommended_anticoagulation

    def test_male_score_two_recommended(self) -> None:
        result = cha2ds2_vasc_assessment(
            _features(sex="male", hypertension=True, diabetes=True)
        )
        assert result.score == 2
        assert "Anticoagulation recommended" in result.recommended_anticoagulation
        assert "Class I" in result.recommended_anticoagulation


class TestFemaleAnticoagulationThresholds:
    def test_female_score_one_sex_only_not_recommended(self) -> None:
        result = cha2ds2_vasc_assessment(_features(sex="female"))
        assert result.score == 1
        assert "not recommended" in result.recommended_anticoagulation.lower()

    def test_female_score_two_with_sex_plus_one_consider(self) -> None:
        result = cha2ds2_vasc_assessment(
            _features(sex="female", hypertension=True)
        )
        assert result.score == 2
        assert "Consider anticoagulation" in result.recommended_anticoagulation
        assert "IIa" in result.recommended_anticoagulation

    def test_female_score_three_recommended(self) -> None:
        result = cha2ds2_vasc_assessment(
            _features(sex="female", hypertension=True, diabetes=True)
        )
        assert result.score == 3
        assert "Anticoagulation recommended" in result.recommended_anticoagulation
        assert "Class I" in result.recommended_anticoagulation


class TestInvalidInput:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError, match="age_years must be non-negative"):
            cha2ds2_vasc_score(_features(age_years=-1))

    def test_invalid_sex_raises(self) -> None:
        with pytest.raises(ValueError, match="sex must be"):
            cha2ds2_vasc_score(_features(sex="unspecified"))


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = cha2ds2_vasc_assessment(_features())
        assert "Lip 2010" in result.citations
        assert "ESC 2020" in result.citations

    def test_stroke_risk_band_present(self) -> None:
        result = cha2ds2_vasc_assessment(_features())
        assert result.annual_stroke_risk_band.strip() != ""

    def test_criteria_present_format_is_label_points_tuples(self) -> None:
        criteria = cha2ds2_vasc_criteria(
            _features(hypertension=True, prior_stroke_tia_or_thromboembolism=True)
        )
        assert ("hypertension", 1) in criteria
        assert ("prior stroke / TIA / thromboembolism", 2) in criteria
