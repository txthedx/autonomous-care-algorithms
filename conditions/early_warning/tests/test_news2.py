"""Tests for NEWS2."""

from __future__ import annotations

import pytest

from conditions.early_warning.news2 import (
    NewsFeatures,
    news2_assessment,
    news2_component_scores,
    news2_score,
)

# A fully-normal patient: every parameter scores 0.
_D = {
    "respiratory_rate_per_minute": 16, "spo2_percent": 98,
    "on_supplemental_oxygen": False, "use_spo2_scale_2": False,
    "systolic_bp_mmhg": 120, "pulse_per_minute": 70,
    "consciousness": "alert", "temperature_celsius": 37.0,
}


def _f(**o: object) -> NewsFeatures:
    return NewsFeatures(**(_D | o))  # type: ignore[arg-type]


def _c(**o: object):
    return news2_component_scores(_f(**o))


class TestRespiratoryRate:
    @pytest.mark.parametrize("rr,pts", [(8, 3), (9, 1), (11, 1), (12, 0), (20, 0), (21, 2), (24, 2), (25, 3)])
    def test_rr(self, rr: int, pts: int) -> None:
        assert _c(respiratory_rate_per_minute=rr).respiratory_rate == pts


class TestSpo2Scale1:
    @pytest.mark.parametrize("s,pts", [(91, 3), (92, 2), (93, 2), (94, 1), (95, 1), (96, 0), (100, 0)])
    def test_scale1(self, s: int, pts: int) -> None:
        assert _c(spo2_percent=s).spo2 == pts


class TestSpo2Scale2:
    @pytest.mark.parametrize("s,pts", [(83, 3), (84, 2), (86, 1), (88, 0), (92, 0), (95, 0), (99, 0)])
    def test_scale2_on_air(self, s: int, pts: int) -> None:
        assert _c(use_spo2_scale_2=True, spo2_percent=s, on_supplemental_oxygen=False).spo2 == pts

    @pytest.mark.parametrize("s,pts", [(92, 0), (93, 1), (94, 1), (95, 2), (96, 2), (97, 3), (100, 3)])
    def test_scale2_on_oxygen(self, s: int, pts: int) -> None:
        assert _c(use_spo2_scale_2=True, spo2_percent=s, on_supplemental_oxygen=True).spo2 == pts


class TestOtherParameters:
    def test_supplemental_oxygen(self) -> None:
        assert _c(on_supplemental_oxygen=True).supplemental_oxygen == 2
        assert _c().supplemental_oxygen == 0

    @pytest.mark.parametrize("bp,pts", [(90, 3), (91, 2), (100, 2), (101, 1), (110, 1), (111, 0), (219, 0), (220, 3)])
    def test_sbp(self, bp: int, pts: int) -> None:
        assert _c(systolic_bp_mmhg=bp).systolic_bp == pts

    @pytest.mark.parametrize("p,pts", [(40, 3), (41, 1), (50, 1), (51, 0), (90, 0), (91, 1), (110, 1), (111, 2), (130, 2), (131, 3)])
    def test_pulse(self, p: int, pts: int) -> None:
        assert _c(pulse_per_minute=p).pulse == pts

    def test_consciousness(self) -> None:
        assert _c(consciousness="confusion_or_vpu").consciousness == 3
        assert _c().consciousness == 0

    @pytest.mark.parametrize("t,pts", [(35.0, 3), (35.1, 1), (36.0, 1), (36.1, 0), (38.0, 0), (38.1, 1), (39.0, 1), (39.1, 2)])
    def test_temperature(self, t: float, pts: int) -> None:
        assert _c(temperature_celsius=t).temperature == pts


class TestAggregateAndBands:
    def test_all_normal_zero_low(self) -> None:
        r = news2_assessment(_f())
        assert r.score == 0 and r.monitoring_band == "low"
        assert r.any_parameter_scored_3 is False

    def test_red_score_low_medium(self) -> None:
        # Single parameter = 3 (RR 26), aggregate 3 -> low_medium.
        r = news2_assessment(_f(respiratory_rate_per_minute=26))
        assert r.score == 3 and r.any_parameter_scored_3 is True
        assert r.monitoring_band == "low_medium"

    def test_aggregate_without_red_is_low(self) -> None:
        # RR 22 (2) + temp 38.5 (1) + pulse 95 (1) = 4, no red -> low.
        r = news2_assessment(_f(respiratory_rate_per_minute=22, temperature_celsius=38.5, pulse_per_minute=95))
        assert r.score == 4 and r.monitoring_band == "low"

    def test_medium_5(self) -> None:
        # spo2 92 scale1 (2) + sbp 95 (2) + pulse 95 (1) = 5
        r = news2_assessment(_f(spo2_percent=92, systolic_bp_mmhg=95, pulse_per_minute=95))
        assert r.score == 5 and r.monitoring_band == "medium"

    def test_high_7(self) -> None:
        # RR 26 (3) + sbp 88 (3) + pulse 95 (1) = 7
        r = news2_assessment(_f(respiratory_rate_per_minute=26, systolic_bp_mmhg=88, pulse_per_minute=95))
        assert r.score == 7 and r.monitoring_band == "high"

    def test_components_sum(self) -> None:
        f = _f(respiratory_rate_per_minute=22, spo2_percent=92, on_supplemental_oxygen=True)
        c = news2_component_scores(f)
        assert (c.respiratory_rate + c.spo2 + c.supplemental_oxygen + c.systolic_bp
                + c.pulse + c.consciousness + c.temperature) == news2_score(f)


class TestOutputAndValidation:
    def test_citations(self) -> None:
        assert "RCP 2017" in news2_assessment(_f()).citations

    def test_caveats_mention_scale2_and_pregnancy(self) -> None:
        text = " ".join(news2_assessment(_f()).population_caveats).lower()
        assert "scale 2" in text and "pregnancy" in text

    def test_high_response_mentions_critical_care(self) -> None:
        r = news2_assessment(_f(respiratory_rate_per_minute=26, systolic_bp_mmhg=88, pulse_per_minute=95))
        assert "critical-care" in r.recommended_response.lower()

    def test_bad_spo2_raises(self) -> None:
        with pytest.raises(ValueError):
            news2_score(_f(spo2_percent=101))

    def test_negative_rr_raises(self) -> None:
        with pytest.raises(ValueError):
            news2_score(_f(respiratory_rate_per_minute=-1))
