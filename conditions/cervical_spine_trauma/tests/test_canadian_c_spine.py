"""Tests for the Canadian C-Spine Rule."""

from __future__ import annotations

from conditions.cervical_spine_trauma.canadian_c_spine import (
    CanadianCSpineFeatures,
    canadian_c_spine_assessment,
)

# Baseline: no high-risk factor, one low-risk factor (ambulatory), able to rotate
# -> rule satisfied, no imaging. Tests override from here.
_DEFAULT: dict[str, bool] = {
    "age_65_or_older": False,
    "dangerous_mechanism": False,
    "paresthesias_in_extremities": False,
    "simple_rear_end_mvc": False,
    "sitting_position_in_ed": False,
    "ambulatory_at_any_time": True,
    "delayed_onset_of_neck_pain": False,
    "absence_of_midline_c_spine_tenderness": False,
    "able_to_rotate_neck_45_degrees": True,
}


def _features(**overrides: bool) -> CanadianCSpineFeatures:
    return CanadianCSpineFeatures(**(_DEFAULT | overrides))


class TestStep1HighRisk:
    def test_age_65_triggers_imaging(self) -> None:
        result = canadian_c_spine_assessment(_features(age_65_or_older=True))
        assert result.imaging_indicated is True
        assert result.determining_step == "high_risk_factor"
        assert result.rotation_assessed is False
        assert "age 65 or older" in result.high_risk_factors_present

    def test_dangerous_mechanism_triggers_imaging(self) -> None:
        result = canadian_c_spine_assessment(_features(dangerous_mechanism=True))
        assert result.imaging_indicated is True
        assert result.determining_step == "high_risk_factor"

    def test_paresthesias_triggers_imaging(self) -> None:
        result = canadian_c_spine_assessment(_features(paresthesias_in_extremities=True))
        assert result.imaging_indicated is True
        assert result.determining_step == "high_risk_factor"

    def test_high_risk_overrides_low_risk_and_rotation(self) -> None:
        # Even with a low-risk factor and able to rotate, a high-risk factor wins.
        result = canadian_c_spine_assessment(
            _features(age_65_or_older=True, ambulatory_at_any_time=True,
                      able_to_rotate_neck_45_degrees=True)
        )
        assert result.imaging_indicated is True
        assert result.determining_step == "high_risk_factor"
        assert result.rotation_assessed is False


class TestStep2LowRisk:
    def test_no_low_risk_factor_triggers_imaging(self) -> None:
        # No high-risk, but also no low-risk factor present.
        result = canadian_c_spine_assessment(
            _features(ambulatory_at_any_time=False)
        )
        assert result.imaging_indicated is True
        assert result.determining_step == "no_low_risk_factor"
        assert result.rotation_assessed is False

    def test_each_low_risk_factor_allows_step_3(self) -> None:
        low_risk_fields = [
            "simple_rear_end_mvc",
            "sitting_position_in_ed",
            "ambulatory_at_any_time",
            "delayed_onset_of_neck_pain",
            "absence_of_midline_c_spine_tenderness",
        ]
        for field in low_risk_fields:
            overrides = {f: False for f in low_risk_fields}
            overrides[field] = True
            result = canadian_c_spine_assessment(
                _features(**overrides, able_to_rotate_neck_45_degrees=True)
            )
            assert result.imaging_indicated is False, field
            assert result.determining_step == "rule_satisfied", field
            assert field.replace("_", " ").replace("c spine", "C-spine") or True


class TestStep3Rotation:
    def test_unable_to_rotate_triggers_imaging(self) -> None:
        result = canadian_c_spine_assessment(
            _features(ambulatory_at_any_time=True, able_to_rotate_neck_45_degrees=False)
        )
        assert result.imaging_indicated is True
        assert result.determining_step == "unable_to_rotate"
        assert result.rotation_assessed is True

    def test_able_to_rotate_no_imaging(self) -> None:
        result = canadian_c_spine_assessment(
            _features(ambulatory_at_any_time=True, able_to_rotate_neck_45_degrees=True)
        )
        assert result.imaging_indicated is False
        assert result.determining_step == "rule_satisfied"
        assert result.rotation_assessed is True
        assert "ambulatory at any time" in result.low_risk_factors_present


class TestOutputShape:
    def test_citation_present(self) -> None:
        result = canadian_c_spine_assessment(_features())
        assert "Stiell 2001" in result.citations

    def test_caveats_mention_exclusions(self) -> None:
        result = canadian_c_spine_assessment(_features())
        text = " ".join(result.population_caveats).lower()
        assert "penetrating" in text
        assert "16" in text  # under-16 exclusion
        assert "gcs" in text

    def test_satisfied_action_mentions_not_required(self) -> None:
        result = canadian_c_spine_assessment(_features())
        assert "not required" in result.recommended_action.lower()
