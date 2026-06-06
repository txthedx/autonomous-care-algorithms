"""NEXUS low-risk criteria for cervical-spine imaging after blunt trauma.

Reference:
    Hoffman JR, Mower WR, Wolfson AB, Todd KH, Zucker MI.
        Validity of a set of clinical criteria to rule out injury to the
        cervical spine in patients with blunt trauma. N Engl J Med.
        2000;343(2):94-99. PMID: 10891516.

The NEXUS (National Emergency X-Radiography Utilization Study) low-risk criteria
identify blunt-trauma patients in whom clinically significant cervical-spine
injury is unlikely, so that imaging can be deferred. Cervical-spine imaging is
**not required** only when **all five** low-risk criteria are satisfied — that
is, when **none** of the five risk findings below is present.

The rule applies to alert, stable patients with blunt trauma. It is not a
substitute for clinical judgement; see the population caveats and DISCLAIMER.md
at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NexusFeatures:
    """Risk findings for the NEXUS low-risk criteria.

    Each field is the *risk finding*; imaging is not required only when all
    five are False (i.e., all five NEXUS low-risk criteria are satisfied).

    Attributes:
        posterior_midline_cervical_tenderness: Posterior midline cervical-spine
            tenderness. Risk finding.
        focal_neurologic_deficit: Any focal neurologic deficit. Risk finding.
        altered_alertness: Anything less than a normal level of alertness.
            Risk finding.
        evidence_of_intoxication: Clinical evidence of intoxication. Risk
            finding.
        distracting_injury: A clinically apparent painful injury that might
            distract the patient from the pain of a cervical-spine injury.
            Risk finding.
    """

    posterior_midline_cervical_tenderness: bool
    focal_neurologic_deficit: bool
    altered_alertness: bool
    evidence_of_intoxication: bool
    distracting_injury: bool


@dataclass(frozen=True)
class NexusResult:
    """NEXUS assessment result.

    Attributes:
        imaging_indicated: True if any NEXUS criterion is present (so the
            patient cannot be cleared without imaging).
        risk_findings_present: Labels of the criteria that are present.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the rule must not be applied
            or must be interpreted with care.
        citations: Source short tags.
    """

    imaging_indicated: bool
    risk_findings_present: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_FIELD_LABELS: dict[str, str] = {
    "posterior_midline_cervical_tenderness": "posterior midline cervical tenderness",
    "focal_neurologic_deficit": "focal neurologic deficit",
    "altered_alertness": "altered level of alertness",
    "evidence_of_intoxication": "evidence of intoxication",
    "distracting_injury": "painful distracting injury",
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "Applies to alert, stable patients with blunt trauma. It does not apply to "
    "penetrating trauma.",
    "Does not apply to patients with a reduced level of consciousness (the "
    "'normal alertness' criterion already fails in GCS < 15).",
    "Pediatric performance is less well established than in adults; apply with "
    "caution and clinical judgement in children.",
    "The criteria are clinical judgements (e.g., what counts as a 'distracting' "
    "injury); the rule supports but does not replace clinical assessment.",
)


def nexus_risk_findings(features: NexusFeatures) -> tuple[str, ...]:
    """Return labels of the NEXUS criteria that are present (non-low-risk)."""
    return tuple(
        label for attr, label in _FIELD_LABELS.items() if getattr(features, attr)
    )


def nexus_assessment(features: NexusFeatures) -> NexusResult:
    """Apply the NEXUS low-risk criteria.

    Args:
        features: Risk findings. See `NexusFeatures`.

    Returns:
        A `NexusResult`. `imaging_indicated` is True if any criterion is present.
    """
    findings = nexus_risk_findings(features)
    citations = ("Hoffman 2000",)

    if findings:
        return NexusResult(
            imaging_indicated=True,
            risk_findings_present=findings,
            recommended_action=(
                "One or more NEXUS criteria are present; cervical-spine imaging "
                "is indicated."
            ),
            rationale="At least one NEXUS low-risk criterion is not satisfied.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return NexusResult(
        imaging_indicated=False,
        risk_findings_present=(),
        recommended_action=(
            "All five NEXUS low-risk criteria are satisfied; cervical-spine "
            "imaging is not required by NEXUS. Apply clinical judgement and the "
            "rule's exclusions."
        ),
        rationale="All five NEXUS low-risk criteria are satisfied (no risk findings present).",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
