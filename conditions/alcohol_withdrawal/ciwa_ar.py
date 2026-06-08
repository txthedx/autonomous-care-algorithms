"""CIWA-Ar (revised Clinical Institute Withdrawal Assessment for Alcohol).

Reference:
    Sullivan JT, Sykora K, Schneiderman J, Naranjo CA, Sellers EM.
        Assessment of alcohol withdrawal: the revised Clinical Institute
        Withdrawal Assessment for Alcohol scale (CIWA-Ar).
        Br J Addict. 1989;84(11):1353-1357. PMID: 2597811.

CIWA-Ar quantifies the severity of alcohol withdrawal from ten rater-scored
items (nine scored 0-7, plus orientation scored 0-4) for a total of 0 to 67. It
is used to guide symptom-triggered therapy.

The item scores are factual to the instrument. The severity bands below are the
commonly used clinical interpretation; the original instrument did not prescribe
fixed thresholds, and the exact score that triggers medication (and the agent
used) are set by local protocol. CIWA-Ar requires a cooperative, communicative
patient. Not a medical device; see DISCLAIMER.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SeverityBand = Literal["minimal", "mild_to_moderate", "moderate_to_severe", "severe"]


@dataclass(frozen=True)
class CiwaArFeatures:
    """The ten CIWA-Ar items (rater-scored severities).

    Nine items are scored 0-7; orientation/clouding of sensorium is scored 0-4.

    Attributes:
        nausea_vomiting: Nausea and vomiting (0-7).
        tremor: Tremor (0-7).
        paroxysmal_sweats: Paroxysmal sweats (0-7).
        anxiety: Anxiety (0-7).
        agitation: Agitation (0-7).
        tactile_disturbances: Tactile disturbances (0-7).
        auditory_disturbances: Auditory disturbances (0-7).
        visual_disturbances: Visual disturbances (0-7).
        headache_fullness_in_head: Headache or fullness in the head (0-7).
        orientation_clouding_of_sensorium: Orientation and clouding of
            sensorium (0-4).
    """

    nausea_vomiting: int
    tremor: int
    paroxysmal_sweats: int
    anxiety: int
    agitation: int
    tactile_disturbances: int
    auditory_disturbances: int
    visual_disturbances: int
    headache_fullness_in_head: int
    orientation_clouding_of_sensorium: int


@dataclass(frozen=True)
class CiwaArResult:
    """CIWA-Ar assessment result.

    Attributes:
        score: Total CIWA-Ar score, range 0 to 67.
        severity_band: "minimal", "mild_to_moderate", "moderate_to_severe", or
            "severe" (commonly used interpretation).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be interpreted
            with care.
        citations: Source short tags.
    """

    score: int
    severity_band: SeverityBand
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_SEVEN_POINT_ITEMS: tuple[str, ...] = (
    "nausea_vomiting", "tremor", "paroxysmal_sweats", "anxiety", "agitation",
    "tactile_disturbances", "auditory_disturbances", "visual_disturbances",
    "headache_fullness_in_head",
)

_POPULATION_CAVEATS: tuple[str, ...] = (
    "CIWA-Ar requires a cooperative, communicative patient. It is unreliable in "
    "delirium, intubation, severe agitation, or communication barriers, where "
    "other approaches are used.",
    "The instrument quantifies withdrawal severity to guide symptom-triggered "
    "therapy; it is not a standalone protocol. The score that triggers "
    "medication and the agent used are set by local protocol.",
    "Higher scores (commonly > 20) indicate severe withdrawal with increased "
    "risk of seizures and delirium tremens.",
    "The severity bands are the commonly used clinical interpretation; the "
    "original instrument (Sullivan 1989) did not prescribe fixed thresholds.",
)


def _check(features: CiwaArFeatures) -> None:
    for name in _SEVEN_POINT_ITEMS:
        value = getattr(features, name)
        if not 0 <= value <= 7:
            raise ValueError(f"{name} must be between 0 and 7")
    if not 0 <= features.orientation_clouding_of_sensorium <= 4:
        raise ValueError("orientation_clouding_of_sensorium must be between 0 and 4")


def ciwa_ar_score(features: CiwaArFeatures) -> int:
    """Compute the CIWA-Ar score, range 0 to 67.

    Raises:
        ValueError: If any item is out of range.
    """
    _check(features)
    return (
        sum(getattr(features, name) for name in _SEVEN_POINT_ITEMS)
        + features.orientation_clouding_of_sensorium
    )


def ciwa_ar_assessment(features: CiwaArFeatures) -> CiwaArResult:
    """Compute CIWA-Ar and its severity band.

    Args:
        features: The ten items. See `CiwaArFeatures`.

    Returns:
        A `CiwaArResult`.

    Raises:
        ValueError: If any item is out of range.
    """
    score = ciwa_ar_score(features)
    citations = ("Sullivan 1989",)

    if score < 8:
        band: SeverityBand = "minimal"
        action = ("Minimal withdrawal. Supportive care and monitoring; "
                  "medication is often not required at this level per protocol.")
    elif score <= 15:
        band = "mild_to_moderate"
        action = ("Mild to moderate withdrawal. Symptom-triggered therapy per "
                  "local protocol with reassessment.")
    elif score <= 20:
        band = "moderate_to_severe"
        action = ("Moderate to severe withdrawal. Symptom-triggered therapy and "
                  "closer monitoring per local protocol.")
    else:
        band = "severe"
        action = ("Severe withdrawal with increased risk of seizures and "
                  "delirium tremens. Urgent treatment and close monitoring per "
                  "local protocol; consider a higher-acuity setting.")

    return CiwaArResult(
        score=score,
        severity_band=band,
        recommended_action=action,
        rationale=f"A CIWA-Ar score of {score} corresponds to the {band.replace('_', ' ')} band (commonly used interpretation).",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
