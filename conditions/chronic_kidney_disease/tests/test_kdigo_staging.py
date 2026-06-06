"""Tests for KDIGO CKD staging (GFR and albuminuria heat map)."""

from __future__ import annotations

import pytest

from conditions.chronic_kidney_disease.kdigo_staging import (
    KdigoFeatures,
    kdigo_albuminuria_category,
    kdigo_assessment,
    kdigo_gfr_category,
    kdigo_risk_band,
)


def _features(
    egfr: float = 100.0,
    acr: float = 1.0,
    persistent: bool = True,
) -> KdigoFeatures:
    return KdigoFeatures(
        egfr_ml_min_1_73m2=egfr,
        acr_mg_per_mmol=acr,
        persistent_over_3_months=persistent,
    )


class TestGfrCategoryBoundaries:
    @pytest.mark.parametrize(
        "egfr, expected",
        [
            (120.0, "G1"),
            (90.0, "G1"),
            (89.0, "G2"),
            (60.0, "G2"),
            (59.0, "G3a"),
            (45.0, "G3a"),
            (44.0, "G3b"),
            (30.0, "G3b"),
            (29.0, "G4"),
            (15.0, "G4"),
            (14.0, "G5"),
            (5.0, "G5"),
        ],
    )
    def test_gfr_category(self, egfr: float, expected: str) -> None:
        assert kdigo_gfr_category(egfr) == expected


class TestAlbuminuriaCategoryBoundaries:
    @pytest.mark.parametrize(
        "acr, expected",
        [
            (0.0, "A1"),
            (2.9, "A1"),
            (3.0, "A2"),
            (15.0, "A2"),
            (30.0, "A2"),
            (30.1, "A3"),
            (100.0, "A3"),
        ],
    )
    def test_albuminuria_category(self, acr: float, expected: str) -> None:
        assert kdigo_albuminuria_category(acr) == expected


class TestRiskHeatMap:
    @pytest.mark.parametrize(
        "gfr, alb, expected",
        [
            ("G1", "A1", "low"),
            ("G1", "A2", "moderately_increased"),
            ("G1", "A3", "high"),
            ("G2", "A1", "low"),
            ("G2", "A2", "moderately_increased"),
            ("G2", "A3", "high"),
            ("G3a", "A1", "moderately_increased"),
            ("G3a", "A2", "high"),
            ("G3a", "A3", "very_high"),
            ("G3b", "A1", "high"),
            ("G3b", "A2", "very_high"),
            ("G3b", "A3", "very_high"),
            ("G4", "A1", "very_high"),
            ("G4", "A2", "very_high"),
            ("G4", "A3", "very_high"),
            ("G5", "A1", "very_high"),
            ("G5", "A2", "very_high"),
            ("G5", "A3", "very_high"),
        ],
    )
    def test_all_eighteen_cells(self, gfr: str, alb: str, expected: str) -> None:
        assert kdigo_risk_band(gfr, alb) == expected  # type: ignore[arg-type]


class TestAssessment:
    def test_stage_label_and_color(self) -> None:
        # eGFR 35 -> G3b, ACR 10 -> A2 -> very_high (red).
        result = kdigo_assessment(_features(egfr=35.0, acr=10.0))
        assert result.gfr_category == "G3b"
        assert result.albuminuria_category == "A2"
        assert result.stage_label == "G3bA2"
        assert result.risk_band == "very_high"
        assert result.risk_color == "red"

    def test_low_risk_green(self) -> None:
        result = kdigo_assessment(_features(egfr=100.0, acr=1.0))
        assert result.stage_label == "G1A1"
        assert result.risk_band == "low"
        assert result.risk_color == "green"

    def test_referral_indicated_for_g4(self) -> None:
        result = kdigo_assessment(_features(egfr=20.0, acr=1.0))
        assert result.gfr_category == "G4"
        assert result.nephrology_referral_indicated is True

    def test_referral_indicated_for_a3(self) -> None:
        result = kdigo_assessment(_features(egfr=100.0, acr=50.0))
        assert result.albuminuria_category == "A3"
        assert result.nephrology_referral_indicated is True

    def test_referral_not_indicated_for_g2a1(self) -> None:
        result = kdigo_assessment(_features(egfr=70.0, acr=1.0))
        assert result.nephrology_referral_indicated is False

    def test_monitoring_scales_with_risk(self) -> None:
        high = kdigo_assessment(_features(egfr=35.0, acr=1.0))  # G3b A1 -> high
        assert "twice" in high.recommended_monitoring


class TestChronicity:
    def test_persistent_flag_echoed_true(self) -> None:
        result = kdigo_assessment(_features(persistent=True))
        assert result.meets_ckd_chronicity_criterion is True
        assert "chronicity is not yet established" not in result.recommended_disposition

    def test_not_persistent_flagged_in_disposition(self) -> None:
        result = kdigo_assessment(_features(egfr=35.0, acr=10.0, persistent=False))
        assert result.meets_ckd_chronicity_criterion is False
        assert "chronicity is not yet established" in result.recommended_disposition

    def test_categories_still_computed_when_not_persistent(self) -> None:
        # Staging categories are reported regardless; only the CKD label is gated.
        result = kdigo_assessment(_features(egfr=50.0, acr=5.0, persistent=False))
        assert result.gfr_category == "G3a"
        assert result.albuminuria_category == "A2"


class TestOutputShape:
    def test_citations_present(self) -> None:
        result = kdigo_assessment(_features())
        assert "KDIGO 2024" in result.citations

    def test_caveats_mention_three_months(self) -> None:
        result = kdigo_assessment(_features())
        assert any("three months" in c for c in result.population_caveats)

    def test_caveats_mention_g1_g2_marker_requirement(self) -> None:
        result = kdigo_assessment(_features())
        assert any("marker of kidney damage" in c for c in result.population_caveats)


class TestValidation:
    def test_negative_egfr_raises(self) -> None:
        with pytest.raises(ValueError):
            kdigo_assessment(_features(egfr=-1.0))

    def test_negative_acr_raises(self) -> None:
        with pytest.raises(ValueError):
            kdigo_assessment(_features(acr=-1.0))

    def test_negative_egfr_category_raises(self) -> None:
        with pytest.raises(ValueError):
            kdigo_gfr_category(-5.0)
