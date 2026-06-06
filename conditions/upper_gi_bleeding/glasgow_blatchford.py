"""Glasgow-Blatchford score (GBS) for upper gastrointestinal bleeding.

References:
    Blatchford O, Murray WR, Blatchford M.
        A risk score to predict need for treatment for upper-gastrointestinal
        haemorrhage. Lancet. 2000;356(9238):1318-1321. PMID: 11073021.
    Stanley AJ, Ashley D, Dalton HR, et al.
        Outpatient management of patients with low-risk upper-gastrointestinal
        haemorrhage: multicentre validation and prospective evaluation.
        Lancet. 2009;373(9657):42-47. PMID: 19091393.
    Stanley AJ, Laine L, Dalton HR, et al.
        Comparison of risk scoring systems for patients presenting with upper
        gastrointestinal bleeding: international multicentre prospective study.
        BMJ. 2017;356:i6432. PMID: 28053181.
    National Institute for Health and Care Excellence.
        Acute upper gastrointestinal bleeding in over 16s: management.
        Clinical guideline CG141. 2012 (updated 2016).

The GBS is a pre-endoscopy risk score that predicts the need for hospital-based
intervention (transfusion, endoscopic therapy, or surgery) or death in patients
presenting with upper gastrointestinal bleeding. Its principal validated use is
identifying very low-risk patients who may be managed as outpatients: a score of
0 is the most conservative threshold, and Stanley 2017 found a score of <= 1 to
be the optimum threshold for directing patients to outpatient management.

The score uses Canadian/SI units: blood urea in mmol/L and hemoglobin in g/L.
The hemoglobin component is sex-specific.

This is a risk-stratification aid, not a diagnosis or a substitute for clinical
judgement and timely endoscopy. See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Sex = Literal["male", "female"]
RiskBand = Literal["very_low", "intermediate", "high"]


@dataclass(frozen=True)
class GlasgowBlatchfordFeatures:
    """Clinical features for the Glasgow-Blatchford score.

    Attributes:
        sex: Patient sex, "male" or "female". Determines the hemoglobin bands.
        urea_mmol_per_l: Blood urea in mmol/L. Bands: 6.5-7.9 (+2),
            8.0-9.9 (+3), 10.0-24.9 (+4), >=25.0 (+6).
        hemoglobin_g_per_l: Hemoglobin in g/L. Men: 120-129 (+1),
            100-119 (+3), <100 (+6). Women: 100-119 (+1), <100 (+6).
        systolic_bp_mmhg: Systolic blood pressure in mmHg. 100-109 (+1),
            90-99 (+2), <90 (+3).
        pulse_per_minute: Heart rate in beats per minute. >=100 (+1).
        melena: Presentation with melena. +1.
        syncope: Presentation with syncope. +2.
        hepatic_disease: Known history of hepatic disease. +2.
        cardiac_failure: Known history of cardiac (heart) failure. +2.
    """

    sex: Sex
    urea_mmol_per_l: float
    hemoglobin_g_per_l: float
    systolic_bp_mmhg: int
    pulse_per_minute: int
    melena: bool
    syncope: bool
    hepatic_disease: bool
    cardiac_failure: bool


@dataclass(frozen=True)
class GlasgowBlatchfordResult:
    """Glasgow-Blatchford assessment result.

    Attributes:
        score: Total GBS, range 0 to 23.
        contributing_factors: Human-readable labels for each component that
            contributed points, with the points awarded.
        risk_band: "very_low" (0), "intermediate" (1-5), or "high" (>=6).
        outpatient_management_candidate: True when the score is 0, the most
            conservative validated discharge threshold.
        recommended_disposition: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be
            interpreted with care.
        citations: Source short tags.
    """

    score: int
    contributing_factors: tuple[str, ...]
    risk_band: RiskBand
    outpatient_management_candidate: bool
    recommended_disposition: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "The GBS predicts the need for hospital-based intervention or death; it "
    "does not diagnose the bleeding source and does not replace timely "
    "endoscopy or clinical judgement.",
    "Uses Canadian/SI units: urea in mmol/L and hemoglobin in g/L. Convert "
    "before use if local results are reported in mg/dL or g/dL.",
    "A score of 0 is the most conservative discharge threshold. Stanley 2017 "
    "found a score of <= 1 to be the optimum threshold for outpatient "
    "management; a score of 1 may be managed as an outpatient with clinical "
    "judgement and reliable follow-up.",
    "Derived and validated in adults (over 16s) presenting with upper "
    "gastrointestinal bleeding; it does not apply to lower GI bleeding or to "
    "hemodynamically unstable patients, who warrant immediate resuscitation "
    "regardless of score.",
)


def _check_non_negative(features: GlasgowBlatchfordFeatures) -> None:
    if features.urea_mmol_per_l < 0:
        raise ValueError("urea_mmol_per_l must not be negative")
    if features.hemoglobin_g_per_l < 0:
        raise ValueError("hemoglobin_g_per_l must not be negative")
    if features.systolic_bp_mmhg < 0:
        raise ValueError("systolic_bp_mmhg must not be negative")
    if features.pulse_per_minute < 0:
        raise ValueError("pulse_per_minute must not be negative")


def _urea_points(urea_mmol_per_l: float) -> int:
    if urea_mmol_per_l < 6.5:
        return 0
    if urea_mmol_per_l < 8.0:
        return 2
    if urea_mmol_per_l < 10.0:
        return 3
    if urea_mmol_per_l < 25.0:
        return 4
    return 6


def _hemoglobin_points(hemoglobin_g_per_l: float, sex: Sex) -> int:
    if sex == "male":
        if hemoglobin_g_per_l >= 130:
            return 0
        if hemoglobin_g_per_l >= 120:
            return 1
        if hemoglobin_g_per_l >= 100:
            return 3
        return 6
    # female
    if hemoglobin_g_per_l >= 120:
        return 0
    if hemoglobin_g_per_l >= 100:
        return 1
    return 6


def _systolic_bp_points(systolic_bp_mmhg: int) -> int:
    if systolic_bp_mmhg >= 110:
        return 0
    if systolic_bp_mmhg >= 100:
        return 1
    if systolic_bp_mmhg >= 90:
        return 2
    return 3


def glasgow_blatchford_components(
    features: GlasgowBlatchfordFeatures,
) -> tuple[str, ...]:
    """Return human-readable labels for each component that scored points.

    Args:
        features: Clinical features. See `GlasgowBlatchfordFeatures`.

    Returns:
        A tuple of labels, each including the points awarded.

    Raises:
        ValueError: If any measured value is negative.
    """
    _check_non_negative(features)
    factors: list[str] = []

    urea_points = _urea_points(features.urea_mmol_per_l)
    if urea_points:
        factors.append(
            f"blood urea {features.urea_mmol_per_l} mmol/L (+{urea_points})"
        )

    hb_points = _hemoglobin_points(features.hemoglobin_g_per_l, features.sex)
    if hb_points:
        factors.append(
            f"hemoglobin {features.hemoglobin_g_per_l} g/L, {features.sex} (+{hb_points})"
        )

    sbp_points = _systolic_bp_points(features.systolic_bp_mmhg)
    if sbp_points:
        factors.append(
            f"systolic BP {features.systolic_bp_mmhg} mmHg (+{sbp_points})"
        )

    if features.pulse_per_minute >= 100:
        factors.append(f"pulse {features.pulse_per_minute}/min >= 100 (+1)")
    if features.melena:
        factors.append("presentation with melena (+1)")
    if features.syncope:
        factors.append("presentation with syncope (+2)")
    if features.hepatic_disease:
        factors.append("hepatic disease (+2)")
    if features.cardiac_failure:
        factors.append("cardiac failure (+2)")

    return tuple(factors)


def glasgow_blatchford_score(features: GlasgowBlatchfordFeatures) -> int:
    """Compute the Glasgow-Blatchford score, range 0 to 23.

    Args:
        features: Clinical features. See `GlasgowBlatchfordFeatures`.

    Returns:
        The integer GBS.

    Raises:
        ValueError: If any measured value is negative.
    """
    _check_non_negative(features)
    score = (
        _urea_points(features.urea_mmol_per_l)
        + _hemoglobin_points(features.hemoglobin_g_per_l, features.sex)
        + _systolic_bp_points(features.systolic_bp_mmhg)
    )
    if features.pulse_per_minute >= 100:
        score += 1
    if features.melena:
        score += 1
    if features.syncope:
        score += 2
    if features.hepatic_disease:
        score += 2
    if features.cardiac_failure:
        score += 2
    return score


def glasgow_blatchford_assessment(
    features: GlasgowBlatchfordFeatures,
) -> GlasgowBlatchfordResult:
    """Compute the GBS and its risk-banded disposition.

    Args:
        features: Clinical features. See `GlasgowBlatchfordFeatures`.

    Returns:
        A `GlasgowBlatchfordResult`.

    Raises:
        ValueError: If any measured value is negative.
    """
    score = glasgow_blatchford_score(features)
    factors = glasgow_blatchford_components(features)
    citations = ("Blatchford 2000", "Stanley 2009", "Stanley 2017", "NICE CG141")

    if score == 0:
        return GlasgowBlatchfordResult(
            score=score,
            contributing_factors=factors,
            risk_band="very_low",
            outpatient_management_candidate=True,
            recommended_disposition=(
                "Very low risk. Outpatient management with early outpatient "
                "endoscopy may be considered, provided there is no other reason "
                "for admission and reliable follow-up is available."
            ),
            rationale="A Glasgow-Blatchford score of 0 is the most conservative validated threshold for outpatient management.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    if score <= 5:
        return GlasgowBlatchfordResult(
            score=score,
            contributing_factors=factors,
            risk_band="intermediate",
            outpatient_management_candidate=False,
            recommended_disposition=(
                "Admission is generally warranted for inpatient assessment and "
                "endoscopy. A score of 1 falls at the validated <= 1 outpatient "
                "threshold (Stanley 2017) and may be managed as an outpatient "
                "with clinical judgement and reliable follow-up."
            ),
            rationale="A Glasgow-Blatchford score of 1 to 5 indicates more than minimal risk of needing hospital-based intervention.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return GlasgowBlatchfordResult(
        score=score,
        contributing_factors=factors,
        risk_band="high",
        outpatient_management_candidate=False,
        recommended_disposition=(
            "Higher risk of needing hospital-based intervention. Admit, "
            "resuscitate as required, expedite endoscopy, and consider a "
            "higher-acuity setting."
        ),
        rationale="A Glasgow-Blatchford score of 6 or more indicates a substantial risk of needing transfusion, endoscopic therapy, or surgery.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
