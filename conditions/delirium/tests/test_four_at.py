"""Tests for the 4AT delirium screening instrument."""

from __future__ import annotations

from conditions.delirium.four_at import (
    FourATFeatures,
    four_at_assessment,
    four_at_component_scores,
    four_at_score,
)

# Baseline with all items at their zero-point level. Each test overrides.
_DEFAULT: dict[str, object] = {
    "alertness": "normal",
    "amt4": "no_mistakes",
    "attention_months_backwards": "seven_or_more_correct",
    "acute_change_or_fluctuating_course": False,
}


def _features(**overrides: object) -> FourATFeatures:
    return FourATFeatures(**(_DEFAULT | overrides))  # type: ignore[arg-type]


def _score(**overrides: object) -> int:
    return four_at_score(_features(**overrides))


class TestAlertnessItem:
    def test_normal_is_zero(self) -> None:
        assert four_at_component_scores(_features()).alertness == 0

    def test_altered_is_four(self) -> None:
        assert four_at_component_scores(_features(alertness="altered")).alertness == 4


class TestAmt4Item:
    def test_no_mistakes_is_zero(self) -> None:
        assert four_at_component_scores(_features()).amt4 == 0

    def test_one_mistake_is_one(self) -> None:
        assert four_at_component_scores(_features(amt4="one_mistake")).amt4 == 1

    def test_two_or_more_is_two(self) -> None:
        result = four_at_component_scores(
            _features(amt4="two_or_more_mistakes_or_untestable")
        )
        assert result.amt4 == 2


class TestAttentionItem:
    def test_seven_or_more_is_zero(self) -> None:
        assert four_at_component_scores(_features()).attention == 0

    def test_fewer_than_seven_is_one(self) -> None:
        result = four_at_component_scores(
            _features(attention_months_backwards="fewer_than_seven_or_refuses")
        )
        assert result.attention == 1

    def test_untestable_is_two(self) -> None:
        result = four_at_component_scores(
            _features(attention_months_backwards="untestable")
        )
        assert result.attention == 2


class TestAcuteChangeItem:
    def test_absent_is_zero(self) -> None:
        assert four_at_component_scores(_features()).acute_change == 0

    def test_present_is_four(self) -> None:
        result = four_at_component_scores(
            _features(acute_change_or_fluctuating_course=True)
        )
        assert result.acute_change == 4


class TestTotalScore:
    def test_all_zero_is_zero(self) -> None:
        assert _score() == 0

    def test_maximum_is_twelve(self) -> None:
        result = _score(
            alertness="altered",
            amt4="two_or_more_mistakes_or_untestable",
            attention_months_backwards="untestable",
            acute_change_or_fluctuating_course=True,
        )
        assert result == 12

    def test_components_sum_to_total(self) -> None:
        features = _features(
            amt4="one_mistake",
            attention_months_backwards="untestable",
            acute_change_or_fluctuating_course=True,
        )
        c = four_at_component_scores(features)
        assert c.alertness + c.amt4 + c.attention + c.acute_change == four_at_score(features)
        # 0 + 1 + 2 + 4 = 7
        assert four_at_score(features) == 7


class TestInterpretationBands:
    def test_zero_is_unlikely(self) -> None:
        result = four_at_assessment(_features())
        assert result.score == 0
        assert result.interpretation_band == "unlikely"

    def test_one_is_possible_cognitive_impairment(self) -> None:
        result = four_at_assessment(_features(amt4="one_mistake"))
        assert result.score == 1
        assert result.interpretation_band == "possible_cognitive_impairment"

    def test_three_is_possible_cognitive_impairment(self) -> None:
        # amt4 2 + attention 1 = 3
        result = four_at_assessment(
            _features(
                amt4="two_or_more_mistakes_or_untestable",
                attention_months_backwards="fewer_than_seven_or_refuses",
            )
        )
        assert result.score == 3
        assert result.interpretation_band == "possible_cognitive_impairment"

    def test_four_from_acute_change_alone_is_possible_delirium(self) -> None:
        result = four_at_assessment(_features(acute_change_or_fluctuating_course=True))
        assert result.score == 4
        assert result.interpretation_band == "possible_delirium"

    def test_four_from_alertness_alone_is_possible_delirium(self) -> None:
        result = four_at_assessment(_features(alertness="altered"))
        assert result.score == 4
        assert result.interpretation_band == "possible_delirium"

    def test_twelve_is_possible_delirium(self) -> None:
        result = four_at_assessment(
            _features(
                alertness="altered",
                amt4="two_or_more_mistakes_or_untestable",
                attention_months_backwards="untestable",
                acute_change_or_fluctuating_course=True,
            )
        )
        assert result.interpretation_band == "possible_delirium"


class TestDispositionAndCaveats:
    def test_unlikely_mentions_rescreen(self) -> None:
        result = four_at_assessment(_features())
        assert "re-screen" in result.recommended_action.lower()

    def test_cognitive_impairment_mentions_cognitive_assessment(self) -> None:
        result = four_at_assessment(_features(amt4="one_mistake"))
        assert "cognitive" in result.recommended_action.lower()

    def test_delirium_mentions_full_assessment(self) -> None:
        result = four_at_assessment(_features(acute_change_or_fluctuating_course=True))
        assert "full clinical assessment" in result.recommended_action.lower()

    def test_caveats_state_screen_not_diagnosis(self) -> None:
        result = four_at_assessment(_features())
        assert any("screening tool, not a diagnostic test" in c
                   for c in result.population_caveats)

    def test_caveats_mention_dementia_distinction(self) -> None:
        result = four_at_assessment(_features())
        assert any("dementia" in c for c in result.population_caveats)


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = four_at_assessment(_features())
        assert "Bellelli 2014" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = four_at_assessment(_features())
        assert result.rationale.strip() != ""

    def test_components_echoed(self) -> None:
        result = four_at_assessment(
            _features(amt4="one_mistake", acute_change_or_fluctuating_course=True)
        )
        assert result.components.amt4 == 1
        assert result.components.acute_change == 4
