"""CURB-65 severity score for community-acquired pneumonia in adults.

References:
    Lim WS, van der Eerden MM, Laing R, et al.
        Defining community acquired pneumonia severity on presentation to
        hospital: an international derivation and validation study.
        Thorax. 2003;58(5):377-382. PMID: 12728155.
    Lim WS, Baudouin SV, George RC, et al.
        BTS guidelines for the management of community acquired pneumonia
        in adults: update 2009. Thorax. 2009;64 Suppl 3:iii1-55.
        PMID: 19783532.
    NICE Guideline NG138. Pneumonia (community-acquired): antimicrobial
        prescribing. 2019.

This module computes a score and assigns a disposition band. It applies to
adults with community-acquired pneumonia only. It does not apply to
pediatric, hospital-acquired, or immunocompromised pneumonia without
independent clinical synthesis, and it does not provide ICU admission
criteria (see Mandell 2007 / IDSA-ATS for that).

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SeverityBand = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class Curb65Features:
    """Clinical and laboratory features for CURB-65.

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
        confusion: New disorientation in person, place, or time, or
            Abbreviated Mental Test Score (AMTS) of 8 or less.
        urea_mmol_per_l: Serum urea in mmol/L. For US BUN in mg/dL, multiply
            by approximately 0.357 to convert to urea in mmol/L. Must be
            non-negative.
        respiratory_rate_per_minute: Resting respiratory rate. Must be
            non-negative.
        systolic_bp_mmhg: Systolic blood pressure in mmHg. Must be
            non-negative.
        diastolic_bp_mmhg: Diastolic blood pressure in mmHg. Must be
            non-negative.
    """

    age_years: int
    confusion: bool
    urea_mmol_per_l: float
    respiratory_rate_per_minute: int
    systolic_bp_mmhg: int
    diastolic_bp_mmhg: int


@dataclass(frozen=True)
class Curb65Result:
    """CURB-65 scoring and disposition result.

    Attributes:
        score: Sum of the five criteria, range 0 to 5.
        criteria_present: Tuple of the score components that were met.
        severity_band: "low", "moderate", or "high".
        recommended_disposition: Narrative disposition aligned with Lim 2003
            and BTS 2009. Includes an explicit reminder of factors the score
            does not capture.
        mortality_band: Approximate 30-day mortality band from the Lim 2003
            derivation cohort. Vary across validation populations.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: int
    criteria_present: tuple[str, ...]
    severity_band: SeverityBand
    recommended_disposition: str
    mortality_band: str
    rationale: str
    citations: tuple[str, ...]


_UNCAPTURED_REMINDER = (
    "Synthesize with factors the score does not capture: oxygenation (SpO2), "
    "radiographic extent, comorbidities, social factors, and pregnancy."
)


def _validate(features: Curb65Features) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")
    if features.urea_mmol_per_l < 0:
        raise ValueError("urea_mmol_per_l must be non-negative")
    if features.respiratory_rate_per_minute < 0:
        raise ValueError("respiratory_rate_per_minute must be non-negative")
    if features.systolic_bp_mmhg < 0 or features.diastolic_bp_mmhg < 0:
        raise ValueError("blood pressure values must be non-negative")


def curb_65_criteria(features: Curb65Features) -> tuple[str, ...]:
    """Return the labels of the CURB-65 criteria that are met."""
    _validate(features)
    present: list[str] = []
    if features.confusion:
        present.append("confusion")
    if features.urea_mmol_per_l > 7.0:
        present.append("urea > 7 mmol/L")
    if features.respiratory_rate_per_minute >= 30:
        present.append("respiratory rate >= 30/min")
    if features.systolic_bp_mmhg < 90 or features.diastolic_bp_mmhg <= 60:
        present.append("SBP < 90 or DBP <= 60 mmHg")
    if features.age_years >= 65:
        present.append("age >= 65 years")
    return tuple(present)


def curb_65_score(features: Curb65Features) -> int:
    """Compute the CURB-65 score, range 0 to 5."""
    return len(curb_65_criteria(features))


def curb_65_assessment(features: Curb65Features) -> Curb65Result:
    """Return the CURB-65 score, severity band, and disposition recommendation.

    Args:
        features: The clinical and laboratory features. See `Curb65Features`.

    Returns:
        A `Curb65Result` with score, criteria present, severity band,
        recommended disposition, mortality band, rationale, and citations.
    """
    criteria = curb_65_criteria(features)
    score = len(criteria)

    if score <= 1:
        band: SeverityBand = "low"
        disposition = (
            "Low severity. Outpatient treatment is likely appropriate in patients without other concerning features. "
            + _UNCAPTURED_REMINDER
        )
        mortality = "approximately 0.7 to 3% at 30 days (Lim 2003)"
        rationale = "CURB-65 of 0 or 1 corresponds to low 30-day mortality risk."
    elif score == 2:
        band = "moderate"
        disposition = (
            "Moderate severity. Consider hospital-supervised treatment: either short-stay inpatient or closely supervised outpatient if otherwise stable. "
            + _UNCAPTURED_REMINDER
        )
        mortality = "approximately 13% at 30 days (Lim 2003)"
        rationale = "CURB-65 of 2 corresponds to moderate 30-day mortality risk."
    else:
        band = "high"
        if score >= 4:
            disposition = (
                "High severity with ICU consideration. Hospital admission; assess for ICU or high-dependency care using IDSA/ATS 2007 criteria. "
                + _UNCAPTURED_REMINDER
            )
            mortality = "approximately 41 to 57% at 30 days (Lim 2003)"
            rationale = "CURB-65 of 4 or 5 corresponds to very high 30-day mortality risk and merits ICU evaluation."
        else:
            disposition = (
                "High severity. Hospital admission. "
                + _UNCAPTURED_REMINDER
            )
            mortality = "approximately 17% at 30 days (Lim 2003)"
            rationale = "CURB-65 of 3 corresponds to high 30-day mortality risk."

    return Curb65Result(
        score=score,
        criteria_present=criteria,
        severity_band=band,
        recommended_disposition=disposition,
        mortality_band=mortality,
        rationale=rationale,
        citations=("Lim 2003", "BTS 2009", "NICE NG138"),
    )
