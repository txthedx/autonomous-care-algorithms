"""Wells PE score: original three-tier and modified two-tier interpretations.

References:
    Wells PS, Anderson DR, Rodger M, et al.
        Derivation of a simple clinical model to categorize patients
        probability of pulmonary embolism: increasing the models utility
        with the SimpliRED D-dimer. Thromb Haemost. 2000;83(3):416-420.
        PMID: 10744147.
    Wells PS, Anderson DR, Rodger M, et al.
        Excluding pulmonary embolism at the bedside without diagnostic
        imaging: management of patients with suspected pulmonary embolism
        presenting to the emergency department by using a simple clinical
        model and d-dimer. Ann Intern Med. 2001;135(2):98-107.
        PMID: 11453709.
    Konstantinides SV, Meyer G, Becattini C, et al.
        2019 ESC Guidelines for the diagnosis and management of acute
        pulmonary embolism. Eur Heart J. 2020;41(4):543-603.
        PMID: 31504429.

This module applies to non-pregnant adults presenting with suspected
acute pulmonary embolism. It does not apply to hemodynamically unstable
patients (who warrant immediate evaluation regardless of score) or to
pregnant patients (separate pregnancy-adapted algorithms apply).

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TwoTierBand = Literal["unlikely", "likely"]
ThreeTierBand = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class WellsPeFeatures:
    """Clinical features for the Wells PE score.

    Attributes:
        clinical_signs_of_dvt: Clinical signs and symptoms of DVT, minimum
            leg swelling and pain with palpation of deep veins. +3.
        pe_at_least_as_likely_as_alternative: PE is at least as likely as
            an alternative diagnosis. +3.
        heart_rate_over_100: Heart rate greater than 100/min. +1.5.
        immobilization_3_days_or_surgery_within_4_weeks: Immobilization
            for at least 3 days, or surgery within the past 4 weeks. +1.5.
        previous_dvt_or_pe: Previously documented DVT or PE. +1.5.
        hemoptysis: Hemoptysis. +1.
        malignancy: Malignancy (treatment within 6 months or palliative). +1.
    """

    clinical_signs_of_dvt: bool
    pe_at_least_as_likely_as_alternative: bool
    heart_rate_over_100: bool
    immobilization_3_days_or_surgery_within_4_weeks: bool
    previous_dvt_or_pe: bool
    hemoptysis: bool
    malignancy: bool


@dataclass(frozen=True)
class WellsPeTwoTierResult:
    """Modified Wells PE two-tier interpretation.

    Attributes:
        score: Wells PE score, range 0 to 12.5.
        risk_band: "unlikely" or "likely".
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: float
    risk_band: TwoTierBand
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


@dataclass(frozen=True)
class WellsPeThreeTierResult:
    """Original Wells PE three-tier interpretation.

    Attributes:
        score: Wells PE score, range 0 to 12.5.
        risk_band: "low", "moderate", or "high".
        estimated_pe_prevalence_band: Approximate prevalence from Wells 2001.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: float
    risk_band: ThreeTierBand
    estimated_pe_prevalence_band: str
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


_ITEM_POINTS: dict[str, float] = {
    "clinical_signs_of_dvt": 3.0,
    "pe_at_least_as_likely_as_alternative": 3.0,
    "heart_rate_over_100": 1.5,
    "immobilization_3_days_or_surgery_within_4_weeks": 1.5,
    "previous_dvt_or_pe": 1.5,
    "hemoptysis": 1.0,
    "malignancy": 1.0,
}


def wells_pe_score(features: WellsPeFeatures) -> float:
    """Compute the Wells PE score, range 0 to 12.5."""
    return sum(points for attr, points in _ITEM_POINTS.items() if getattr(features, attr))


def wells_pe_two_tier(features: WellsPeFeatures) -> WellsPeTwoTierResult:
    """Return the two-tier interpretation (PE unlikely vs likely).

    Args:
        features: Clinical features. See `WellsPeFeatures`.

    Returns:
        A `WellsPeTwoTierResult`.
    """
    score = wells_pe_score(features)
    citations = ("Wells 2001", "Konstantinides 2019")

    if score <= 4.0:
        return WellsPeTwoTierResult(
            score=score,
            risk_band="unlikely",
            recommended_action=(
                "PE unlikely. If the patient is judged to have low pretest probability, "
                "apply PERC; if PERC fails, obtain a sensitive D-dimer. "
                "If pretest probability is moderate, obtain a sensitive D-dimer directly. "
                "Proceed to CT-PA only if D-dimer is positive."
            ),
            rationale="Wells PE score of 4 or less corresponds to a PE-unlikely pretest probability.",
            citations=citations,
        )

    return WellsPeTwoTierResult(
        score=score,
        risk_band="likely",
        recommended_action=(
            "PE likely. Proceed directly to CT pulmonary angiography. "
            "D-dimer is not required for rule-out at this probability. "
            "Consider empirical anticoagulation while imaging is being arranged if there is no contraindication."
        ),
        rationale="Wells PE score greater than 4 corresponds to a PE-likely pretest probability.",
        citations=citations,
    )


def wells_pe_three_tier(features: WellsPeFeatures) -> WellsPeThreeTierResult:
    """Return the three-tier interpretation (low / moderate / high).

    Args:
        features: Clinical features. See `WellsPeFeatures`.

    Returns:
        A `WellsPeThreeTierResult`.
    """
    score = wells_pe_score(features)
    citations = ("Wells 2000", "Wells 2001")

    if score < 2.0:
        return WellsPeThreeTierResult(
            score=score,
            risk_band="low",
            estimated_pe_prevalence_band="approximately 3.6% (Wells 2001)",
            recommended_action=(
                "Low pretest probability. PERC may be applied to rule out PE without further testing. "
                "If PERC fails, obtain a sensitive D-dimer. CT-PA only if D-dimer is positive."
            ),
            rationale="Wells PE score less than 2 corresponds to low pretest probability.",
            citations=citations,
        )

    if score <= 6.0:
        return WellsPeThreeTierResult(
            score=score,
            risk_band="moderate",
            estimated_pe_prevalence_band="approximately 20.5% (Wells 2001)",
            recommended_action=(
                "Moderate pretest probability. Obtain a sensitive D-dimer; proceed to CT-PA if positive. "
                "Do not apply PERC at this probability."
            ),
            rationale="Wells PE score between 2 and 6 inclusive corresponds to moderate pretest probability.",
            citations=citations,
        )

    return WellsPeThreeTierResult(
        score=score,
        risk_band="high",
        estimated_pe_prevalence_band="approximately 66.7% (Wells 2001)",
        recommended_action=(
            "High pretest probability. Proceed directly to CT pulmonary angiography. "
            "D-dimer is not required for rule-out at this probability."
        ),
        rationale="Wells PE score greater than 6 corresponds to high pretest probability.",
        citations=citations,
    )
