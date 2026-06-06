"""Alvarado score (MANTRELS) for the probability of acute appendicitis.

References:
    Alvarado A.
        A practical score for the early diagnosis of acute appendicitis.
        Ann Emerg Med. 1986;15(5):557-564. PMID: 3963537.
    Ohle R, O'Reilly F, O'Brien KK, Fahey T, Dimitrov BD.
        The Alvarado score for predicting acute appendicitis: a systematic
        review. BMC Med. 2011;9:139. PMID: 22204638.
    Samuel M.
        Pediatric appendicitis score. J Pediatr Surg. 2002;37(6):877-881.
        PMID: 12037754.

The Alvarado score stratifies the probability of acute appendicitis in
patients presenting with suspected appendicitis, using eight clinical and
laboratory findings (the MANTRELS mnemonic) for a total of 0 to 10. It
supports decisions about imaging, surgical consultation, and discharge; it
does not diagnose appendicitis.

The two laboratory/vital findings and the neutrophil shift are computed from
raw measured values, using Canadian/SI units: temperature in degrees Celsius,
white cell count in 10^9/L, and neutrophils as a percentage.

This is a risk-stratification aid, not a diagnosis and not a substitute for
serial examination, imaging, and clinical judgement. See DISCLAIMER.md at the
repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskBand = Literal["low", "moderate", "high"]

# Thresholds from Alvarado 1986.
_ELEVATED_TEMPERATURE_CELSIUS = 37.3
_LEUKOCYTOSIS_X10E9_PER_L = 10.0
_LEFT_SHIFT_NEUTROPHIL_PERCENT = 75.0


@dataclass(frozen=True)
class AlvaradoFeatures:
    """Clinical and laboratory features for the Alvarado score.

    The five clinical findings are booleans. The temperature, white cell
    count, and neutrophil percentage are raw measured values, so their
    thresholds are applied in one auditable place.

    Attributes:
        migration_of_pain_to_rlq: Migration of pain to the right lower
            quadrant. +1.
        anorexia: Anorexia (or ketones in the urine). +1.
        nausea_or_vomiting: Nausea or vomiting. +1.
        tenderness_in_rlq: Tenderness in the right lower quadrant. +2.
        rebound_tenderness: Rebound tenderness. +1.
        temperature_celsius: Body temperature in degrees Celsius. Scores +1
            for elevated temperature (>= 37.3 C).
        white_cell_count_x10e9_per_l: White cell count in 10^9/L. Scores +2
            for leukocytosis (> 10.0).
        neutrophil_percent: Neutrophils as a percentage of white cells.
            Scores +1 for a left shift (> 75%).
    """

    migration_of_pain_to_rlq: bool
    anorexia: bool
    nausea_or_vomiting: bool
    tenderness_in_rlq: bool
    rebound_tenderness: bool
    temperature_celsius: float
    white_cell_count_x10e9_per_l: float
    neutrophil_percent: float


@dataclass(frozen=True)
class AlvaradoResult:
    """Alvarado assessment result.

    Attributes:
        score: Total Alvarado score, range 0 to 10.
        contributing_factors: Human-readable labels for each component that
            scored, with the points awarded.
        risk_band: "low" (<= 4), "moderate" (5-6), or "high" (>= 7).
        recommended_disposition: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be
            interpreted with care.
        citations: Source short tags.
    """

    score: int
    contributing_factors: tuple[str, ...]
    risk_band: RiskBand
    recommended_disposition: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "The Alvarado score predicts the probability of acute appendicitis; it "
    "does not diagnose it. Diagnosis rests on imaging, operative findings, or "
    "histology, and the score does not replace serial examination or clinical "
    "judgement.",
    "Derived predominantly in adults. Performance differs in children, where a "
    "pediatric-specific score (Samuel 2002) is often preferred.",
    "Specificity is lower in women of reproductive age because gynecologic "
    "conditions mimic appendicitis; imaging is frequently required regardless "
    "of score.",
    "Uses Canadian/SI units: temperature in degrees Celsius, white cell count "
    "in 10^9/L, neutrophils as a percentage. Convert before use if local "
    "results are reported in degrees Fahrenheit or cells/microlitre.",
)


def _check_values(features: AlvaradoFeatures) -> None:
    if features.temperature_celsius < 0:
        raise ValueError("temperature_celsius must not be negative")
    if features.white_cell_count_x10e9_per_l < 0:
        raise ValueError("white_cell_count_x10e9_per_l must not be negative")
    if not 0 <= features.neutrophil_percent <= 100:
        raise ValueError("neutrophil_percent must be between 0 and 100")


def _elevated_temperature(features: AlvaradoFeatures) -> bool:
    return features.temperature_celsius >= _ELEVATED_TEMPERATURE_CELSIUS


def _leukocytosis(features: AlvaradoFeatures) -> bool:
    return features.white_cell_count_x10e9_per_l > _LEUKOCYTOSIS_X10E9_PER_L


def _left_shift(features: AlvaradoFeatures) -> bool:
    return features.neutrophil_percent > _LEFT_SHIFT_NEUTROPHIL_PERCENT


def alvarado_components(features: AlvaradoFeatures) -> tuple[str, ...]:
    """Return human-readable labels for each component that scored points.

    Args:
        features: Clinical and laboratory features. See `AlvaradoFeatures`.

    Returns:
        A tuple of labels, each including the points awarded.

    Raises:
        ValueError: If a measured value is out of range.
    """
    _check_values(features)
    factors: list[str] = []
    if features.migration_of_pain_to_rlq:
        factors.append("migration of pain to RLQ (+1)")
    if features.anorexia:
        factors.append("anorexia (+1)")
    if features.nausea_or_vomiting:
        factors.append("nausea or vomiting (+1)")
    if features.tenderness_in_rlq:
        factors.append("tenderness in RLQ (+2)")
    if features.rebound_tenderness:
        factors.append("rebound tenderness (+1)")
    if _elevated_temperature(features):
        factors.append(
            f"elevated temperature {features.temperature_celsius} C (+1)"
        )
    if _leukocytosis(features):
        factors.append(
            f"leukocytosis {features.white_cell_count_x10e9_per_l} x10^9/L (+2)"
        )
    if _left_shift(features):
        factors.append(
            f"left shift {features.neutrophil_percent}% neutrophils (+1)"
        )
    return tuple(factors)


def alvarado_score(features: AlvaradoFeatures) -> int:
    """Compute the Alvarado score, range 0 to 10.

    Args:
        features: Clinical and laboratory features. See `AlvaradoFeatures`.

    Returns:
        The integer Alvarado score.

    Raises:
        ValueError: If a measured value is out of range.
    """
    _check_values(features)
    score = 0
    if features.migration_of_pain_to_rlq:
        score += 1
    if features.anorexia:
        score += 1
    if features.nausea_or_vomiting:
        score += 1
    if features.tenderness_in_rlq:
        score += 2
    if features.rebound_tenderness:
        score += 1
    if _elevated_temperature(features):
        score += 1
    if _leukocytosis(features):
        score += 2
    if _left_shift(features):
        score += 1
    return score


def alvarado_assessment(features: AlvaradoFeatures) -> AlvaradoResult:
    """Compute the Alvarado score and its risk-banded disposition.

    Args:
        features: Clinical and laboratory features. See `AlvaradoFeatures`.

    Returns:
        An `AlvaradoResult`.

    Raises:
        ValueError: If a measured value is out of range.
    """
    score = alvarado_score(features)
    factors = alvarado_components(features)
    citations = ("Alvarado 1986", "Ohle 2011")

    if score <= 4:
        return AlvaradoResult(
            score=score,
            contributing_factors=factors,
            risk_band="low",
            recommended_disposition=(
                "Low probability of appendicitis. Consider alternative diagnoses; "
                "active observation or discharge with safety-netting may be "
                "appropriate depending on the overall clinical picture."
            ),
            rationale="An Alvarado score of 4 or less indicates a low probability of acute appendicitis.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    if score <= 6:
        return AlvaradoResult(
            score=score,
            contributing_factors=factors,
            risk_band="moderate",
            recommended_disposition=(
                "Intermediate probability. Further evaluation is warranted: "
                "imaging (ultrasound first-line in children and women of "
                "reproductive age, otherwise CT) and/or active observation with "
                "serial examination."
            ),
            rationale="An Alvarado score of 5 to 6 indicates an intermediate probability of acute appendicitis.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return AlvaradoResult(
        score=score,
        contributing_factors=factors,
        risk_band="high",
        recommended_disposition=(
            "High probability of appendicitis. Surgical consultation is "
            "warranted; imaging may still be used per local pathways, "
            "particularly in women of reproductive age."
        ),
        rationale="An Alvarado score of 7 or more indicates a high probability of acute appendicitis.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
