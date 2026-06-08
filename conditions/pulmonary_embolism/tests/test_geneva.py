"""Tests for the revised Geneva score."""

from __future__ import annotations

import pytest

from conditions.pulmonary_embolism.geneva import GenevaFeatures, geneva_assessment, geneva_score

_D = {
    "age_years": 40, "previous_dvt_or_pe": False,
    "surgery_or_lower_limb_fracture_within_1_month": False,
    "active_malignancy": False, "unilateral_lower_limb_pain": False,
    "hemoptysis": False, "heart_rate_per_minute": 70,
    "pain_on_deep_venous_palpation_and_unilateral_edema": False,
}


def _f(**o: object) -> GenevaFeatures:
    return GenevaFeatures(**(_D | o))  # type: ignore[arg-type]


def _s(**o: object) -> int:
    return geneva_score(_f(**o))


class TestItems:
    def test_zero(self) -> None:
        assert _s() == 0

    def test_age_over_65(self) -> None:
        assert _s(age_years=66) == 1
        assert _s(age_years=65) == 0

    def test_prior_dvt_pe_3(self) -> None:
        assert _s(previous_dvt_or_pe=True) == 3

    def test_surgery_fracture_2(self) -> None:
        assert _s(surgery_or_lower_limb_fracture_within_1_month=True) == 2

    def test_malignancy_2(self) -> None:
        assert _s(active_malignancy=True) == 2

    def test_unilateral_pain_3(self) -> None:
        assert _s(unilateral_lower_limb_pain=True) == 3

    def test_hemoptysis_2(self) -> None:
        assert _s(hemoptysis=True) == 2

    def test_hr_bands(self) -> None:
        assert _s(heart_rate_per_minute=74) == 0
        assert _s(heart_rate_per_minute=75) == 3
        assert _s(heart_rate_per_minute=94) == 3
        assert _s(heart_rate_per_minute=95) == 5

    def test_palpation_edema_4(self) -> None:
        assert _s(pain_on_deep_venous_palpation_and_unilateral_edema=True) == 4

    def test_max_22(self) -> None:
        assert _s(age_years=70, previous_dvt_or_pe=True,
                  surgery_or_lower_limb_fracture_within_1_month=True, active_malignancy=True,
                  unilateral_lower_limb_pain=True, hemoptysis=True, heart_rate_per_minute=100,
                  pain_on_deep_venous_palpation_and_unilateral_edema=True) == 22


class TestBands:
    def test_low_3(self) -> None:
        r = geneva_assessment(_f(previous_dvt_or_pe=True))  # 3
        assert r.score == 3 and r.risk_band == "low"

    def test_intermediate_4_and_10(self) -> None:
        assert geneva_assessment(_f(active_malignancy=True, hemoptysis=True)).risk_band == "intermediate"  # 4
        assert geneva_assessment(_f(previous_dvt_or_pe=True, unilateral_lower_limb_pain=True,
                                    heart_rate_per_minute=80)).risk_band == "intermediate"  # 9

    def test_high_11(self) -> None:
        r = geneva_assessment(_f(unilateral_lower_limb_pain=True, heart_rate_per_minute=95,
                                 pain_on_deep_venous_palpation_and_unilateral_edema=True))  # 12
        assert r.risk_band == "high"


class TestOutput:
    def test_citations(self) -> None:
        assert "Le Gal 2006" in geneva_assessment(_f()).citations

    def test_prevalence(self) -> None:
        assert "Le Gal 2006" in geneva_assessment(_f()).estimated_pe_prevalence_band

    def test_negative_hr_raises(self) -> None:
        with pytest.raises(ValueError):
            geneva_score(_f(heart_rate_per_minute=-1))
