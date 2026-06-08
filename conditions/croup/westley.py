"""Westley Croup Score for croup severity.

Reference:
    Westley CR, Cotton EK, Brooks JG.
        Nebulized racemic epinephrine by IPPB for the treatment of croup: a
        double-blind study. Am J Dis Child. 1978;132(5):484-487. PMID: 347921.

The Westley Croup Score grades the severity of croup (laryngotracheobronchitis)
from five clinical items for a total of 0 to 17. It is a severity grading tool,
not a diagnosis; severe or impending-failure scores warrant urgent intervention
regardless of the number. Not a medical device; see DISCLAIMER.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ConsciousnessLevel = Literal["normal", "disoriented"]
CyanosisLevel = Literal["none", "with_agitation", "at_rest"]
StridorLevel = Literal["none", "with_agitation", "at_rest"]
AirEntryLevel = Literal["normal", "decreased", "markedly_decreased"]
RetractionsLevel = Literal["none", "mild", "moderate", "severe"]
SeverityBand = Literal["mild", "moderate", "severe", "impending_respiratory_failure"]


@dataclass(frozen=True)
class WestleyFeatures:
    """The five Westley Croup Score items.

    Attributes:
        level_of_consciousness: "normal" (0) or "disoriented" (5).
        cyanosis: "none" (0), "with_agitation" (4), or "at_rest" (5).
        stridor: "none" (0), "with_agitation" (1), or "at_rest" (2).
        air_entry: "normal" (0), "decreased" (1), or "markedly_decreased" (2).
        retractions: "none" (0), "mild" (1), "moderate" (2), or "severe" (3).
    """

    level_of_consciousness: ConsciousnessLevel
    cyanosis: CyanosisLevel
    stridor: StridorLevel
    air_entry: AirEntryLevel
    retractions: RetractionsLevel


@dataclass(frozen=True)
class WestleyResult:
    """Westley Croup Score result.

    Attributes:
        score: Total score, range 0 to 17.
        severity_band: "mild" (<= 2), "moderate" (3-5), "severe" (6-11), or
            "impending_respiratory_failure" (>= 12).
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


_CONSCIOUSNESS = {"normal": 0, "disoriented": 5}
_CYANOSIS = {"none": 0, "with_agitation": 4, "at_rest": 5}
_STRIDOR = {"none": 0, "with_agitation": 1, "at_rest": 2}
_AIR_ENTRY = {"normal": 0, "decreased": 1, "markedly_decreased": 2}
_RETRACTIONS = {"none": 0, "mild": 1, "moderate": 2, "severe": 3}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "A clinical grading tool for croup in children; it does not diagnose croup "
    "or exclude other causes of stridor (e.g. foreign body, epiglottitis).",
    "Severe or impending-respiratory-failure scores warrant urgent assessment "
    "and intervention regardless of the exact number.",
    "Cyanosis and altered consciousness are heavily weighted late signs; their "
    "absence does not guarantee mild disease.",
)


def westley_score(features: WestleyFeatures) -> int:
    """Compute the Westley Croup Score, range 0 to 17."""
    return (
        _CONSCIOUSNESS[features.level_of_consciousness]
        + _CYANOSIS[features.cyanosis]
        + _STRIDOR[features.stridor]
        + _AIR_ENTRY[features.air_entry]
        + _RETRACTIONS[features.retractions]
    )


def westley_assessment(features: WestleyFeatures) -> WestleyResult:
    """Compute the Westley Croup Score and its severity band.

    Args:
        features: The five items. See `WestleyFeatures`.

    Returns:
        A `WestleyResult`.
    """
    score = westley_score(features)
    citations = ("Westley 1978",)

    if score <= 2:
        band: SeverityBand = "mild"
        action = "Mild croup. Usually managed with corticosteroids and supportive care."
    elif score <= 5:
        band = "moderate"
        action = "Moderate croup. Corticosteroids; observe; consider nebulized epinephrine."
    elif score <= 11:
        band = "severe"
        action = (
            "Severe croup. Nebulized epinephrine and corticosteroids; close "
            "monitoring and urgent assessment."
        )
    else:
        band = "impending_respiratory_failure"
        action = (
            "Impending respiratory failure. Immediate intervention: airway "
            "support, nebulized epinephrine, corticosteroids, and urgent senior "
            "and critical-care involvement."
        )

    return WestleyResult(
        score=score,
        severity_band=band,
        recommended_action=action,
        rationale=f"A Westley Croup Score of {score} corresponds to the {band.replace('_', ' ')} band.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
