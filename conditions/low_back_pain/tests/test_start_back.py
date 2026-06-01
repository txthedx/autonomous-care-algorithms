"""Tests for the STarT Back Screening Tool.

Coverage targets:
- Each of the 9 items contributes one point when "agree" / sufficiently bothersome.
- Psychosocial subscale covers items 5 through 9 only.
- Score range 0 to 9, psychosocial subscale range 0 to 5.
- Risk band boundaries: total 3 vs 4, psychosocial 3 vs 4.
- Bothersomeness level mapping per Hill 2008.
- Invalid bothersomeness raises.
"""

from __future__ import annotations

import pytest

from conditions.low_back_pain.start_back import (
    StartBackResponses,
    start_back_score,
    start_back_stratification,
)


def _responses(
    *,
    leg_pain_in_last_2_weeks: bool = False,
    shoulder_or_neck_pain_in_last_2_weeks: bool = False,
    walked_only_short_distances: bool = False,
    dressed_more_slowly: bool = False,
    not_safe_to_be_physically_active: bool = False,
    worrying_thoughts_a_lot: bool = False,
    pain_is_terrible_never_better: bool = False,
    not_enjoying_usual_things: bool = False,
    bothersomeness: str = "not_at_all",
) -> StartBackResponses:
    return StartBackResponses(
        leg_pain_in_last_2_weeks=leg_pain_in_last_2_weeks,
        shoulder_or_neck_pain_in_last_2_weeks=shoulder_or_neck_pain_in_last_2_weeks,
        walked_only_short_distances=walked_only_short_distances,
        dressed_more_slowly=dressed_more_slowly,
        not_safe_to_be_physically_active=not_safe_to_be_physically_active,
        worrying_thoughts_a_lot=worrying_thoughts_a_lot,
        pain_is_terrible_never_better=pain_is_terrible_never_better,
        not_enjoying_usual_things=not_enjoying_usual_things,
        bothersomeness=bothersomeness,  # type: ignore[arg-type]
    )


class TestItemContributions:
    def test_all_false_scores_zero(self) -> None:
        total, psych = start_back_score(_responses())
        assert total == 0
        assert psych == 0

    @pytest.mark.parametrize(
        "field",
        [
            "leg_pain_in_last_2_weeks",
            "shoulder_or_neck_pain_in_last_2_weeks",
            "walked_only_short_distances",
            "dressed_more_slowly",
        ],
    )
    def test_physical_item_adds_one_to_total_only(self, field: str) -> None:
        total, psych = start_back_score(_responses(**{field: True}))
        assert total == 1
        assert psych == 0

    @pytest.mark.parametrize(
        "field",
        [
            "not_safe_to_be_physically_active",
            "worrying_thoughts_a_lot",
            "pain_is_terrible_never_better",
            "not_enjoying_usual_things",
        ],
    )
    def test_psychosocial_item_adds_one_to_total_and_subscale(self, field: str) -> None:
        total, psych = start_back_score(_responses(**{field: True}))
        assert total == 1
        assert psych == 1


class TestBothersomenessMapping:
    @pytest.mark.parametrize("level", ["not_at_all", "slightly"])
    def test_low_bothersome_levels_score_zero(self, level: str) -> None:
        total, psych = start_back_score(_responses(bothersomeness=level))
        assert total == 0
        assert psych == 0

    @pytest.mark.parametrize("level", ["moderately", "very_much", "extremely"])
    def test_high_bothersome_levels_score_one(self, level: str) -> None:
        total, psych = start_back_score(_responses(bothersomeness=level))
        assert total == 1
        assert psych == 1

    def test_invalid_bothersomeness_raises(self) -> None:
        with pytest.raises(ValueError, match="bothersomeness must be one of"):
            start_back_score(_responses(bothersomeness="somewhat"))


class TestScoreRange:
    def test_minimum_score_is_zero(self) -> None:
        total, psych = start_back_score(_responses())
        assert total == 0
        assert psych == 0

    def test_maximum_total_is_nine_and_psychosocial_is_five(self) -> None:
        total, psych = start_back_score(
            _responses(
                leg_pain_in_last_2_weeks=True,
                shoulder_or_neck_pain_in_last_2_weeks=True,
                walked_only_short_distances=True,
                dressed_more_slowly=True,
                not_safe_to_be_physically_active=True,
                worrying_thoughts_a_lot=True,
                pain_is_terrible_never_better=True,
                not_enjoying_usual_things=True,
                bothersomeness="extremely",
            )
        )
        assert total == 9
        assert psych == 5


class TestRiskBands:
    def test_total_zero_is_low_risk(self) -> None:
        result = start_back_stratification(_responses())
        assert result.risk_band == "low"

    def test_total_three_is_low_risk(self) -> None:
        result = start_back_stratification(
            _responses(
                leg_pain_in_last_2_weeks=True,
                shoulder_or_neck_pain_in_last_2_weeks=True,
                walked_only_short_distances=True,
            )
        )
        assert result.total_score == 3
        assert result.risk_band == "low"

    def test_total_four_with_low_psychosocial_is_medium_risk(self) -> None:
        result = start_back_stratification(
            _responses(
                leg_pain_in_last_2_weeks=True,
                shoulder_or_neck_pain_in_last_2_weeks=True,
                walked_only_short_distances=True,
                dressed_more_slowly=True,
            )
        )
        assert result.total_score == 4
        assert result.psychosocial_subscale_score == 0
        assert result.risk_band == "medium"

    def test_total_four_with_psychosocial_three_is_medium_risk(self) -> None:
        result = start_back_stratification(
            _responses(
                leg_pain_in_last_2_weeks=True,
                not_safe_to_be_physically_active=True,
                worrying_thoughts_a_lot=True,
                pain_is_terrible_never_better=True,
            )
        )
        assert result.total_score == 4
        assert result.psychosocial_subscale_score == 3
        assert result.risk_band == "medium"

    def test_total_four_with_psychosocial_four_is_high_risk(self) -> None:
        result = start_back_stratification(
            _responses(
                not_safe_to_be_physically_active=True,
                worrying_thoughts_a_lot=True,
                pain_is_terrible_never_better=True,
                not_enjoying_usual_things=True,
            )
        )
        assert result.total_score == 4
        assert result.psychosocial_subscale_score == 4
        assert result.risk_band == "high"

    def test_maximum_score_is_high_risk(self) -> None:
        result = start_back_stratification(
            _responses(
                leg_pain_in_last_2_weeks=True,
                shoulder_or_neck_pain_in_last_2_weeks=True,
                walked_only_short_distances=True,
                dressed_more_slowly=True,
                not_safe_to_be_physically_active=True,
                worrying_thoughts_a_lot=True,
                pain_is_terrible_never_better=True,
                not_enjoying_usual_things=True,
                bothersomeness="extremely",
            )
        )
        assert result.total_score == 9
        assert result.psychosocial_subscale_score == 5
        assert result.risk_band == "high"


class TestManagementRecommendations:
    def test_low_risk_recommends_education_and_reassurance(self) -> None:
        result = start_back_stratification(_responses())
        assert "Education" in result.recommended_management

    def test_medium_risk_recommends_standardized_physiotherapy(self) -> None:
        result = start_back_stratification(
            _responses(
                leg_pain_in_last_2_weeks=True,
                shoulder_or_neck_pain_in_last_2_weeks=True,
                walked_only_short_distances=True,
                dressed_more_slowly=True,
            )
        )
        assert "Standardized physiotherapy" in result.recommended_management

    def test_high_risk_recommends_combined_physical_and_psychological(self) -> None:
        result = start_back_stratification(
            _responses(
                not_safe_to_be_physically_active=True,
                worrying_thoughts_a_lot=True,
                pain_is_terrible_never_better=True,
                not_enjoying_usual_things=True,
            )
        )
        assert "psychologically informed" in result.recommended_management


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = start_back_stratification(_responses())
        assert "Hill 2008" in result.citations
        assert "Hill 2011" in result.citations

    def test_rationale_is_non_empty(self) -> None:
        result = start_back_stratification(_responses())
        assert result.rationale.strip() != ""
