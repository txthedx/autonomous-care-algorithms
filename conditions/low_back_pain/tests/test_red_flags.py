"""Tests for the low back pain red flag screen.

Coverage targets:
- Each feature in each category individually.
- Combinations across categories with the documented precedence
  (emergency > high-concern > moderate).
- No-flag baseline.
- Output shape: presence of category lists, urgency band, rationale, citations.
"""

from __future__ import annotations

import pytest

from conditions.low_back_pain.red_flags import (
    RedFlagFeatures,
    red_flag_assessment,
)

_DEFAULTS: dict[str, bool] = {
    "saddle_anesthesia": False,
    "new_urinary_retention": False,
    "new_fecal_incontinence": False,
    "bilateral_leg_weakness": False,
    "progressive_neurologic_deficit": False,
    "history_of_cancer_with_new_pain": False,
    "unexplained_weight_loss": False,
    "pain_unrelieved_by_rest": False,
    "fever": False,
    "intravenous_drug_use": False,
    "immunosuppression": False,
    "recent_spinal_procedure_or_bacteremia": False,
    "significant_trauma": False,
    "minor_trauma_with_osteoporosis_risk": False,
    "long_term_corticosteroid_use": False,
    "age_over_50_new_severe_pain": False,
    "age_under_18_significant_pain": False,
    "no_improvement_after_4_to_6_weeks": False,
}

_EMERGENCY_FIELDS: tuple[str, ...] = (
    "saddle_anesthesia",
    "new_urinary_retention",
    "new_fecal_incontinence",
    "bilateral_leg_weakness",
    "progressive_neurologic_deficit",
)

_HIGH_CONCERN_FIELDS: tuple[str, ...] = (
    "history_of_cancer_with_new_pain",
    "unexplained_weight_loss",
    "pain_unrelieved_by_rest",
    "fever",
    "intravenous_drug_use",
    "immunosuppression",
    "recent_spinal_procedure_or_bacteremia",
)

_MODERATE_FIELDS: tuple[str, ...] = (
    "significant_trauma",
    "minor_trauma_with_osteoporosis_risk",
    "long_term_corticosteroid_use",
    "age_over_50_new_severe_pain",
    "age_under_18_significant_pain",
    "no_improvement_after_4_to_6_weeks",
)


def _features(**overrides: bool) -> RedFlagFeatures:
    data = _DEFAULTS | overrides
    return RedFlagFeatures(**data)


class TestNoFlags:
    def test_all_false_yields_no_flags(self) -> None:
        result = red_flag_assessment(_features())
        assert result.emergency_flags == ()
        assert result.high_concern_flags == ()
        assert result.moderate_flags == ()

    def test_no_flags_recommends_proceeding_to_start_back(self) -> None:
        result = red_flag_assessment(_features())
        assert "STarT Back" in result.recommended_urgency

    def test_no_flags_carries_citation(self) -> None:
        result = red_flag_assessment(_features())
        assert "NICE NG59" in result.citations


class TestEmergencyFlags:
    @pytest.mark.parametrize("field", _EMERGENCY_FIELDS)
    def test_each_emergency_feature_triggers_emergency_band(self, field: str) -> None:
        result = red_flag_assessment(_features(**{field: True}))
        assert len(result.emergency_flags) == 1
        assert "Same-day emergency" in result.recommended_urgency
        assert "cauda equina" in result.rationale.lower()

    def test_multiple_emergency_features_listed(self) -> None:
        result = red_flag_assessment(
            _features(saddle_anesthesia=True, new_urinary_retention=True)
        )
        assert len(result.emergency_flags) == 2

    def test_emergency_overrides_high_concern_and_moderate(self) -> None:
        result = red_flag_assessment(
            _features(
                saddle_anesthesia=True,
                fever=True,
                significant_trauma=True,
            )
        )
        assert "Same-day emergency" in result.recommended_urgency
        assert len(result.emergency_flags) == 1
        assert len(result.high_concern_flags) == 1
        assert len(result.moderate_flags) == 1


class TestHighConcernFlags:
    @pytest.mark.parametrize("field", _HIGH_CONCERN_FIELDS)
    def test_each_high_concern_feature_triggers_high_concern_band(self, field: str) -> None:
        result = red_flag_assessment(_features(**{field: True}))
        assert result.emergency_flags == ()
        assert len(result.high_concern_flags) == 1
        assert "Urgent workup" in result.recommended_urgency
        assert "do not stratify" in result.recommended_urgency.lower()

    def test_high_concern_overrides_moderate(self) -> None:
        result = red_flag_assessment(
            _features(fever=True, significant_trauma=True)
        )
        assert "Urgent workup" in result.recommended_urgency
        assert len(result.high_concern_flags) == 1
        assert len(result.moderate_flags) == 1


class TestModerateFlags:
    @pytest.mark.parametrize("field", _MODERATE_FIELDS)
    def test_each_moderate_feature_triggers_moderate_band(self, field: str) -> None:
        result = red_flag_assessment(_features(**{field: True}))
        assert result.emergency_flags == ()
        assert result.high_concern_flags == ()
        assert len(result.moderate_flags) == 1
        assert "Targeted workup" in result.recommended_urgency


class TestAllFlagsTrue:
    def test_all_true_yields_emergency_band_with_all_categories_populated(self) -> None:
        result = red_flag_assessment(
            _features(**{field: True for field in _DEFAULTS})
        )
        assert "Same-day emergency" in result.recommended_urgency
        assert len(result.emergency_flags) == len(_EMERGENCY_FIELDS)
        assert len(result.high_concern_flags) == len(_HIGH_CONCERN_FIELDS)
        assert len(result.moderate_flags) == len(_MODERATE_FIELDS)


class TestOutputShape:
    def test_citations_are_non_empty(self) -> None:
        result = red_flag_assessment(_features(fever=True))
        assert len(result.citations) >= 1
        assert all(isinstance(c, str) for c in result.citations)

    def test_rationale_is_non_empty(self) -> None:
        result = red_flag_assessment(_features(saddle_anesthesia=True))
        assert result.rationale.strip() != ""
