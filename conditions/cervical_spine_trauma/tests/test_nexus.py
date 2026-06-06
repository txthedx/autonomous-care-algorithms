"""Tests for the NEXUS low-risk criteria."""

from __future__ import annotations

from conditions.cervical_spine_trauma.nexus import (
    NexusFeatures,
    nexus_assessment,
    nexus_risk_findings,
)

# Baseline: all risk findings absent (all five low-risk criteria satisfied).
_DEFAULT: dict[str, bool] = {
    "posterior_midline_cervical_tenderness": False,
    "focal_neurologic_deficit": False,
    "altered_alertness": False,
    "evidence_of_intoxication": False,
    "distracting_injury": False,
}


def _features(**overrides: bool) -> NexusFeatures:
    return NexusFeatures(**(_DEFAULT | overrides))


class TestNexus:
    def test_all_absent_no_imaging(self) -> None:
        result = nexus_assessment(_features())
        assert result.imaging_indicated is False
        assert result.risk_findings_present == ()

    def test_midline_tenderness_triggers_imaging(self) -> None:
        result = nexus_assessment(_features(posterior_midline_cervical_tenderness=True))
        assert result.imaging_indicated is True
        assert "posterior midline cervical tenderness" in result.risk_findings_present

    def test_focal_deficit_triggers_imaging(self) -> None:
        result = nexus_assessment(_features(focal_neurologic_deficit=True))
        assert result.imaging_indicated is True
        assert "focal neurologic deficit" in result.risk_findings_present

    def test_altered_alertness_triggers_imaging(self) -> None:
        result = nexus_assessment(_features(altered_alertness=True))
        assert result.imaging_indicated is True
        assert "altered level of alertness" in result.risk_findings_present

    def test_intoxication_triggers_imaging(self) -> None:
        result = nexus_assessment(_features(evidence_of_intoxication=True))
        assert result.imaging_indicated is True
        assert "evidence of intoxication" in result.risk_findings_present

    def test_distracting_injury_triggers_imaging(self) -> None:
        result = nexus_assessment(_features(distracting_injury=True))
        assert result.imaging_indicated is True
        assert "painful distracting injury" in result.risk_findings_present

    def test_multiple_findings_all_listed(self) -> None:
        result = nexus_assessment(
            _features(focal_neurologic_deficit=True, evidence_of_intoxication=True)
        )
        assert len(result.risk_findings_present) == 2


class TestOutputShape:
    def test_citation_present(self) -> None:
        result = nexus_assessment(_features())
        assert "Hoffman 2000" in result.citations

    def test_caveats_mention_penetrating_and_pediatric(self) -> None:
        result = nexus_assessment(_features())
        text = " ".join(result.population_caveats).lower()
        assert "penetrating" in text
        assert "pediatric" in text or "children" in text

    def test_cleared_action_mentions_not_required(self) -> None:
        result = nexus_assessment(_features())
        assert "not required" in result.recommended_action.lower()
