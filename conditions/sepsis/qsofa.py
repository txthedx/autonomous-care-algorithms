"""qSOFA (quick SOFA) for suspected infection.

References:
    Singer M, Deutschman CS, Seymour CW, et al.
        The Third International Consensus Definitions for Sepsis and Septic
        Shock (Sepsis-3). JAMA. 2016;315(8):801-810. PMID: 26903338.
    Seymour CW, Liu VX, Iwashyna TJ, et al.
        Assessment of clinical criteria for sepsis (Sepsis-3).
        JAMA. 2016;315(8):762-774. PMID: 26903335.

qSOFA is a rapid bedside prompt for patients with suspected infection who are at
higher risk of a poor outcome (in-hospital mortality or prolonged ICU stay). One
point each for respiratory rate >= 22/min, altered mentation (GCS < 15), and
systolic blood pressure <= 100 mmHg. A score >= 2 should prompt further
assessment for organ dysfunction; a score < 2 does not rule out sepsis.

Vitals are entered as raw values and the thresholds are applied internally. Not
a medical device; see DISCLAIMER.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskBand = Literal["lower_risk", "higher_risk"]


@dataclass(frozen=True)
class QsofaFeatures:
    """Inputs for qSOFA.

    Attributes:
        respiratory_rate_per_minute: Respiratory rate. Scores 1 if >= 22.
        glasgow_coma_scale: Glasgow Coma Scale (3-15). Scores 1 for altered
            mentation (< 15).
        systolic_bp_mmhg: Systolic blood pressure in mmHg. Scores 1 if <= 100.
    """

    respiratory_rate_per_minute: int
    glasgow_coma_scale: int
    systolic_bp_mmhg: int


@dataclass(frozen=True)
class QsofaResult:
    """qSOFA assessment result.

    Attributes:
        score: Total qSOFA score, range 0 to 3.
        contributing_factors: Labels of the criteria that scored.
        risk_band: "higher_risk" (score >= 2) or "lower_risk".
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be interpreted
            with care.
        citations: Source short tags.
    """

    score: int
    contributing_factors: tuple[str, ...]
    risk_band: RiskBand
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "qSOFA is a prognostic prompt for patients with suspected infection, not a "
    "diagnosis of sepsis. A score < 2 does not rule out sepsis or organ "
    "dysfunction.",
    "A score >= 2 should prompt assessment for organ dysfunction (e.g. full "
    "SOFA, lactate) and consideration of escalation; it is not itself a "
    "treatment trigger.",
    "Apply in the context of suspected or confirmed infection; the score has "
    "limited value outside that setting.",
)


def _check(features: QsofaFeatures) -> None:
    if features.respiratory_rate_per_minute < 0:
        raise ValueError("respiratory_rate_per_minute must not be negative")
    if not 3 <= features.glasgow_coma_scale <= 15:
        raise ValueError("glasgow_coma_scale must be between 3 and 15")
    if features.systolic_bp_mmhg < 0:
        raise ValueError("systolic_bp_mmhg must not be negative")


def qsofa_contributing_factors(features: QsofaFeatures) -> tuple[str, ...]:
    """Return labels of the qSOFA criteria that scored."""
    _check(features)
    factors: list[str] = []
    if features.respiratory_rate_per_minute >= 22:
        factors.append(f"respiratory rate >= 22 ({features.respiratory_rate_per_minute}/min)")
    if features.glasgow_coma_scale < 15:
        factors.append(f"altered mentation (GCS {features.glasgow_coma_scale})")
    if features.systolic_bp_mmhg <= 100:
        factors.append(f"systolic BP <= 100 ({features.systolic_bp_mmhg} mmHg)")
    return tuple(factors)


def qsofa_score(features: QsofaFeatures) -> int:
    """Compute the qSOFA score, range 0 to 3."""
    return len(qsofa_contributing_factors(features))


def qsofa_assessment(features: QsofaFeatures) -> QsofaResult:
    """Compute qSOFA and its risk band.

    Args:
        features: Vitals and GCS. See `QsofaFeatures`.

    Returns:
        A `QsofaResult`.

    Raises:
        ValueError: If a value is out of range.
    """
    factors = qsofa_contributing_factors(features)
    score = len(factors)
    citations = ("Singer 2016", "Seymour 2016")

    if score >= 2:
        return QsofaResult(
            score=score,
            contributing_factors=factors,
            risk_band="higher_risk",
            recommended_action=(
                "Higher risk of a poor outcome. In a patient with suspected "
                "infection, assess for organ dysfunction (full SOFA, lactate) "
                "and consider escalation of care."
            ),
            rationale="A qSOFA score of 2 or more identifies higher risk of in-hospital mortality or prolonged ICU stay.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return QsofaResult(
        score=score,
        contributing_factors=factors,
        risk_band="lower_risk",
        recommended_action=(
            "Lower risk by qSOFA, but a score below 2 does not rule out sepsis "
            "or organ dysfunction. Continue clinical assessment and reassess."
        ),
        rationale="A qSOFA score below 2 does not identify higher risk, and does not exclude sepsis.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
