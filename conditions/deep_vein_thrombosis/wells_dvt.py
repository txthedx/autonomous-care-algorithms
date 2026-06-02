"""Wells DVT score: original (1997) and modified (2003) interpretations.

References:
    Wells PS, Anderson DR, Bormanis J, Guy F, Mitchell M, Gray L, Clement C,
    Robinson KS, Lewandowski B.
        Value of assessment of pretest probability of deep-vein thrombosis
        in clinical management. Lancet. 1997;350(9094):1795-1798.
        PMID: 9428249.
    Wells PS, Anderson DR, Rodger M, et al.
        Evaluation of D-dimer in the diagnosis of suspected deep-vein
        thrombosis. N Engl J Med. 2003;349(13):1227-1235.
        PMID: 14507948.
    Scarvelis D, Wells PS.
        Diagnosis and treatment of deep-vein thrombosis. CMAJ.
        2006;175(9):1087-1092.

This module applies to symptomatic outpatients with suspected acute
lower-extremity DVT. It does not apply to upper-extremity DVT,
pregnancy, or hospitalized populations without independent clinical
synthesis. See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TwoTierBand = Literal["unlikely", "likely"]
ThreeTierBand = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class WellsDvtFeatures:
    """Clinical features for the Wells DVT score.

    All items contribute +1 except `alternative_diagnosis_at_least_as_likely`,
    which contributes -2. The `previously_documented_dvt` item is part of
    the 2003 modification only and is not used in the 1997 three-tier score.

    Attributes:
        active_cancer: Active cancer (treatment within 6 months or palliative).
        paralysis_paresis_or_recent_lower_limb_immobilization: Paralysis,
            paresis, or recent plaster immobilization of a lower extremity.
        recently_bedridden_3_days_or_major_surgery_within_12_weeks:
            Recently bedridden for at least 3 days, or major surgery within
            the past 12 weeks requiring general or regional anesthesia.
        localized_tenderness_along_deep_venous_system: Localized tenderness
            along the distribution of the deep venous system.
        entire_leg_swollen: Entire leg swelling.
        calf_swelling_more_than_3cm: Calf swelling more than 3 cm compared
            with the asymptomatic leg, measured 10 cm below the tibial
            tuberosity.
        pitting_edema_in_symptomatic_leg: Pitting edema confined to the
            symptomatic leg.
        collateral_superficial_veins_non_varicose: Non-varicose collateral
            superficial veins.
        previously_documented_dvt: Previously documented DVT. Added in the
            2003 modification.
        alternative_diagnosis_at_least_as_likely: Alternative diagnosis at
            least as likely as DVT. Contributes **-2** points.
    """

    active_cancer: bool
    paralysis_paresis_or_recent_lower_limb_immobilization: bool
    recently_bedridden_3_days_or_major_surgery_within_12_weeks: bool
    localized_tenderness_along_deep_venous_system: bool
    entire_leg_swollen: bool
    calf_swelling_more_than_3cm: bool
    pitting_edema_in_symptomatic_leg: bool
    collateral_superficial_veins_non_varicose: bool
    previously_documented_dvt: bool
    alternative_diagnosis_at_least_as_likely: bool


@dataclass(frozen=True)
class WellsDvtTwoTierResult:
    """Modified Wells (2003) two-tier interpretation.

    Attributes:
        score: Modified Wells score, range -2 to 9.
        risk_band: "unlikely" or "likely".
        recommended_action: Narrative recommendation aligned to Wells 2003.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: int
    risk_band: TwoTierBand
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


@dataclass(frozen=True)
class WellsDvtThreeTierResult:
    """Original Wells (1997) three-tier interpretation.

    Attributes:
        score: Original Wells score, range -2 to 8. The previously-documented-DVT
            item is **not** included in this score.
        risk_band: "low", "moderate", or "high".
        estimated_dvt_prevalence_band: Approximate prevalence band from
            Wells 1997 derivation cohort.
        recommended_action: Narrative recommendation aligned to Wells 1997.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: int
    risk_band: ThreeTierBand
    estimated_dvt_prevalence_band: str
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


_POSITIVE_ITEMS_BOTH_VERSIONS: tuple[str, ...] = (
    "active_cancer",
    "paralysis_paresis_or_recent_lower_limb_immobilization",
    "recently_bedridden_3_days_or_major_surgery_within_12_weeks",
    "localized_tenderness_along_deep_venous_system",
    "entire_leg_swollen",
    "calf_swelling_more_than_3cm",
    "pitting_edema_in_symptomatic_leg",
    "collateral_superficial_veins_non_varicose",
)


def _shared_positive_points(features: WellsDvtFeatures) -> int:
    return sum(int(getattr(features, attr)) for attr in _POSITIVE_ITEMS_BOTH_VERSIONS)


def _alternative_diagnosis_points(features: WellsDvtFeatures) -> int:
    return -2 if features.alternative_diagnosis_at_least_as_likely else 0


def wells_dvt_score_modified(features: WellsDvtFeatures) -> int:
    """Compute the modified (2003) Wells DVT score, range -2 to 9.

    Includes the previously-documented-DVT item.
    """
    return (
        _shared_positive_points(features)
        + int(features.previously_documented_dvt)
        + _alternative_diagnosis_points(features)
    )


def wells_dvt_score_original(features: WellsDvtFeatures) -> int:
    """Compute the original (1997) Wells DVT score, range -2 to 8.

    Excludes the previously-documented-DVT item, which was not part of the
    1997 derivation.
    """
    return _shared_positive_points(features) + _alternative_diagnosis_points(features)


def wells_dvt_two_tier(features: WellsDvtFeatures) -> WellsDvtTwoTierResult:
    """Return the modified (2003) two-tier interpretation.

    Args:
        features: Clinical features. See `WellsDvtFeatures`.

    Returns:
        A `WellsDvtTwoTierResult` with score, risk band, and recommendation.
    """
    score = wells_dvt_score_modified(features)
    citations = ("Wells 2003", "Scarvelis 2006")

    if score <= 1:
        return WellsDvtTwoTierResult(
            score=score,
            risk_band="unlikely",
            recommended_action=(
                "DVT unlikely. Obtain a sensitive (high-sensitivity) D-dimer assay. "
                "A negative D-dimer excludes DVT without imaging. "
                "A positive D-dimer requires compression ultrasound."
            ),
            rationale="Modified Wells score of 1 or less corresponds to a DVT-unlikely pretest probability.",
            citations=citations,
        )

    return WellsDvtTwoTierResult(
        score=score,
        risk_band="likely",
        recommended_action=(
            "DVT likely. Proceed directly to compression ultrasound. "
            "D-dimer is not required for rule-out at this probability. "
            "If initial ultrasound is negative and clinical suspicion persists, consider repeat imaging or further evaluation."
        ),
        rationale="Modified Wells score of 2 or more corresponds to a DVT-likely pretest probability.",
        citations=citations,
    )


def wells_dvt_three_tier(features: WellsDvtFeatures) -> WellsDvtThreeTierResult:
    """Return the original (1997) three-tier interpretation.

    Args:
        features: Clinical features. See `WellsDvtFeatures`.

    Returns:
        A `WellsDvtThreeTierResult` with score (1997 form, no previously-
        documented-DVT term), risk band, prevalence estimate, and
        recommendation.
    """
    score = wells_dvt_score_original(features)
    citations = ("Wells 1997", "Scarvelis 2006")

    if score <= 0:
        return WellsDvtThreeTierResult(
            score=score,
            risk_band="low",
            estimated_dvt_prevalence_band="approximately 3% (Wells 1997)",
            recommended_action=(
                "Low pretest probability. Obtain a sensitive D-dimer. "
                "A negative result excludes DVT without imaging. "
                "A positive result requires compression ultrasound."
            ),
            rationale="Original Wells score of 0 or less corresponds to low pretest probability.",
            citations=citations,
        )

    if score <= 2:
        return WellsDvtThreeTierResult(
            score=score,
            risk_band="moderate",
            estimated_dvt_prevalence_band="approximately 17% (Wells 1997)",
            recommended_action=(
                "Moderate pretest probability. Compression ultrasound is recommended."
            ),
            rationale="Original Wells score of 1 or 2 corresponds to moderate pretest probability.",
            citations=citations,
        )

    return WellsDvtThreeTierResult(
        score=score,
        risk_band="high",
        estimated_dvt_prevalence_band="approximately 75% (Wells 1997)",
        recommended_action=(
            "High pretest probability. Compression ultrasound is recommended. "
            "If the initial ultrasound is negative and clinical suspicion persists, consider repeat imaging in approximately one week."
        ),
        rationale="Original Wells score of 3 or more corresponds to high pretest probability.",
        citations=citations,
    )
