"""Tests for CIWA-Ar."""

from __future__ import annotations

import pytest

from conditions.alcohol_withdrawal.ciwa_ar import CiwaArFeatures, ciwa_ar_assessment, ciwa_ar_score

_D = {k: 0 for k in (
    "nausea_vomiting", "tremor", "paroxysmal_sweats", "anxiety", "agitation",
    "tactile_disturbances", "auditory_disturbances", "visual_disturbances",
    "headache_fullness_in_head", "orientation_clouding_of_sensorium")}


def _f(**o: int) -> CiwaArFeatures:
    return CiwaArFeatures(**(_D | o))


class TestScore:
    def test_zero(self) -> None:
        assert ciwa_ar_score(_f()) == 0

    def test_sums_items(self) -> None:
        assert ciwa_ar_score(_f(tremor=4, anxiety=3, orientation_clouding_of_sensorium=2)) == 9

    def test_max_67(self) -> None:
        f = _f(**{k: 7 for k in _D if k != "orientation_clouding_of_sensorium"},
               orientation_clouding_of_sensorium=4)
        assert ciwa_ar_score(f) == 67


class TestBands:
    def test_minimal_below_8(self) -> None:
        assert ciwa_ar_assessment(_f(tremor=7)).severity_band == "minimal"  # 7

    def test_mild_to_moderate_8_and_15(self) -> None:
        assert ciwa_ar_assessment(_f(tremor=7, anxiety=1)).severity_band == "mild_to_moderate"  # 8
        assert ciwa_ar_assessment(_f(tremor=7, anxiety=7, agitation=1)).severity_band == "mild_to_moderate"  # 15

    def test_moderate_to_severe_16_and_20(self) -> None:
        assert ciwa_ar_assessment(_f(tremor=7, anxiety=7, agitation=2)).severity_band == "moderate_to_severe"  # 16
        assert ciwa_ar_assessment(_f(tremor=7, anxiety=7, agitation=6)).severity_band == "moderate_to_severe"  # 20

    def test_severe_above_20(self) -> None:
        assert ciwa_ar_assessment(_f(tremor=7, anxiety=7, agitation=7)).severity_band == "severe"  # 21


class TestOutputAndValidation:
    def test_citations(self) -> None:
        assert "Sullivan 1989" in ciwa_ar_assessment(_f()).citations

    def test_caveats_mention_cooperative_and_protocol(self) -> None:
        text = " ".join(ciwa_ar_assessment(_f()).population_caveats).lower()
        assert "cooperative" in text and "protocol" in text

    def test_severe_action_mentions_dts(self) -> None:
        assert "delirium tremens" in ciwa_ar_assessment(_f(tremor=7, anxiety=7, agitation=7)).recommended_action.lower()

    def test_item_over_7_raises(self) -> None:
        with pytest.raises(ValueError):
            ciwa_ar_score(_f(tremor=8))

    def test_orientation_over_4_raises(self) -> None:
        with pytest.raises(ValueError):
            ciwa_ar_score(_f(orientation_clouding_of_sensorium=5))

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            ciwa_ar_score(_f(anxiety=-1))
