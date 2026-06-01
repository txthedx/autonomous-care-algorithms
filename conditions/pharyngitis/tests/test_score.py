"""Tests for the McIsaac/Centor pharyngitis score.

Each Centor criterion and each age band is exercised individually so that
changes to clinical thresholds will fail loudly without a corresponding
citation update.
"""

from __future__ import annotations

import pytest

from conditions.pharyngitis.score import (
    PharyngitisFeatures,
    mcisaac_recommendation,
    mcisaac_score,
)


def _features(
    *,
    age_years: int = 30,
    history_of_fever: bool = False,
    tonsillar_exudate: bool = False,
    tender_anterior_cervical_nodes: bool = False,
    no_cough: bool = False,
) -> PharyngitisFeatures:
    return PharyngitisFeatures(
        age_years=age_years,
        history_of_fever=history_of_fever,
        tonsillar_exudate=tonsillar_exudate,
        tender_anterior_cervical_nodes=tender_anterior_cervical_nodes,
        no_cough=no_cough,
    )


class TestCentorPoints:
    def test_no_features_adult_scores_zero(self) -> None:
        assert mcisaac_score(_features()) == 0

    def test_fever_alone_scores_one(self) -> None:
        assert mcisaac_score(_features(history_of_fever=True)) == 1

    def test_exudate_alone_scores_one(self) -> None:
        assert mcisaac_score(_features(tonsillar_exudate=True)) == 1

    def test_nodes_alone_scores_one(self) -> None:
        assert mcisaac_score(_features(tender_anterior_cervical_nodes=True)) == 1

    def test_absence_of_cough_alone_scores_one(self) -> None:
        assert mcisaac_score(_features(no_cough=True)) == 1

    def test_all_four_features_adult_scores_four(self) -> None:
        score = mcisaac_score(
            _features(
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
                no_cough=True,
            )
        )
        assert score == 4


class TestAgeAdjustment:
    @pytest.mark.parametrize("age", [3, 7, 10, 14])
    def test_children_3_to_14_get_plus_one(self, age: int) -> None:
        assert mcisaac_score(_features(age_years=age)) == 1

    @pytest.mark.parametrize("age", [15, 20, 30, 44])
    def test_adults_15_to_44_get_zero(self, age: int) -> None:
        assert mcisaac_score(_features(age_years=age)) == 0

    @pytest.mark.parametrize("age", [45, 60, 80, 100])
    def test_adults_45_or_older_get_minus_one(self, age: int) -> None:
        assert mcisaac_score(_features(age_years=age)) == -1

    @pytest.mark.parametrize("age", [0, 1, 2])
    def test_under_three_gets_zero_adjustment(self, age: int) -> None:
        assert mcisaac_score(_features(age_years=age)) == 0


class TestScoreRange:
    def test_minimum_score_is_negative_one(self) -> None:
        assert mcisaac_score(_features(age_years=60)) == -1

    def test_maximum_score_is_five(self) -> None:
        score = mcisaac_score(
            _features(
                age_years=8,
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
                no_cough=True,
            )
        )
        assert score == 5

    def test_maximum_score_in_adult_is_four(self) -> None:
        score = mcisaac_score(
            _features(
                age_years=30,
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
                no_cough=True,
            )
        )
        assert score == 4


class TestInvalidInput:
    def test_negative_age_raises(self) -> None:
        with pytest.raises(ValueError, match="age_years must be non-negative"):
            mcisaac_score(_features(age_years=-1))


class TestRecommendationBands:
    def test_score_minus_one_recommends_no_action(self) -> None:
        rec = mcisaac_recommendation(_features(age_years=60))
        assert rec.score == -1
        assert "No testing" in rec.action
        assert "No antibiotics" in rec.action

    def test_score_zero_recommends_no_action(self) -> None:
        rec = mcisaac_recommendation(_features(age_years=30))
        assert rec.score == 0
        assert "No testing" in rec.action

    def test_score_one_recommends_no_routine_testing(self) -> None:
        rec = mcisaac_recommendation(_features(age_years=30, history_of_fever=True))
        assert rec.score == 1
        assert "No routine testing" in rec.action

    def test_score_two_recommends_radt(self) -> None:
        rec = mcisaac_recommendation(
            _features(
                age_years=30,
                history_of_fever=True,
                tonsillar_exudate=True,
            )
        )
        assert rec.score == 2
        assert "RADT" in rec.action

    def test_score_three_recommends_radt(self) -> None:
        rec = mcisaac_recommendation(
            _features(
                age_years=30,
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
            )
        )
        assert rec.score == 3
        assert "RADT" in rec.action

    def test_score_four_recommends_radt_not_empirical(self) -> None:
        rec = mcisaac_recommendation(
            _features(
                age_years=30,
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
                no_cough=True,
            )
        )
        assert rec.score == 4
        assert "RADT" in rec.action
        assert "does not endorse empirical antibiotics" in rec.action

    def test_score_five_recommends_radt_not_empirical(self) -> None:
        rec = mcisaac_recommendation(
            _features(
                age_years=8,
                history_of_fever=True,
                tonsillar_exudate=True,
                tender_anterior_cervical_nodes=True,
                no_cough=True,
            )
        )
        assert rec.score == 5
        assert "RADT" in rec.action

    def test_recommendation_carries_citations(self) -> None:
        rec = mcisaac_recommendation(_features(age_years=30))
        assert len(rec.citations) >= 1
        assert all(isinstance(c, str) for c in rec.citations)


class TestClinicalVignettes:
    """Vignettes designed to exercise the algorithm at clinically meaningful points.

    These are deliberately abstract (no patient details) and only test
    score-to-action mapping. They are not derived from any real patient.
    """

    def test_young_child_with_classic_features_scores_high(self) -> None:
        features = _features(
            age_years=8,
            history_of_fever=True,
            tonsillar_exudate=True,
            tender_anterior_cervical_nodes=True,
            no_cough=True,
        )
        rec = mcisaac_recommendation(features)
        assert rec.score == 5
        assert "RADT" in rec.action

    def test_middle_aged_adult_with_only_cough_absence_scores_one(self) -> None:
        features = _features(age_years=30, no_cough=True)
        assert mcisaac_score(features) == 1

    def test_older_adult_with_two_features_scores_one(self) -> None:
        features = _features(
            age_years=60,
            history_of_fever=True,
            tonsillar_exudate=True,
        )
        assert mcisaac_score(features) == 1
