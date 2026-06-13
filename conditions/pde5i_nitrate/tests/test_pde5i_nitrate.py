"""Tests for the PDE5 inhibitor + nitrate contraindication screen."""

from __future__ import annotations

import pytest

from conditions.pde5i_nitrate.pde5i_nitrate import (
    NitrateTimingFeatures,
    Pde5iNitrateFeatures,
    nitrate_timing_after_pde5i,
    pde5i_nitrate_contraindication,
)

# Baseline for the forward screen: no concomitant agent present.
_DEFAULT: dict[str, bool] = {
    "nitrate_or_no_donor_use": False,
    "sgc_stimulator_use": False,
}


def _features(**overrides: bool) -> Pde5iNitrateFeatures:
    return Pde5iNitrateFeatures(**(_DEFAULT | overrides))


# Agent -> published interaction interval (hours).
_INTERVALS: dict[str, float] = {
    "sildenafil": 24.0,
    "vardenafil": 24.0,
    "avanafil": 12.0,
    "tadalafil": 48.0,
}


class TestForwardScreenNoContraindication:
    def test_no_agents_is_clear(self) -> None:
        result = pde5i_nitrate_contraindication(_features())
        assert result.verdict == "no_contraindication_detected"
        assert result.contraindicated is False
        assert result.triggering_agents == ()

    def test_action_flags_partial_coverage(self) -> None:
        result = pde5i_nitrate_contraindication(_features())
        assert "only this interaction" in result.recommended_action.lower()


class TestForwardScreenContraindication:
    def test_nitrate_only(self) -> None:
        result = pde5i_nitrate_contraindication(
            _features(nitrate_or_no_donor_use=True)
        )
        assert result.verdict == "absolute_contraindication"
        assert result.contraindicated is True
        assert result.triggering_agents == ("nitrate or nitric-oxide donor",)

    def test_sgc_stimulator_only(self) -> None:
        result = pde5i_nitrate_contraindication(_features(sgc_stimulator_use=True))
        assert result.contraindicated is True
        assert result.triggering_agents == (
            "soluble guanylate cyclase stimulator",
        )

    def test_both_agents_listed(self) -> None:
        result = pde5i_nitrate_contraindication(
            _features(nitrate_or_no_donor_use=True, sgc_stimulator_use=True)
        )
        assert result.contraindicated is True
        assert len(result.triggering_agents) == 2

    def test_action_is_absolute_and_names_hypotension(self) -> None:
        result = pde5i_nitrate_contraindication(
            _features(nitrate_or_no_donor_use=True)
        )
        action = result.recommended_action.lower()
        assert "contraindicated" in action
        assert "absolute contraindication" in action
        assert "hypotension" in action


class TestForwardScreenOutputShape:
    def test_citations_present(self) -> None:
        result = pde5i_nitrate_contraindication(_features())
        assert "Schwartz 2010" in result.citations
        assert "Adempas label" in result.citations

    def test_caveats_name_poppers_and_riociguat(self) -> None:
        text = " ".join(
            pde5i_nitrate_contraindication(_features()).population_caveats
        ).lower()
        assert "poppers" in text
        assert "riociguat" in text

    def test_rationale_non_empty(self) -> None:
        result = pde5i_nitrate_contraindication(_features())
        assert result.rationale.strip() != ""


class TestTimingIntervals:
    def test_each_agent_interval(self) -> None:
        for agent, interval in _INTERVALS.items():
            result = nitrate_timing_after_pde5i(
                NitrateTimingFeatures(
                    pde5_inhibitor=agent, hours_since_last_pde5i_dose=0.0
                )
            )
            assert result.interaction_interval_hours == interval, agent


class TestTimingBoundaries:
    def test_just_before_interval_is_contraindicated(self) -> None:
        for agent, interval in _INTERVALS.items():
            result = nitrate_timing_after_pde5i(
                NitrateTimingFeatures(
                    pde5_inhibitor=agent,
                    hours_since_last_pde5i_dose=interval - 0.1,
                )
            )
            assert result.interval_elapsed is False, agent
            assert result.nitrate_coadministration_contraindicated is True, agent

    def test_exactly_at_interval_has_elapsed(self) -> None:
        for agent, interval in _INTERVALS.items():
            result = nitrate_timing_after_pde5i(
                NitrateTimingFeatures(
                    pde5_inhibitor=agent, hours_since_last_pde5i_dose=interval
                )
            )
            assert result.interval_elapsed is True, agent
            assert result.nitrate_coadministration_contraindicated is False, agent

    def test_after_interval_has_elapsed(self) -> None:
        for agent, interval in _INTERVALS.items():
            result = nitrate_timing_after_pde5i(
                NitrateTimingFeatures(
                    pde5_inhibitor=agent,
                    hours_since_last_pde5i_dose=interval + 0.1,
                )
            )
            assert result.interval_elapsed is True, agent

    def test_zero_hours_is_contraindicated(self) -> None:
        result = nitrate_timing_after_pde5i(
            NitrateTimingFeatures(
                pde5_inhibitor="sildenafil", hours_since_last_pde5i_dose=0.0
            )
        )
        assert result.nitrate_coadministration_contraindicated is True


class TestTimingWorkedExampleKloner2003:
    # Kloner 2003: the tadalafil-nitroglycerin interaction lasted 24 h and was
    # absent at or beyond 48 h.
    def test_tadalafil_at_24h_still_contraindicated(self) -> None:
        result = nitrate_timing_after_pde5i(
            NitrateTimingFeatures(
                pde5_inhibitor="tadalafil", hours_since_last_pde5i_dose=24.0
            )
        )
        assert result.nitrate_coadministration_contraindicated is True

    def test_tadalafil_at_48h_has_elapsed(self) -> None:
        result = nitrate_timing_after_pde5i(
            NitrateTimingFeatures(
                pde5_inhibitor="tadalafil", hours_since_last_pde5i_dose=48.0
            )
        )
        assert result.interval_elapsed is True
        assert result.nitrate_coadministration_contraindicated is False


class TestTimingValidationAndShape:
    def test_negative_hours_raises(self) -> None:
        with pytest.raises(ValueError):
            nitrate_timing_after_pde5i(
                NitrateTimingFeatures(
                    pde5_inhibitor="sildenafil",
                    hours_since_last_pde5i_dose=-1.0,
                )
            )

    def test_contraindicated_action_mentions_monitoring(self) -> None:
        result = nitrate_timing_after_pde5i(
            NitrateTimingFeatures(
                pde5_inhibitor="tadalafil", hours_since_last_pde5i_dose=10.0
            )
        )
        assert "monitoring" in result.recommended_action.lower()

    def test_citations_present(self) -> None:
        result = nitrate_timing_after_pde5i(
            NitrateTimingFeatures(
                pde5_inhibitor="avanafil", hours_since_last_pde5i_dose=0.0
            )
        )
        assert "Kloner 2003" in result.citations
        assert "Stendra label" in result.citations
