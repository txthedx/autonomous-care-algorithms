"""Revised Geneva score for pretest probability of pulmonary embolism.

Reference:
    Le Gal G, Righini M, Roy PM, et al.
        Prediction of pulmonary embolism in the emergency department: the
        revised Geneva score. Ann Intern Med. 2006;144(3):165-171.
        PMID: 16461960.

A fully clinical (no-gestalt) pretest-probability score for PE — an alternative
to the Wells PE score. Eight weighted items give a total of 0 to 22, stratified
into low, intermediate, and high probability. Age and heart rate are entered as
raw values; the remaining items are clinical findings.

Not a medical device; this is a pretest-probability aid, not a diagnosis. See
DISCLAIMER.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskBand = Literal["low", "intermediate", "high"]


@dataclass(frozen=True)
class GenevaFeatures:
    """Clinical features for the revised Geneva score.

    Attributes:
        age_years: Age in years. Scores 1 if > 65.
        previous_dvt_or_pe: Previous DVT or PE. +3.
        surgery_or_lower_limb_fracture_within_1_month: Surgery (under general
            anesthesia) or lower-limb fracture within the past month. +2.
        active_malignancy: Active malignancy (solid or hematologic, currently
            active or considered cured < 1 year). +2.
        unilateral_lower_limb_pain: Unilateral lower-limb pain. +3.
        hemoptysis: Hemoptysis. +2.
        heart_rate_per_minute: Heart rate. 75-94 scores +3, >= 95 scores +5.
        pain_on_deep_venous_palpation_and_unilateral_edema: Pain on lower-limb
            deep venous palpation and unilateral edema. +4.
    """

    age_years: int
    previous_dvt_or_pe: bool
    surgery_or_lower_limb_fracture_within_1_month: bool
    active_malignancy: bool
    unilateral_lower_limb_pain: bool
    hemoptysis: bool
    heart_rate_per_minute: int
    pain_on_deep_venous_palpation_and_unilateral_edema: bool


@dataclass(frozen=True)
class GenevaResult:
    """Revised Geneva assessment result.

    Attributes:
        score: Total score, range 0 to 22.
        risk_band: "low" (0-3), "intermediate" (4-10), or "high" (>= 11).
        estimated_pe_prevalence_band: Approximate PE prevalence (Le Gal 2006).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be interpreted
            with care.
        citations: Source short tags.
    """

    score: int
    risk_band: RiskBand
    estimated_pe_prevalence_band: str
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "A pretest-probability aid for suspected PE, not a diagnosis. Combine with "
    "D-dimer and imaging (CT pulmonary angiography) per the diagnostic pathway.",
    "Does not apply to hemodynamically unstable patients, who warrant immediate "
    "evaluation regardless of score.",
    "Age and heart rate are entered as raw values; the > 65 and 75-94 / >= 95 "
    "thresholds are applied internally.",
)


def _check(features: GenevaFeatures) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must not be negative")
    if features.heart_rate_per_minute < 0:
        raise ValueError("heart_rate_per_minute must not be negative")


def _heart_rate_points(heart_rate_per_minute: int) -> int:
    if heart_rate_per_minute >= 95:
        return 5
    if heart_rate_per_minute >= 75:
        return 3
    return 0


def geneva_score(features: GenevaFeatures) -> int:
    """Compute the revised Geneva score, range 0 to 22."""
    _check(features)
    score = 0
    if features.age_years > 65:
        score += 1
    if features.previous_dvt_or_pe:
        score += 3
    if features.surgery_or_lower_limb_fracture_within_1_month:
        score += 2
    if features.active_malignancy:
        score += 2
    if features.unilateral_lower_limb_pain:
        score += 3
    if features.hemoptysis:
        score += 2
    score += _heart_rate_points(features.heart_rate_per_minute)
    if features.pain_on_deep_venous_palpation_and_unilateral_edema:
        score += 4
    return score


def geneva_assessment(features: GenevaFeatures) -> GenevaResult:
    """Compute the revised Geneva score and its three-tier probability band.

    Args:
        features: Clinical features. See `GenevaFeatures`.

    Returns:
        A `GenevaResult`.

    Raises:
        ValueError: If age or heart rate is negative.
    """
    score = geneva_score(features)
    citations = ("Le Gal 2006",)

    if score <= 3:
        return GenevaResult(
            score=score, risk_band="low",
            estimated_pe_prevalence_band="approximately 8% (Le Gal 2006)",
            recommended_action=(
                "Low pretest probability. Obtain a sensitive D-dimer; PE is "
                "excluded if negative, and CT pulmonary angiography is reserved "
                "for a positive result."
            ),
            rationale="A revised Geneva score of 3 or less corresponds to low pretest probability.",
            population_caveats=_POPULATION_CAVEATS, citations=citations,
        )
    if score <= 10:
        return GenevaResult(
            score=score, risk_band="intermediate",
            estimated_pe_prevalence_band="approximately 29% (Le Gal 2006)",
            recommended_action=(
                "Intermediate pretest probability. Obtain a sensitive D-dimer "
                "and proceed to CT pulmonary angiography if positive."
            ),
            rationale="A revised Geneva score of 4 to 10 corresponds to intermediate pretest probability.",
            population_caveats=_POPULATION_CAVEATS, citations=citations,
        )
    return GenevaResult(
        score=score, risk_band="high",
        estimated_pe_prevalence_band="approximately 74% (Le Gal 2006)",
        recommended_action=(
            "High pretest probability. Proceed to CT pulmonary angiography; "
            "D-dimer is not appropriate for rule-out at this probability."
        ),
        rationale="A revised Geneva score of 11 or more corresponds to high pretest probability.",
        population_caveats=_POPULATION_CAVEATS, citations=citations,
    )
