"""Tests for the finasteride safety screens."""

from __future__ import annotations

from conditions.finasteride_safety.finasteride_safety import (
    FinasterideContraindicationFeatures,
    FinasteridePsychiatricFeatures,
    finasteride_contraindication,
    finasteride_psychiatric_screen,
)


def _psych(
    *, active: bool = False, depression: bool = False
) -> FinasteridePsychiatricFeatures:
    return FinasteridePsychiatricFeatures(
        active_suicidal_ideation_or_self_harm=active,
        current_or_past_depression=depression,
    )


class TestContraindication:
    def test_pregnant_or_reproductive_potential_is_contraindicated(self) -> None:
        result = finasteride_contraindication(
            FinasterideContraindicationFeatures(
                pregnant_or_able_to_become_pregnant=True
            )
        )
        assert result.verdict == "absolute_contraindication"
        assert result.contraindicated is True
        assert "teratogenic" in result.recommended_action.lower()

    def test_not_pregnant_no_contraindication(self) -> None:
        result = finasteride_contraindication(
            FinasterideContraindicationFeatures(
                pregnant_or_able_to_become_pregnant=False
            )
        )
        assert result.verdict == "no_contraindication_detected"
        assert result.contraindicated is False

    def test_citation_and_caveats(self) -> None:
        result = finasteride_contraindication(
            FinasterideContraindicationFeatures(
                pregnant_or_able_to_become_pregnant=False
            )
        )
        assert "Propecia label" in result.citations
        text = " ".join(result.population_caveats).lower()
        assert "crushed or broken" in text
        assert "gender identity" in text


class TestPsychiatricScreen:
    def test_active_si_blocks_initiation(self) -> None:
        result = finasteride_psychiatric_screen(_psych(active=True))
        assert result.verdict == "active_risk_do_not_initiate"
        assert result.block_initiation is True
        assert "crisis" in result.recommended_action.lower()

    def test_active_si_takes_precedence_over_depression(self) -> None:
        result = finasteride_psychiatric_screen(
            _psych(active=True, depression=True)
        )
        assert result.verdict == "active_risk_do_not_initiate"
        assert result.block_initiation is True
        assert result.positive_findings == (
            "active suicidal ideation or self-harm",
        )

    def test_depression_history_routes_to_review(self) -> None:
        result = finasteride_psychiatric_screen(_psych(depression=True))
        assert result.verdict == "history_clinician_review"
        assert result.block_initiation is False
        assert "review" in result.recommended_action.lower()

    def test_negative_screen(self) -> None:
        result = finasteride_psychiatric_screen(_psych())
        assert result.verdict == "screen_negative"
        assert result.block_initiation is False
        assert result.positive_findings == ()

    def test_negative_screen_still_counsels(self) -> None:
        result = finasteride_psychiatric_screen(_psych())
        assert "counsel" in result.recommended_action.lower()

    def test_citation_and_caveats(self) -> None:
        result = finasteride_psychiatric_screen(_psych())
        assert "Health Canada 2024" in result.citations
        text = " ".join(result.population_caveats).lower()
        assert "january 2024" in text
        assert "not a validated" in text
