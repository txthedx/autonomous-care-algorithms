"""Tests for the GLP-1 receptor agonist eligibility screen."""

from __future__ import annotations

from conditions.glp1_safety.glp1_safety import (
    Glp1EligibilityFeatures,
    glp1_eligibility,
)

_DEFAULT: dict[str, bool] = {
    "personal_or_family_history_mtc": False,
    "men2_syndrome": False,
    "pregnancy": False,
    "breastfeeding": False,
    "history_of_pancreatitis": False,
}

_CONTRAINDICATIONS = ["personal_or_family_history_mtc", "men2_syndrome", "pregnancy"]
_REVIEWS = ["history_of_pancreatitis", "breastfeeding"]


def _features(**overrides: bool) -> Glp1EligibilityFeatures:
    return Glp1EligibilityFeatures(**(_DEFAULT | overrides))


class TestEligible:
    def test_no_factors_is_eligible(self) -> None:
        result = glp1_eligibility(_features())
        assert result.verdict == "eligible"
        assert result.contraindicated is False
        assert result.needs_clinician_review is False
        assert result.contraindication_factors == ()
        assert result.review_factors == ()


class TestContraindications:
    def test_each_contraindication(self) -> None:
        for field in _CONTRAINDICATIONS:
            result = glp1_eligibility(_features(**{field: True}))
            assert result.verdict == "contraindicated", field
            assert result.contraindicated is True, field
            assert len(result.contraindication_factors) == 1, field

    def test_mtc_action_mentions_boxed_warning(self) -> None:
        result = glp1_eligibility(_features(personal_or_family_history_mtc=True))
        assert "boxed warning" in result.recommended_action.lower()


class TestReviewFactors:
    def test_each_review_factor(self) -> None:
        for field in _REVIEWS:
            result = glp1_eligibility(_features(**{field: True}))
            assert result.verdict == "needs_clinician_review", field
            assert result.needs_clinician_review is True, field
            assert result.contraindicated is False, field
            assert len(result.review_factors) == 1, field


class TestPrecedence:
    def test_contraindication_takes_precedence_over_review(self) -> None:
        result = glp1_eligibility(
            _features(men2_syndrome=True, history_of_pancreatitis=True)
        )
        assert result.verdict == "contraindicated"
        assert result.contraindicated is True
        assert result.needs_clinician_review is False
        # the review factor is still reported alongside
        assert "history of pancreatitis" in result.review_factors

    def test_multiple_contraindications_listed(self) -> None:
        result = glp1_eligibility(
            _features(personal_or_family_history_mtc=True, pregnancy=True)
        )
        assert len(result.contraindication_factors) == 2


class TestOutputShape:
    def test_citation_present(self) -> None:
        result = glp1_eligibility(_features())
        assert "GLP-1 label" in result.citations

    def test_caveats_mention_class_warning_and_pregnancy(self) -> None:
        text = " ".join(glp1_eligibility(_features()).population_caveats).lower()
        assert "boxed warning" in text
        assert "pregnancy" in text

    def test_rationale_non_empty(self) -> None:
        assert glp1_eligibility(_features()).rationale.strip() != ""
