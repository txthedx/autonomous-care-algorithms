"""HEART score for chest pain in the emergency department.

References:
    Six AJ, Backus BE, Kelder JC.
        Chest pain in the emergency room: value of the HEART score.
        Neth Heart J. 2008;16(6):191-196. PMID: 18665203.
    Backus BE, Six AJ, Kelder JC, et al.
        A prospective validation of the HEART score for chest pain
        patients at the emergency department.
        Int J Cardiol. 2013;168(3):2153-2158. PMID: 23465250.
    Mahler SA, Riley RF, Hiestand BC, et al.
        The HEART Pathway randomized trial: identifying emergency
        department patients with acute chest pain for early discharge.
        Circ Cardiovasc Qual Outcomes. 2015;8(2):195-203. PMID: 25737484.

The HEART score stratifies adults presenting to the emergency department
with chest pain by their short-term (6-week) risk of a major adverse
cardiac event (MACE: all-cause death, acute myocardial infarction, or
coronary revascularization). It is a risk-stratification aid, not a
diagnosis of acute coronary syndrome.

It does not apply to patients with ST-elevation myocardial infarction,
hemodynamic instability, or an obvious non-cardiac cause of chest pain,
all of whom are managed independently of the score.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HistoryLevel = Literal[
    "slightly_suspicious",
    "moderately_suspicious",
    "highly_suspicious",
]
EcgLevel = Literal[
    "normal",
    "nonspecific_repolarization_disturbance",
    "significant_st_deviation",
]
TroponinLevel = Literal[
    "at_or_below_normal_limit",
    "one_to_three_times_normal_limit",
    "above_three_times_normal_limit",
]
RiskBand = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class HeartFeatures:
    """Clinical features for the HEART score.

    The History, ECG, and Troponin components are clinician judgements
    expressed as named levels. Age is a raw value. The Risk-factor
    component is derived from the individual cardiovascular risk factors
    and any history of established atherosclerotic disease, rather than
    asking the caller to pre-count, so the mapping is auditable.

    Attributes:
        history: Clinical suspicion from the history. "slightly_suspicious"
            (+0), "moderately_suspicious" (+1), or "highly_suspicious" (+2).
        ecg: Resting 12-lead ECG. "normal" (+0),
            "nonspecific_repolarization_disturbance" (+1, e.g. LBBB,
            LVH, repolarization changes, digoxin effect), or
            "significant_st_deviation" (+2).
        age_years: Patient age in years. <45 (+0), 45-64 (+1), >=65 (+2).
        hypertension: Treated or documented hypertension. Risk factor.
        hypercholesterolemia: Treated or documented hypercholesterolemia.
            Risk factor.
        diabetes_mellitus: Diabetes mellitus. Risk factor.
        current_or_recent_smoking: Current smoking, or smoking cessation
            within the past 90 days. Risk factor.
        family_history_of_cad: Family history of coronary artery disease.
            Risk factor.
        obesity_bmi_over_30: Obesity (BMI > 30). Risk factor.
        history_of_atherosclerotic_disease: Established atherosclerotic
            disease (prior MI, PCI or CABG, stroke or TIA, or peripheral
            arterial disease). When True, the Risk-factor component scores
            +2 regardless of the individual risk-factor count.
        troponin: Cardiac troponin relative to the local assay's 99th-
            percentile upper reference limit. "at_or_below_normal_limit"
            (+0), "one_to_three_times_normal_limit" (+1), or
            "above_three_times_normal_limit" (+2).
    """

    history: HistoryLevel
    ecg: EcgLevel
    age_years: int
    hypertension: bool
    hypercholesterolemia: bool
    diabetes_mellitus: bool
    current_or_recent_smoking: bool
    family_history_of_cad: bool
    obesity_bmi_over_30: bool
    history_of_atherosclerotic_disease: bool
    troponin: TroponinLevel


@dataclass(frozen=True)
class HeartComponentScores:
    """Per-component point breakdown for the HEART score.

    Attributes:
        history: History component points (0-2).
        ecg: ECG component points (0-2).
        age: Age component points (0-2).
        risk_factors: Risk-factor component points (0-2).
        troponin: Troponin component points (0-2).
    """

    history: int
    ecg: int
    age: int
    risk_factors: int
    troponin: int


@dataclass(frozen=True)
class HeartResult:
    """HEART score result.

    Attributes:
        score: Total HEART score, range 0 to 10.
        components: Per-component point breakdown.
        risk_band: "low" (0-3), "moderate" (4-6), or "high" (7-10).
        estimated_6_week_mace_band: Approximate 6-week MACE risk from the
            Backus 2013 validation cohort.
        recommended_disposition: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the score does not apply
            or must be interpreted with care.
        citations: Source short tags.
    """

    score: int
    components: HeartComponentScores
    risk_band: RiskBand
    estimated_6_week_mace_band: str
    recommended_disposition: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_HISTORY_POINTS: dict[str, int] = {
    "slightly_suspicious": 0,
    "moderately_suspicious": 1,
    "highly_suspicious": 2,
}
_ECG_POINTS: dict[str, int] = {
    "normal": 0,
    "nonspecific_repolarization_disturbance": 1,
    "significant_st_deviation": 2,
}
_TROPONIN_POINTS: dict[str, int] = {
    "at_or_below_normal_limit": 0,
    "one_to_three_times_normal_limit": 1,
    "above_three_times_normal_limit": 2,
}
_RISK_FACTOR_FIELDS: tuple[str, ...] = (
    "hypertension",
    "hypercholesterolemia",
    "diabetes_mellitus",
    "current_or_recent_smoking",
    "family_history_of_cad",
    "obesity_bmi_over_30",
)

_POPULATION_CAVEATS: tuple[str, ...] = (
    "Derived and validated in adults presenting to the emergency department "
    "with chest pain; it does not apply to ST-elevation myocardial infarction, "
    "hemodynamic instability, or an obvious non-cardiac cause.",
    "The troponin component must be calibrated to the local assay's "
    "99th-percentile upper reference limit. High-sensitivity troponin "
    "pathways (e.g., ESC 0/1-hour algorithms) may outperform a single value.",
    "The HEART score predicts short-term MACE; it does not diagnose acute "
    "coronary syndrome and does not replace serial troponin or clinical judgement.",
    "A low score (0-3) is typically not sufficient for discharge on its own. "
    "Validated early-discharge pathways pair it with serial troponin "
    "(e.g., the HEART Pathway, Mahler 2015).",
)


def _age_points(age_years: int) -> int:
    if age_years < 45:
        return 0
    if age_years <= 64:
        return 1
    return 2


def _risk_factor_points(features: HeartFeatures) -> int:
    if features.history_of_atherosclerotic_disease:
        return 2
    count = sum(1 for field in _RISK_FACTOR_FIELDS if getattr(features, field))
    if count == 0:
        return 0
    if count <= 2:
        return 1
    return 2


def heart_component_scores(features: HeartFeatures) -> HeartComponentScores:
    """Return the per-component point breakdown for the HEART score.

    Args:
        features: Clinical features. See `HeartFeatures`.

    Returns:
        A `HeartComponentScores`.

    Raises:
        ValueError: If `age_years` is negative.
    """
    if features.age_years < 0:
        raise ValueError("age_years must not be negative")
    return HeartComponentScores(
        history=_HISTORY_POINTS[features.history],
        ecg=_ECG_POINTS[features.ecg],
        age=_age_points(features.age_years),
        risk_factors=_risk_factor_points(features),
        troponin=_TROPONIN_POINTS[features.troponin],
    )


def heart_score(features: HeartFeatures) -> int:
    """Compute the total HEART score, range 0 to 10.

    Args:
        features: Clinical features. See `HeartFeatures`.

    Returns:
        The integer HEART score.

    Raises:
        ValueError: If `age_years` is negative.
    """
    components = heart_component_scores(features)
    return (
        components.history
        + components.ecg
        + components.age
        + components.risk_factors
        + components.troponin
    )


def heart_assessment(features: HeartFeatures) -> HeartResult:
    """Compute the HEART score and its risk-banded disposition.

    Args:
        features: Clinical features. See `HeartFeatures`.

    Returns:
        A `HeartResult`.

    Raises:
        ValueError: If `age_years` is negative.
    """
    components = heart_component_scores(features)
    score = (
        components.history
        + components.ecg
        + components.age
        + components.risk_factors
        + components.troponin
    )
    citations = ("Six 2008", "Backus 2013")

    if score <= 3:
        return HeartResult(
            score=score,
            components=components,
            risk_band="low",
            estimated_6_week_mace_band="approximately 1.7% (Backus 2013)",
            recommended_disposition=(
                "Low risk. Reasonable for early discharge with timely outpatient "
                "follow-up, ideally within a validated serial-troponin pathway "
                "(e.g., the HEART Pathway). Apply local protocols and shared "
                "decision-making."
            ),
            rationale="HEART score of 3 or less corresponds to the low-risk band.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    if score <= 6:
        return HeartResult(
            score=score,
            components=components,
            risk_band="moderate",
            estimated_6_week_mace_band="approximately 16.6% (Backus 2013)",
            recommended_disposition=(
                "Moderate risk. Admit or place in observation for serial troponin "
                "and further risk stratification (non-invasive testing or "
                "inpatient evaluation per local protocol)."
            ),
            rationale="HEART score of 4 to 6 inclusive corresponds to the moderate-risk band.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return HeartResult(
        score=score,
        components=components,
        risk_band="high",
        estimated_6_week_mace_band="approximately 50.1% (Backus 2013)",
        recommended_disposition=(
            "High risk. Admit; involve cardiology and consider an early invasive "
            "strategy in line with acute coronary syndrome management."
        ),
        rationale="HEART score of 7 or more corresponds to the high-risk band.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
