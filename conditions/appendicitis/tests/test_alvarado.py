"""Tests for the Alvarado score and its interpretation."""

from __future__ import annotations

import pytest

from conditions.appendicitis.alvarado import (
    AlvaradoFeatures,
    alvarado_assessment,
    alvarado_components,
    alvarado_score,
)

# Baseline of all-zero-point inputs (score 0). Each test overrides what it needs.
_DEFAULT: dict[str, object] = {
    "migration_of_pain_to_rlq": False,
    "anorexia": False,
    "nausea_or_vomiting": False,
    "tenderness_in_rlq": False,
    "rebound_tenderness": False,
    "temperature_celsius": 37.0,            # < 37.3 -> 0
    "white_cell_count_x10e9_per_l": 8.0,    # <= 10 -> 0
    "neutrophil_percent": 60.0,             # <= 75 -> 0
}


def _features(**overrides: object) -> AlvaradoFeatures:
    return AlvaradoFeatures(**(_DEFAULT | overrides))  # type: ignore[arg-type]


def _score(**overrides: object) -> int:
    return alvarado_score(_features(**overrides))


class TestComponentWeights:
    def test_all_zero_is_zero(self) -> None:
        assert _score() == 0

    def test_migration_adds_one(self) -> None:
        assert _score(migration_of_pain_to_rlq=True) == 1

    def test_anorexia_adds_one(self) -> None:
        assert _score(anorexia=True) == 1

    def test_nausea_or_vomiting_adds_one(self) -> None:
        assert _score(nausea_or_vomiting=True) == 1

    def test_tenderness_adds_two(self) -> None:
        assert _score(tenderness_in_rlq=True) == 2

    def test_rebound_adds_one(self) -> None:
        assert _score(rebound_tenderness=True) == 1

    def test_elevated_temperature_adds_one(self) -> None:
        assert _score(temperature_celsius=38.0) == 1

    def test_leukocytosis_adds_two(self) -> None:
        assert _score(white_cell_count_x10e9_per_l=15.0) == 2

    def test_left_shift_adds_one(self) -> None:
        assert _score(neutrophil_percent=85.0) == 1

    def test_maximum_score_is_ten(self) -> None:
        result = _score(
            migration_of_pain_to_rlq=True,
            anorexia=True,
            nausea_or_vomiting=True,
            tenderness_in_rlq=True,
            rebound_tenderness=True,
            temperature_celsius=38.5,
            white_cell_count_x10e9_per_l=16.0,
            neutrophil_percent=88.0,
        )
        assert result == 10


class TestTemperatureThreshold:
    def test_below_37_3_is_zero(self) -> None:
        assert _score(temperature_celsius=37.2) == 0

    def test_exactly_37_3_is_one(self) -> None:
        assert _score(temperature_celsius=37.3) == 1

    def test_above_37_3_is_one(self) -> None:
        assert _score(temperature_celsius=39.0) == 1


class TestLeukocytosisThreshold:
    def test_exactly_10_is_zero(self) -> None:
        # Threshold is "above 10", so 10.0 does not score.
        assert _score(white_cell_count_x10e9_per_l=10.0) == 0

    def test_just_above_10_is_two(self) -> None:
        assert _score(white_cell_count_x10e9_per_l=10.1) == 2


class TestLeftShiftThreshold:
    def test_exactly_75_is_zero(self) -> None:
        # Threshold is "above 75%", so 75.0 does not score.
        assert _score(neutrophil_percent=75.0) == 0

    def test_just_above_75_is_one(self) -> None:
        assert _score(neutrophil_percent=75.1) == 1


class TestBands:
    def test_score_zero_is_low(self) -> None:
        result = alvarado_assessment(_features())
        assert result.score == 0
        assert result.risk_band == "low"

    def test_score_four_is_low(self) -> None:
        # tenderness (2) + migration (1) + anorexia (1) = 4
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                migration_of_pain_to_rlq=True,
                anorexia=True,
            )
        )
        assert result.score == 4
        assert result.risk_band == "low"

    def test_score_five_is_moderate(self) -> None:
        # tenderness (2) + migration (1) + anorexia (1) + nausea (1) = 5
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                migration_of_pain_to_rlq=True,
                anorexia=True,
                nausea_or_vomiting=True,
            )
        )
        assert result.score == 5
        assert result.risk_band == "moderate"

    def test_score_six_is_moderate(self) -> None:
        # tenderness (2) + leukocytosis (2) + migration (1) + anorexia (1) = 6
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                white_cell_count_x10e9_per_l=12.0,
                migration_of_pain_to_rlq=True,
                anorexia=True,
            )
        )
        assert result.score == 6
        assert result.risk_band == "moderate"

    def test_score_seven_is_high(self) -> None:
        # tenderness (2) + leukocytosis (2) + migration (1) + anorexia (1) + nausea (1) = 7
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                white_cell_count_x10e9_per_l=12.0,
                migration_of_pain_to_rlq=True,
                anorexia=True,
                nausea_or_vomiting=True,
            )
        )
        assert result.score == 7
        assert result.risk_band == "high"


class TestDispositionAndCaveats:
    def test_low_mentions_alternative_diagnoses(self) -> None:
        result = alvarado_assessment(_features())
        assert "alternative" in result.recommended_disposition.lower()

    def test_moderate_mentions_imaging(self) -> None:
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                migration_of_pain_to_rlq=True,
                anorexia=True,
                nausea_or_vomiting=True,
            )
        )
        assert "imaging" in result.recommended_disposition.lower()

    def test_high_mentions_surgical(self) -> None:
        result = alvarado_assessment(
            _features(
                tenderness_in_rlq=True,
                white_cell_count_x10e9_per_l=12.0,
                migration_of_pain_to_rlq=True,
                anorexia=True,
                nausea_or_vomiting=True,
            )
        )
        assert "surgical" in result.recommended_disposition.lower()

    def test_caveats_mention_pediatric(self) -> None:
        result = alvarado_assessment(_features())
        assert any("children" in c.lower() or "pediatric" in c.lower()
                   for c in result.population_caveats)

    def test_caveats_mention_units(self) -> None:
        result = alvarado_assessment(_features())
        assert any("Celsius" in c and "10^9/L" in c for c in result.population_caveats)


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = alvarado_assessment(_features())
        assert "Alvarado 1986" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = alvarado_assessment(_features())
        assert result.rationale.strip() != ""

    def test_contributing_factors_empty_at_zero(self) -> None:
        result = alvarado_assessment(_features())
        assert result.contributing_factors == ()

    def test_contributing_factors_listed(self) -> None:
        factors = alvarado_components(
            _features(tenderness_in_rlq=True, white_cell_count_x10e9_per_l=14.0)
        )
        assert len(factors) == 2
        assert any("tenderness" in f for f in factors)
        assert any("leukocytosis" in f for f in factors)


class TestValidation:
    def test_negative_temperature_raises(self) -> None:
        with pytest.raises(ValueError):
            alvarado_score(_features(temperature_celsius=-1.0))

    def test_negative_wcc_raises(self) -> None:
        with pytest.raises(ValueError):
            alvarado_score(_features(white_cell_count_x10e9_per_l=-1.0))

    def test_neutrophil_percent_over_100_raises(self) -> None:
        with pytest.raises(ValueError):
            alvarado_assessment(_features(neutrophil_percent=101.0))

    def test_negative_neutrophil_percent_raises(self) -> None:
        with pytest.raises(ValueError):
            alvarado_score(_features(neutrophil_percent=-1.0))
