"""Tests for the Glasgow-Blatchford score and its interpretation."""

from __future__ import annotations

import pytest

from conditions.upper_gi_bleeding.glasgow_blatchford import (
    GlasgowBlatchfordFeatures,
    glasgow_blatchford_assessment,
    glasgow_blatchford_components,
    glasgow_blatchford_score,
)

# Baseline of all-zero-point inputs (score 0). Each test overrides what it needs.
_DEFAULT: dict[str, object] = {
    "sex": "male",
    "urea_mmol_per_l": 5.0,          # < 6.5 -> 0
    "hemoglobin_g_per_l": 150.0,     # male >= 130 -> 0
    "systolic_bp_mmhg": 120,         # >= 110 -> 0
    "pulse_per_minute": 80,          # < 100 -> 0
    "melena": False,
    "syncope": False,
    "hepatic_disease": False,
    "cardiac_failure": False,
}


def _features(**overrides: object) -> GlasgowBlatchfordFeatures:
    return GlasgowBlatchfordFeatures(**(_DEFAULT | overrides))  # type: ignore[arg-type]


def _score(**overrides: object) -> int:
    return glasgow_blatchford_score(_features(**overrides))


class TestUreaBands:
    def test_below_6_5_is_zero(self) -> None:
        assert _score(urea_mmol_per_l=6.49) == 0

    def test_6_5_is_two(self) -> None:
        assert _score(urea_mmol_per_l=6.5) == 2

    def test_7_9_is_two(self) -> None:
        assert _score(urea_mmol_per_l=7.9) == 2

    def test_8_0_is_three(self) -> None:
        assert _score(urea_mmol_per_l=8.0) == 3

    def test_9_9_is_three(self) -> None:
        assert _score(urea_mmol_per_l=9.9) == 3

    def test_10_0_is_four(self) -> None:
        assert _score(urea_mmol_per_l=10.0) == 4

    def test_24_9_is_four(self) -> None:
        assert _score(urea_mmol_per_l=24.9) == 4

    def test_25_0_is_six(self) -> None:
        assert _score(urea_mmol_per_l=25.0) == 6

    def test_above_25_is_six(self) -> None:
        assert _score(urea_mmol_per_l=40.0) == 6


class TestHemoglobinMen:
    def test_130_is_zero(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=130.0) == 0

    def test_129_is_one(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=129.0) == 1

    def test_120_is_one(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=120.0) == 1

    def test_119_is_three(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=119.0) == 3

    def test_100_is_three(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=100.0) == 3

    def test_99_is_six(self) -> None:
        assert _score(sex="male", hemoglobin_g_per_l=99.0) == 6


class TestHemoglobinWomen:
    def test_120_is_zero(self) -> None:
        assert _score(sex="female", hemoglobin_g_per_l=120.0) == 0

    def test_119_is_one(self) -> None:
        assert _score(sex="female", hemoglobin_g_per_l=119.0) == 1

    def test_100_is_one(self) -> None:
        assert _score(sex="female", hemoglobin_g_per_l=100.0) == 1

    def test_99_is_six(self) -> None:
        assert _score(sex="female", hemoglobin_g_per_l=99.0) == 6

    def test_women_band_differs_from_men_at_110(self) -> None:
        # 110 g/L: women -> 1 point (100-119), men -> 3 points (100-119).
        # Same band here, but 125 g/L differs: women 0, men 1.
        assert _score(sex="female", hemoglobin_g_per_l=125.0) == 0
        assert _score(sex="male", hemoglobin_g_per_l=125.0) == 1


class TestSystolicBp:
    def test_110_is_zero(self) -> None:
        assert _score(systolic_bp_mmhg=110) == 0

    def test_109_is_one(self) -> None:
        assert _score(systolic_bp_mmhg=109) == 1

    def test_100_is_one(self) -> None:
        assert _score(systolic_bp_mmhg=100) == 1

    def test_99_is_two(self) -> None:
        assert _score(systolic_bp_mmhg=99) == 2

    def test_90_is_two(self) -> None:
        assert _score(systolic_bp_mmhg=90) == 2

    def test_89_is_three(self) -> None:
        assert _score(systolic_bp_mmhg=89) == 3


class TestBinaryMarkers:
    def test_pulse_99_is_zero(self) -> None:
        assert _score(pulse_per_minute=99) == 0

    def test_pulse_100_is_one(self) -> None:
        assert _score(pulse_per_minute=100) == 1

    def test_melena_is_one(self) -> None:
        assert _score(melena=True) == 1

    def test_syncope_is_two(self) -> None:
        assert _score(syncope=True) == 2

    def test_hepatic_disease_is_two(self) -> None:
        assert _score(hepatic_disease=True) == 2

    def test_cardiac_failure_is_two(self) -> None:
        assert _score(cardiac_failure=True) == 2


class TestTotals:
    def test_all_zero_is_zero(self) -> None:
        assert _score() == 0

    def test_maximum_score_is_23(self) -> None:
        result = _score(
            sex="male",
            urea_mmol_per_l=25.0,        # +6
            hemoglobin_g_per_l=99.0,     # +6
            systolic_bp_mmhg=89,         # +3
            pulse_per_minute=100,        # +1
            melena=True,                 # +1
            syncope=True,                # +2
            hepatic_disease=True,        # +2
            cardiac_failure=True,        # +2
        )
        assert result == 23

    def test_components_match_score(self) -> None:
        features = _features(
            urea_mmol_per_l=10.0,   # +4
            melena=True,            # +1
            syncope=True,           # +2
        )
        assert glasgow_blatchford_score(features) == 7
        factors = glasgow_blatchford_components(features)
        assert len(factors) == 3
        assert any("urea" in f for f in factors)
        assert any("melena" in f for f in factors)
        assert any("syncope" in f for f in factors)


class TestBands:
    def test_score_zero_is_very_low(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert result.score == 0
        assert result.risk_band == "very_low"
        assert result.outpatient_management_candidate is True

    def test_score_one_is_intermediate(self) -> None:
        result = glasgow_blatchford_assessment(_features(melena=True))
        assert result.score == 1
        assert result.risk_band == "intermediate"
        assert result.outpatient_management_candidate is False

    def test_score_five_is_intermediate(self) -> None:
        # urea 10.0 (+4) + melena (+1) = 5
        result = glasgow_blatchford_assessment(
            _features(urea_mmol_per_l=10.0, melena=True)
        )
        assert result.score == 5
        assert result.risk_band == "intermediate"

    def test_score_six_is_high(self) -> None:
        # male hemoglobin 99 (+6)
        result = glasgow_blatchford_assessment(
            _features(hemoglobin_g_per_l=99.0)
        )
        assert result.score == 6
        assert result.risk_band == "high"
        assert result.outpatient_management_candidate is False

    def test_high_score_is_high(self) -> None:
        result = glasgow_blatchford_assessment(
            _features(urea_mmol_per_l=25.0, hemoglobin_g_per_l=99.0)
        )
        assert result.score == 12
        assert result.risk_band == "high"


class TestDispositionAndCaveats:
    def test_very_low_mentions_outpatient(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert "outpatient" in result.recommended_disposition.lower()

    def test_intermediate_mentions_admission(self) -> None:
        result = glasgow_blatchford_assessment(_features(melena=True))
        assert "admission" in result.recommended_disposition.lower()

    def test_high_mentions_endoscopy(self) -> None:
        result = glasgow_blatchford_assessment(_features(hemoglobin_g_per_l=99.0))
        assert "endoscopy" in result.recommended_disposition.lower()

    def test_caveats_mention_units(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert any("mmol/L" in c and "g/L" in c for c in result.population_caveats)

    def test_caveats_mention_extended_threshold(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert any("Stanley 2017" in c for c in result.population_caveats)


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert "Blatchford 2000" in result.citations
        assert "Stanley 2017" in result.citations

    def test_rationale_non_empty(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert result.rationale.strip() != ""

    def test_contributing_factors_empty_at_zero(self) -> None:
        result = glasgow_blatchford_assessment(_features())
        assert result.contributing_factors == ()


class TestValidation:
    def test_negative_urea_raises(self) -> None:
        with pytest.raises(ValueError):
            glasgow_blatchford_score(_features(urea_mmol_per_l=-1.0))

    def test_negative_hemoglobin_raises(self) -> None:
        with pytest.raises(ValueError):
            glasgow_blatchford_score(_features(hemoglobin_g_per_l=-1.0))

    def test_negative_bp_raises(self) -> None:
        with pytest.raises(ValueError):
            glasgow_blatchford_assessment(_features(systolic_bp_mmhg=-1))

    def test_negative_pulse_raises(self) -> None:
        with pytest.raises(ValueError):
            glasgow_blatchford_score(_features(pulse_per_minute=-1))
