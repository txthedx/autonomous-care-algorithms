"""Tests for the Ottawa SAH Rule."""

from __future__ import annotations

from conditions.subarachnoid_hemorrhage.ottawa_sah import (
    SahApplicability,
    SahFeatures,
    ottawa_sah_assessment,
)

# Eligible patient: inclusion met, no exclusions.
_ELIGIBLE: dict[str, bool] = {
    "new_severe_atraumatic_headache_peaking_within_1_hour": True,
    "alert_gcs_15": True,
    "age_15_or_older": True,
    "new_neurologic_deficit": False,
    "prior_aneurysm_sah_or_brain_tumor": False,
    "chronic_recurrent_headache": False,
}

# No criteria present.
_NO_CRITERIA: dict[str, bool] = {
    "age_40_or_older": False,
    "neck_pain_or_stiffness": False,
    "witnessed_loss_of_consciousness": False,
    "onset_during_exertion": False,
    "thunderclap_headache": False,
    "limited_neck_flexion_on_exam": False,
}


def _applicability(**overrides: bool) -> SahApplicability:
    return SahApplicability(**(_ELIGIBLE | overrides))


def _features(**overrides: bool) -> SahFeatures:
    return SahFeatures(**(_NO_CRITERIA | overrides))


class TestRuleOut:
    def test_eligible_no_criteria_rules_out(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability())
        assert result.rule_applicable is True
        assert result.investigation_indicated is False
        assert result.positive_criteria == ()
        assert "excluded" in result.recommended_action.lower()


class TestCriteria:
    def test_each_criterion_triggers_investigation(self) -> None:
        for field in _NO_CRITERIA:
            result = ottawa_sah_assessment(_features(**{field: True}), _applicability())
            assert result.rule_applicable is True, field
            assert result.investigation_indicated is True, field
            assert len(result.positive_criteria) == 1, field

    def test_thunderclap_label(self) -> None:
        result = ottawa_sah_assessment(_features(thunderclap_headache=True), _applicability())
        assert "thunderclap headache" in result.positive_criteria

    def test_multiple_criteria_listed(self) -> None:
        result = ottawa_sah_assessment(
            _features(age_40_or_older=True, neck_pain_or_stiffness=True),
            _applicability(),
        )
        assert len(result.positive_criteria) == 2


class TestApplicabilityGate:
    def test_headache_not_meeting_inclusion(self) -> None:
        result = ottawa_sah_assessment(
            _features(thunderclap_headache=True),
            _applicability(new_severe_atraumatic_headache_peaking_within_1_hour=False),
        )
        assert result.rule_applicable is False
        assert result.investigation_indicated is None
        assert any("inclusion" in r for r in result.inapplicability_reasons)

    def test_not_alert(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability(alert_gcs_15=False))
        assert result.rule_applicable is False
        assert any("not alert" in r for r in result.inapplicability_reasons)

    def test_under_15(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability(age_15_or_older=False))
        assert result.rule_applicable is False
        assert any("under 15" in r for r in result.inapplicability_reasons)

    def test_new_neurologic_deficit_excludes(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability(new_neurologic_deficit=True))
        assert result.rule_applicable is False
        assert any("neurologic deficit" in r for r in result.inapplicability_reasons)

    def test_prior_aneurysm_excludes(self) -> None:
        result = ottawa_sah_assessment(
            _features(), _applicability(prior_aneurysm_sah_or_brain_tumor=True)
        )
        assert result.rule_applicable is False
        assert any("aneurysm" in r for r in result.inapplicability_reasons)

    def test_chronic_recurrent_headache_excludes(self) -> None:
        result = ottawa_sah_assessment(
            _features(), _applicability(chronic_recurrent_headache=True)
        )
        assert result.rule_applicable is False
        assert any("chronic recurrent" in r for r in result.inapplicability_reasons)

    def test_inapplicable_action_mentions_does_not_apply(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability(alert_gcs_15=False))
        assert "does not apply" in result.recommended_action.lower()


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability())
        assert "Perry 2013" in result.citations

    def test_caveats_mention_sensitivity_specificity(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability())
        text = " ".join(result.population_caveats).lower()
        assert "sensitiv" in text and "specific" in text

    def test_rationale_non_empty(self) -> None:
        result = ottawa_sah_assessment(_features(), _applicability())
        assert result.rationale.strip() != ""
