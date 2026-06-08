"""Tests for the Westley Croup Score."""

from __future__ import annotations

from conditions.croup.westley import WestleyFeatures, westley_assessment, westley_score

_D = {"level_of_consciousness": "normal", "cyanosis": "none", "stridor": "none",
      "air_entry": "normal", "retractions": "none"}


def _f(**o: str) -> WestleyFeatures:
    return WestleyFeatures(**(_D | o))


class TestItems:
    def test_all_zero(self) -> None:
        assert westley_score(_f()) == 0

    def test_disoriented_5(self) -> None:
        assert westley_score(_f(level_of_consciousness="disoriented")) == 5

    def test_cyanosis_agitation_4_rest_5(self) -> None:
        assert westley_score(_f(cyanosis="with_agitation")) == 4
        assert westley_score(_f(cyanosis="at_rest")) == 5

    def test_stridor_1_2(self) -> None:
        assert westley_score(_f(stridor="with_agitation")) == 1
        assert westley_score(_f(stridor="at_rest")) == 2

    def test_air_entry_1_2(self) -> None:
        assert westley_score(_f(air_entry="decreased")) == 1
        assert westley_score(_f(air_entry="markedly_decreased")) == 2

    def test_retractions_1_2_3(self) -> None:
        assert westley_score(_f(retractions="mild")) == 1
        assert westley_score(_f(retractions="moderate")) == 2
        assert westley_score(_f(retractions="severe")) == 3

    def test_max_17(self) -> None:
        assert westley_score(_f(level_of_consciousness="disoriented", cyanosis="at_rest",
                                stridor="at_rest", air_entry="markedly_decreased",
                                retractions="severe")) == 17


class TestBands:
    def test_mild_0_and_2(self) -> None:
        assert westley_assessment(_f()).severity_band == "mild"
        assert westley_assessment(_f(air_entry="markedly_decreased")).severity_band == "mild"  # 2

    def test_moderate_3_and_5(self) -> None:
        assert westley_assessment(_f(retractions="severe")).severity_band == "moderate"  # 3
        assert westley_assessment(_f(cyanosis="with_agitation", retractions="mild")).severity_band == "moderate"  # 5

    def test_severe_6_and_11(self) -> None:
        assert westley_assessment(_f(cyanosis="at_rest", retractions="mild")).severity_band == "severe"  # 6
        assert westley_assessment(_f(cyanosis="at_rest", stridor="at_rest", air_entry="markedly_decreased",
                                     retractions="moderate")).severity_band == "severe"  # 11

    def test_impending_12_and_17(self) -> None:
        # 5 (disoriented) + 5 (cyanosis at rest) + 2 = 12
        assert westley_assessment(_f(level_of_consciousness="disoriented", cyanosis="at_rest",
                                     stridor="at_rest")).severity_band == "impending_respiratory_failure"


class TestOutput:
    def test_citations(self) -> None:
        assert "Westley 1978" in westley_assessment(_f()).citations

    def test_severe_action_mentions_epinephrine(self) -> None:
        r = westley_assessment(_f(cyanosis="at_rest", retractions="mild"))
        assert "epinephrine" in r.recommended_action.lower()

    def test_caveats_present(self) -> None:
        assert westley_assessment(_f()).population_caveats
