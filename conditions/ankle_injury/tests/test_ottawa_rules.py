"""Tests for the Ottawa Ankle and Foot Rules.

Coverage targets:
- Each applicability factor independently disables the rule.
- Applicability check takes precedence over criterion check.
- Absence of zone pain means imaging not indicated.
- Each individual criterion triggers imaging when zone pain is present.
- Multiple criteria are all enumerated.
- Output shape: rule_applies, excluded_by, imaging_indicated,
  indicating_criteria, recommended_action, rationale, citations.
"""

from __future__ import annotations

import pytest

from conditions.ankle_injury.ottawa_rules import (
    AnkleAssessmentFeatures,
    ApplicabilityFactors,
    FootAssessmentFeatures,
    ottawa_ankle_assessment,
    ottawa_foot_assessment,
)

_APPLICABILITY_DEFAULT: dict[str, bool] = {
    "age_under_18": False,
    "intoxication": False,
    "distracting_injury": False,
    "decreased_sensation_or_neurologic_deficit": False,
    "gross_deformity": False,
    "isolated_skin_injury": False,
    "head_injury_or_decreased_consciousness": False,
}

_APPLICABILITY_FIELDS: tuple[str, ...] = tuple(_APPLICABILITY_DEFAULT.keys())


def _applicability(**overrides: bool) -> ApplicabilityFactors:
    return ApplicabilityFactors(**(_APPLICABILITY_DEFAULT | overrides))


def _ankle_features(
    *,
    pain_in_malleolar_zone: bool = False,
    tender_lateral_malleolus_distal_6cm: bool = False,
    tender_medial_malleolus_distal_6cm: bool = False,
    unable_to_bear_weight_immediately_and_now: bool = False,
) -> AnkleAssessmentFeatures:
    return AnkleAssessmentFeatures(
        pain_in_malleolar_zone=pain_in_malleolar_zone,
        tender_lateral_malleolus_distal_6cm=tender_lateral_malleolus_distal_6cm,
        tender_medial_malleolus_distal_6cm=tender_medial_malleolus_distal_6cm,
        unable_to_bear_weight_immediately_and_now=unable_to_bear_weight_immediately_and_now,
    )


def _foot_features(
    *,
    pain_in_midfoot_zone: bool = False,
    tender_5th_metatarsal_base: bool = False,
    tender_navicular: bool = False,
    unable_to_bear_weight_immediately_and_now: bool = False,
) -> FootAssessmentFeatures:
    return FootAssessmentFeatures(
        pain_in_midfoot_zone=pain_in_midfoot_zone,
        tender_5th_metatarsal_base=tender_5th_metatarsal_base,
        tender_navicular=tender_navicular,
        unable_to_bear_weight_immediately_and_now=unable_to_bear_weight_immediately_and_now,
    )


class TestApplicabilityAnkle:
    @pytest.mark.parametrize("field", _APPLICABILITY_FIELDS)
    def test_each_factor_disables_the_rule(self, field: str) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
            ),
            _applicability(**{field: True}),
        )
        assert result.rule_applies is False
        assert len(result.excluded_by) == 1
        assert result.imaging_indicated is False

    def test_applicability_takes_precedence_over_criterion(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
                tender_medial_malleolus_distal_6cm=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(intoxication=True),
        )
        assert result.rule_applies is False
        assert result.imaging_indicated is False
        assert result.indicating_criteria == ()

    def test_multiple_excluding_factors_all_listed(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(age_under_18=True, intoxication=True),
        )
        assert result.rule_applies is False
        assert len(result.excluded_by) == 2


class TestApplicabilityFoot:
    @pytest.mark.parametrize("field", _APPLICABILITY_FIELDS)
    def test_each_factor_disables_the_rule(self, field: str) -> None:
        result = ottawa_foot_assessment(
            _foot_features(
                pain_in_midfoot_zone=True,
                tender_5th_metatarsal_base=True,
            ),
            _applicability(**{field: True}),
        )
        assert result.rule_applies is False
        assert len(result.excluded_by) == 1
        assert result.imaging_indicated is False


class TestAnkleRule:
    def test_no_pain_in_zone_no_imaging(self) -> None:
        result = ottawa_ankle_assessment(_ankle_features(), _applicability())
        assert result.rule_applies is True
        assert result.imaging_indicated is False
        assert result.indicating_criteria == ()

    def test_zone_pain_alone_no_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(),
        )
        assert result.rule_applies is True
        assert result.imaging_indicated is False
        assert result.indicating_criteria == ()

    def test_lateral_malleolus_tenderness_triggers_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("lateral malleolus" in c for c in result.indicating_criteria)

    def test_medial_malleolus_tenderness_triggers_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_medial_malleolus_distal_6cm=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("medial malleolus" in c for c in result.indicating_criteria)

    def test_inability_to_bear_weight_triggers_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("bear weight" in c for c in result.indicating_criteria)

    def test_tenderness_without_zone_pain_does_not_indicate_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(tender_lateral_malleolus_distal_6cm=True),
            _applicability(),
        )
        assert result.imaging_indicated is False

    def test_all_three_criteria_listed_when_all_positive(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
                tender_medial_malleolus_distal_6cm=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert len(result.indicating_criteria) == 3


class TestFootRule:
    def test_no_pain_in_zone_no_imaging(self) -> None:
        result = ottawa_foot_assessment(_foot_features(), _applicability())
        assert result.rule_applies is True
        assert result.imaging_indicated is False

    def test_zone_pain_alone_no_imaging(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(pain_in_midfoot_zone=True),
            _applicability(),
        )
        assert result.imaging_indicated is False

    def test_5th_metatarsal_tenderness_triggers_imaging(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(
                pain_in_midfoot_zone=True,
                tender_5th_metatarsal_base=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("5th metatarsal" in c for c in result.indicating_criteria)

    def test_navicular_tenderness_triggers_imaging(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(
                pain_in_midfoot_zone=True,
                tender_navicular=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert any("navicular" in c for c in result.indicating_criteria)

    def test_inability_to_bear_weight_triggers_imaging(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(
                pain_in_midfoot_zone=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True

    def test_tenderness_without_zone_pain_does_not_indicate_imaging(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(tender_5th_metatarsal_base=True),
            _applicability(),
        )
        assert result.imaging_indicated is False

    def test_all_three_criteria_listed_when_all_positive(self) -> None:
        result = ottawa_foot_assessment(
            _foot_features(
                pain_in_midfoot_zone=True,
                tender_5th_metatarsal_base=True,
                tender_navicular=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True
        assert len(result.indicating_criteria) == 3


class TestOutputShape:
    def test_ankle_result_has_citations(self) -> None:
        result = ottawa_ankle_assessment(_ankle_features(), _applicability())
        assert "Stiell 1992" in result.citations

    def test_foot_result_has_citations(self) -> None:
        result = ottawa_foot_assessment(_foot_features(), _applicability())
        assert "Stiell 1992" in result.citations

    def test_rule_does_not_apply_recommendation_mentions_clinical_judgment(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(age_under_18=True),
        )
        assert "clinical judgment" in result.recommended_action.lower()

    def test_imaging_indicated_recommendation_mentions_radiography(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
            ),
            _applicability(),
        )
        assert "radiography" in result.recommended_action.lower()

    def test_negative_radiograph_caveat_present_when_imaging_indicated(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                tender_lateral_malleolus_distal_6cm=True,
            ),
            _applicability(),
        )
        assert "soft tissue" in result.recommended_action.lower()


class TestClinicalVignettes:
    """Abstract vignettes exercising the rule at decision boundaries."""

    def test_walking_after_low_energy_inversion_no_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(),
        )
        assert result.imaging_indicated is False

    def test_unable_to_bear_weight_with_malleolar_pain_imaging(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(
                pain_in_malleolar_zone=True,
                unable_to_bear_weight_immediately_and_now=True,
            ),
            _applicability(),
        )
        assert result.imaging_indicated is True

    def test_intoxicated_patient_rule_does_not_apply(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(intoxication=True),
        )
        assert result.rule_applies is False
        assert "intoxication" in result.excluded_by

    def test_pediatric_patient_rule_does_not_apply(self) -> None:
        result = ottawa_ankle_assessment(
            _ankle_features(pain_in_malleolar_zone=True),
            _applicability(age_under_18=True),
        )
        assert result.rule_applies is False
        assert "age under 18" in result.excluded_by
