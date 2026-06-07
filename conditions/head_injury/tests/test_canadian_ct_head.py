"""Tests for the Canadian CT Head Rule."""

from __future__ import annotations

from conditions.head_injury.canadian_ct_head import (
    CanadianCtHeadFeatures,
    canadian_ct_head_assessment,
)

# Baseline: no factor present -> CT not indicated.
_DEFAULT: dict[str, bool] = {
    "gcs_below_15_at_2_hours": False,
    "suspected_open_or_depressed_skull_fracture": False,
    "sign_of_basal_skull_fracture": False,
    "vomiting_2_or_more_episodes": False,
    "age_65_or_older": False,
    "retrograde_amnesia_30_min_or_more": False,
    "dangerous_mechanism": False,
}

_HIGH_RISK = [
    "gcs_below_15_at_2_hours",
    "suspected_open_or_depressed_skull_fracture",
    "sign_of_basal_skull_fracture",
    "vomiting_2_or_more_episodes",
    "age_65_or_older",
]
_MEDIUM_RISK = [
    "retrograde_amnesia_30_min_or_more",
    "dangerous_mechanism",
]


def _features(**overrides: bool) -> CanadianCtHeadFeatures:
    return CanadianCtHeadFeatures(**(_DEFAULT | overrides))


class TestNoFactors:
    def test_none_no_ct(self) -> None:
        result = canadian_ct_head_assessment(_features())
        assert result.ct_indicated is False
        assert result.high_risk_factors_present == ()
        assert result.medium_risk_factors_present == ()

    def test_no_factors_action_mentions_not_required(self) -> None:
        result = canadian_ct_head_assessment(_features())
        assert "not required" in result.recommended_action.lower()


class TestHighRiskFactors:
    def test_each_high_risk_factor_indicates_ct(self) -> None:
        for field in _HIGH_RISK:
            result = canadian_ct_head_assessment(_features(**{field: True}))
            assert result.ct_indicated is True, field
            assert len(result.high_risk_factors_present) == 1, field

    def test_high_risk_action_mentions_neurosurgical(self) -> None:
        result = canadian_ct_head_assessment(_features(age_65_or_older=True))
        assert "neurosurgical" in result.recommended_action.lower()

    def test_basal_skull_fracture_label(self) -> None:
        result = canadian_ct_head_assessment(_features(sign_of_basal_skull_fracture=True))
        assert "basal skull fracture" in result.high_risk_factors_present[0]


class TestMediumRiskFactors:
    def test_each_medium_risk_factor_indicates_ct(self) -> None:
        for field in _MEDIUM_RISK:
            result = canadian_ct_head_assessment(_features(**{field: True}))
            assert result.ct_indicated is True, field
            assert len(result.medium_risk_factors_present) == 1, field
            assert result.high_risk_factors_present == (), field

    def test_medium_risk_action_mentions_brain_injury(self) -> None:
        result = canadian_ct_head_assessment(_features(dangerous_mechanism=True))
        assert "brain injury" in result.recommended_action.lower()


class TestTierReporting:
    def test_high_risk_takes_precedence_in_action(self) -> None:
        # Both tiers present: action should reflect the high-risk (neurosurgical) tier.
        result = canadian_ct_head_assessment(
            _features(age_65_or_older=True, dangerous_mechanism=True)
        )
        assert result.ct_indicated is True
        assert "neurosurgical" in result.recommended_action.lower()
        assert len(result.high_risk_factors_present) == 1
        assert len(result.medium_risk_factors_present) == 1

    def test_all_factors_listed(self) -> None:
        result = canadian_ct_head_assessment(_features(**{k: True for k in _DEFAULT}))
        assert len(result.high_risk_factors_present) == 5
        assert len(result.medium_risk_factors_present) == 2


class TestOutputShape:
    def test_citation_present(self) -> None:
        result = canadian_ct_head_assessment(_features())
        assert "Stiell 2001" in result.citations

    def test_caveats_mention_inclusion_and_exclusions(self) -> None:
        result = canadian_ct_head_assessment(_features())
        text = " ".join(result.population_caveats).lower()
        assert "13-15" in text
        assert "16" in text  # under-16 exclusion
        assert "anticoagulant" in text

    def test_rationale_non_empty(self) -> None:
        result = canadian_ct_head_assessment(_features())
        assert result.rationale.strip() != ""
