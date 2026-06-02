"""Tests for the Ottawa Knee Rule.

Coverage targets:
- Each applicability factor independently disables the rule.
- Applicability check takes precedence over criterion check.
- Each individual criterion triggers imaging.
- Age boundary at 54 vs 55.
- Multiple criteria are all enumerated.
- Invalid input raises.
- Output shape: rule_applies, excluded_by, imaging_indicated,
  indicating_criteria, recommended_action, rationale, citations.
"""

from __future__ import annotations

import pytest

from conditions.knee_injury.ottawa_knee_rule import (
    ApplicabilityFactors,
    OttawaKneeFeatures,
    ottawa_knee_assessment,
)

_APPLICABILITY_DEFAULT: dict[str, bool] = {
    "age_under_18": False,
    "isolated_skin_injury": False,
    "gross_deformity": False,
    "decreased_consciousness": False,
    "paraplegia_or_multiple_injuries": False,
    "re_presentation_more_than_7_days": False,
}

_APPLICABILITY_FIELDS: tuple[str, ...] = tuple(_APPLICABILITY_DEFAULT.keys())


def _applicability(**overrides: bool) -> ApplicabilityFactors:
    return ApplicabilityFactors(**(_APPLICABILITY_DEFAULT | overrides))


def _features(
    *,
    age_years: int = 30,
    isolated_patellar_tenderness: bool = False,
    tender_fibular_head: bool = False,
    unable_to_flex_to_90_degrees: bool = False,
    unable_to_bear_weight_immediately_and_now: bool = False,
) -> OttawaKneeFeatures:
    return OttawaKneeFeatures(
        age_years=age_years,
        isolated_patellar_tenderness=isolated_patellar_tenderness,
        tender_fibular_head=tender_fibular_head,
        unable_to_flex_to_90_degrees=unable_to_flex_to_90_degrees,
        unable_to_bear_weight_immediately_and_now=unable_to_bear_weight_immediately_and_now,
    )


class TestApplicability:
    @pytest.mark.parametrize("field", _APPLICABILITY_FIELDS)
    def test_each_factor_disables_the_rule(self, field: str) -> None:
        result = ottawa_knee_assessment(
            _features(isolated_patellar_tenderness=True),
            _applicability(**{field: True}),
        )
        assert result.rule_applies is False
        assert len(result.excluded_by) == 1
        assert result.imaging_indicated is False

    def test_applicability_takes_precedence_over_criterion(self) -> None:
        result = ottawa_knee_assessment(
            _features(
                age_years=70,
                isolated_patellar_tenderness=True,
                tender_fibular_head=True,
                unable_to_flex_to_90_degrees=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(gross_deformity=True),
        )
        assert result.rule_applies is False
        assert result.imaging_indicated is False
        assert result.indicating_criteria == ()

    def test_multiple_excluding_factors_all_listed(self) -> None:
        result = ottawa_knee_assessment(
            _features(),
            _applicability(age_under_18=True, isolated_skin_injury=True),
        )
        assert result.rule_applies is False
        assert len(result.excluded_by) == 2

    def test_pediatric_recommendation_mentions_pittsburgh(self) -> None:
        result = ottawa_knee_assessment(
            _features(),
            _applicability(age_under_18=True),
        )
        assert "Pittsburgh" in result.recommended_action


class TestAgeCriterion:
    @pytest.mark.parametrize("age", [18, 30, 50, 54])
    def test_age_under_55_does_not_trigger(self, age: int) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=age),
            _applicability(),
        )
        assert result.imaging_indicated is False

    @pytest.mark.parametrize("age", [55, 60, 80])
    def test_age_55_or_older_triggers(self, age: int) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=age),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("55" in c for c in result.indicating_criteria)


class TestIndividualCriteria:
    def test_no_criteria_no_imaging(self) -> None:
        result = ottawa_knee_assessment(_features(), _applicability())
        assert result.rule_applies is True
        assert result.imaging_indicated is False
        assert result.indicating_criteria == ()

    def test_isolated_patellar_tenderness_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(isolated_patellar_tenderness=True),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("patellar" in c for c in result.indicating_criteria)

    def test_fibular_head_tenderness_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(tender_fibular_head=True),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("fibula" in c for c in result.indicating_criteria)

    def test_inability_to_flex_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(unable_to_flex_to_90_degrees=True),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("flex" in c for c in result.indicating_criteria)

    def test_inability_to_bear_weight_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(unable_to_bear_weight_immediately_and_now=True),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("bear weight" in c for c in result.indicating_criteria)


class TestMultipleCriteria:
    def test_all_five_criteria_listed(self) -> None:
        result = ottawa_knee_assessment(
            _features(
                age_years=60,
                isolated_patellar_tenderness=True,
                tender_fibular_head=True,
                unable_to_flex_to_90_degrees=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert len(result.indicating_criteria) == 5

    def test_age_plus_tenderness_listed(self) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=65, tender_fibular_head=True),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert len(result.indicating_criteria) == 2


class TestInvalidInput:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError, match="age_years must be non-negative"):
            ottawa_knee_assessment(_features(age_years=-1), _applicability())


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = ottawa_knee_assessment(_features(), _applicability())
        assert "Stiell 1995" in result.citations
        assert "Bachmann 2004" in result.citations

    def test_imaging_recommendation_mentions_radiography(self) -> None:
        result = ottawa_knee_assessment(
            _features(tender_fibular_head=True),
            _applicability(),
        )
        assert "radiography" in result.recommended_action.lower()

    def test_imaging_recommendation_mentions_soft_tissue_caveat(self) -> None:
        result = ottawa_knee_assessment(
            _features(tender_fibular_head=True),
            _applicability(),
        )
        action = result.recommended_action.lower()
        assert "soft tissue" in action

    def test_no_imaging_recommendation_mentions_reassessment(self) -> None:
        result = ottawa_knee_assessment(_features(), _applicability())
        assert "reassess" in result.recommended_action.lower()

    def test_rule_does_not_apply_recommendation_mentions_clinical_judgment(self) -> None:
        result = ottawa_knee_assessment(
            _features(),
            _applicability(gross_deformity=True),
        )
        assert "clinical judgment" in result.recommended_action.lower()


class TestClinicalVignettes:
    """Abstract vignettes exercising the rule at decision boundaries."""

    def test_young_walking_patient_no_tenderness_no_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=25),
            _applicability(),
        )
        assert result.imaging_indicated is False

    def test_older_adult_alone_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=70),
            _applicability(),
        )
        assert result.imaging_indicated is True

    def test_younger_adult_unable_to_flex_triggers_imaging(self) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=30, unable_to_flex_to_90_degrees=True),
            _applicability(),
        )
        assert result.imaging_indicated is True

    def test_pediatric_patient_rule_does_not_apply(self) -> None:
        result = ottawa_knee_assessment(
            _features(age_years=12),
            _applicability(age_under_18=True),
        )
        assert result.rule_applies is False
        assert "age under 18" in result.excluded_by
