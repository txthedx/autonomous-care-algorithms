"""CRB-65 severity score for community-acquired pneumonia in primary care.

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

CRB-65 omits the urea criterion of CURB-65 and is intended for use in
primary care and community settings where serum urea is not immediately
available. Adults with community-acquired pneumonia only.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SeverityBand = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class Crb65Features:
    """Clinical features for CRB-65 (no laboratory data required).

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
        confusion: New disorientation in person, place, or time, or AMTS ≤ 8.
        respiratory_rate_per_minute: Resting respiratory rate. Must be
            non-negative.
        systolic_bp_mmhg: Systolic blood pressure in mmHg. Must be non-negative.
        diastolic_bp_mmhg: Diastolic blood pressure in mmHg. Must be non-negative.
    """

    age_years: int
    confusion: bool
    respiratory_rate_per_minute: int
    systolic_bp_mmhg: int
    diastolic_bp_mmhg: int


@dataclass(frozen=True)
class Crb65Result:
    """CRB-65 scoring and disposition result.

    Attributes:
        score: Sum of the four criteria, range 0 to 4.
        criteria_present: Tuple of the score components that were met.
        severity_band: "low", "moderate", or "high".
        recommended_disposition: Narrative disposition aligned with Lim 2003
            and BTS 2009. Includes a reminder of factors the score does not
            capture.
        mortality_band: Approximate 30-day mortality band from Lim 2003.
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


def _validate(features: Crb65Features) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")
    if features.respiratory_rate_per_minute < 0:
        raise ValueError("respiratory_rate_per_minute must be non-negative")
    if features.systolic_bp_mmhg < 0 or features.diastolic_bp_mmhg < 0:
        raise ValueError("blood pressure values must be non-negative")


def crb_65_criteria(features: Crb65Features) -> tuple[str, ...]:
    """Return the labels of the CRB-65 criteria that are met."""
    _validate(features)
    present: list[str] = []
    if features.confusion:
        present.append("confusion")
    if features.respiratory_rate_per_minute >= 30:
        present.append("respiratory rate >= 30/min")
    if features.systolic_bp_mmhg < 90 or features.diastolic_bp_mmhg <= 60:
        present.append("SBP < 90 or DBP <= 60 mmHg")
    if features.age_years >= 65:
        present.append("age >= 65 years")
    return tuple(present)


def crb_65_score(features: Crb65Features) -> int:
    """Compute the CRB-65 score, range 0 to 4."""
    return len(crb_65_criteria(features))


def crb_65_assessment(features: Crb65Features) -> Crb65Result:
    """Return the CRB-65 score, severity band, and disposition recommendation.

    Args:
        features: The clinical features. See `Crb65Features`.

    Returns:
        A `Crb65Result` with score, criteria present, severity band,
        recommended disposition, mortality band, rationale, and citations.
    """
    criteria = crb_65_criteria(features)
    score = len(criteria)

    if score == 0:
        band: SeverityBand = "low"
        disposition = (
            "Low severity. Outpatient treatment is likely appropriate in patients without other concerning features. "
            + _UNCAPTURED_REMINDER
        )
        mortality = "approximately 1.2% at 30 days (Lim 2003)"
        rationale = "CRB-65 of 0 corresponds to low 30-day mortality risk."
    elif score in (1, 2):
        band = "moderate"
        disposition = (
            "Moderate severity. Consider hospital referral for assessment. "
            + _UNCAPTURED_REMINDER
        )
        mortality = "approximately 8.5% at 30 days (Lim 2003)"
        rationale = "CRB-65 of 1 or 2 corresponds to moderate 30-day mortality risk."
    else:
        band = "high"
        disposition = (
            "High severity. Urgent hospital admission. "
            + _UNCAPTURED_REMINDER
        )
        mortality = "approximately 31% at 30 days (Lim 2003)"
        rationale = "CRB-65 of 3 or 4 corresponds to high 30-day mortality risk."

    return Crb65Result(
        score=score,
        criteria_present=criteria,
        severity_band=band,
        recommended_disposition=disposition,
        mortality_band=mortality,
        rationale=rationale,
        citations=("Lim 2003", "BTS 2009", "NICE NG138"),
    )
