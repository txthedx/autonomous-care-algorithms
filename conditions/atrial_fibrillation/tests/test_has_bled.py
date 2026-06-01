"""Tests for the HAS-BLED score.

Coverage targets:
- Each of the nine components contributes one point independently.
- Age threshold is strictly > 65 (66 scores, 65 does not).
- Score range 0 to 9.
- Risk band boundary at total 2 vs 3.
- Modifiable factors are correctly enumerated.
- ESC 2020 do-not-withhold language appears in high-risk recommendations.
- Invalid input raises.
"""

from __future__ import annotations

import pytest

from conditions.atrial_fibrillation.has_bled import (
    HasBledFeatures,
    has_bled_assessment,
    has_bled_criteria,
    has_bled_score,
)


def _features(
    *,
    age_years: int = 50,
    uncontrolled_hypertension: bool = False,
    abnormal_renal_function: bool = False,
    abnormal_liver_function: bool = False,
    prior_stroke: bool = False,
    bleeding_history_or_predisposition: bool = False,
    labile_inr: bool = False,
    on_drugs_predisposing_to_bleeding: bool = False,
    alcohol_use_8_or_more_units_per_week: bool = False,
) -> HasBledFeatures:
    return HasBledFeatures(
        age_years=age_years,
        uncontrolled_hypertension=uncontrolled_hypertension,
        abnormal_renal_function=abnormal_renal_function,
        abnormal_liver_function=abnormal_liver_function,
        prior_stroke=prior_stroke,
        bleeding_history_or_predisposition=bleeding_history_or_predisposition,
        labile_inr=labile_inr,
        on_drugs_predisposing_to_bleeding=on_drugs_predisposing_to_bleeding,
        alcohol_use_8_or_more_units_per_week=alcohol_use_8_or_more_units_per_week,
    )


class TestComponentContribution:
    def test_no_factors_scores_zero(self) -> None:
        assert has_bled_score(_features()) == 0

    @pytest.mark.parametrize(
        "field",
        [
            "uncontrolled_hypertension",
            "abnormal_renal_function",
            "abnormal_liver_function",
            "prior_stroke",
            "bleeding_history_or_predisposition",
            "labile_inr",
            "on_drugs_predisposing_to_bleeding",
            "alcohol_use_8_or_more_units_per_week",
        ],
    )
    def test_each_field_adds_one(self, field: str) -> None:
        assert has_bled_score(_features(**{field: True})) == 1

    def test_abnormal_renal_and_liver_score_independently(self) -> None:
        assert has_bled_score(
            _features(abnormal_renal_function=True, abnormal_liver_function=True)
        ) == 2

    def test_drugs_and_alcohol_score_independently(self) -> None:
        assert has_bled_score(
            _features(
                on_drugs_predisposing_to_bleeding=True,
                alcohol_use_8_or_more_units_per_week=True,
            )
        ) == 2


class TestAgeThreshold:
    def test_age_65_does_not_score(self) -> None:
        assert has_bled_score(_features(age_years=65)) == 0

    def test_age_66_scores(self) -> None:
        assert has_bled_score(_features(age_years=66)) == 1

    def test_age_80_scores(self) -> None:
        assert has_bled_score(_features(age_years=80)) == 1


class TestScoreRange:
    def test_maximum_score_is_nine(self) -> None:
        score = has_bled_score(
            _features(
                age_years=80,
                uncontrolled_hypertension=True,
                abnormal_renal_function=True,
                abnormal_liver_function=True,
                prior_stroke=True,
                bleeding_history_or_predisposition=True,
                labile_inr=True,
                on_drugs_predisposing_to_bleeding=True,
                alcohol_use_8_or_more_units_per_week=True,
            )
        )
        assert score == 9


class TestRiskBands:
    def test_score_zero_is_low_to_moderate(self) -> None:
        result = has_bled_assessment(_features())
        assert result.score == 0
        assert result.risk_band == "low_to_moderate"

    def test_score_two_is_low_to_moderate(self) -> None:
        result = has_bled_assessment(
            _features(
                uncontrolled_hypertension=True,
                prior_stroke=True,
            )
        )
        assert result.score == 2
        assert result.risk_band == "low_to_moderate"

    def test_score_three_is_high(self) -> None:
        result = has_bled_assessment(
            _features(
                uncontrolled_hypertension=True,
                prior_stroke=True,
                labile_inr=True,
            )
        )
        assert result.score == 3
        assert result.risk_band == "high"


class TestEscDoNotWithholdLanguage:
    def test_high_risk_explicitly_says_do_not_withhold(self) -> None:
        result = has_bled_assessment(
            _features(
                uncontrolled_hypertension=True,
                prior_stroke=True,
                labile_inr=True,
            )
        )
        assert "do not withhold" in result.recommended_management.lower()
        assert "ESC 2020" in result.recommended_management


class TestModifiableFactors:
    def test_modifiable_factors_listed_when_present(self) -> None:
        result = has_bled_assessment(
            _features(
                uncontrolled_hypertension=True,
                labile_inr=True,
                on_drugs_predisposing_to_bleeding=True,
                alcohol_use_8_or_more_units_per_week=True,
            )
        )
        assert "uncontrolled hypertension" in result.modifiable_factors_present
        assert any("labile INR" in f for f in result.modifiable_factors_present)
        assert any("antiplatelet" in f or "NSAID" in f for f in result.modifiable_factors_present)
        assert any("alcohol" in f.lower() for f in result.modifiable_factors_present)

    def test_non_modifiable_factors_not_listed_as_modifiable(self) -> None:
        result = has_bled_assessment(
            _features(prior_stroke=True, abnormal_renal_function=True)
        )
        assert result.modifiable_factors_present == ()


class TestInvalidInput:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError, match="age_years must be non-negative"):
            has_bled_score(_features(age_years=-1))


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = has_bled_assessment(_features())
        assert "Pisters 2010" in result.citations
        assert "ESC 2020" in result.citations

    def test_criteria_labels_listed_when_present(self) -> None:
        criteria = has_bled_criteria(
            _features(prior_stroke=True, labile_inr=True)
        )
        assert "prior stroke" in criteria
        assert "labile INR" in criteria
        assert len(criteria) == 2
