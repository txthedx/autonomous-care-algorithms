"""San Francisco Syncope Rule (SFSR, CHESS) for short-term serious outcomes.

References:
    Quinn JV, Stiell IG, McDermott DA, Sellers KL, Kohn MA, Wells GA.
        Derivation of the San Francisco Syncope Rule to predict patients with
        short-term serious outcomes. Ann Emerg Med. 2004;43(2):224-232.
        PMID: 14747812.
    Quinn J, McDermott D, Stiell I, Kohn M, Wells G.
        Prospective validation of the San Francisco Syncope Rule to predict
        patients with serious outcomes. Ann Emerg Med. 2006;47(5):448-454.
        PMID: 16631985.
    Sun BC, Mangione CM, Merchant G, et al.
        External validation of the San Francisco Syncope Rule.
        Ann Emerg Med. 2007;49(4):420-427. PMID: 17210201.
    Birnbaum A, Esses D, Bijur P, Wollowitz A, Gallagher EJ.
        Failure to validate the San Francisco Syncope Rule in an independent
        emergency department population. Ann Emerg Med. 2008;52(2):151-159.
        PMID: 18282636.

The SFSR identifies patients presenting with syncope or near-syncope who are at
risk of a short-term serious outcome (death, myocardial infarction, arrhythmia,
pulmonary embolism, stroke, subarachnoid hemorrhage, significant hemorrhage, or
a return ED visit and admission for a related event). It is a binary rule: if
**any** of the five CHESS criteria is present, the patient is high risk.

The rule applies to patients whose syncope is not clearly attributable to a
non-cardiac cause (e.g., seizure, intoxication, hypoglycemia). It is a screening
aid, not a discharge guarantee: independent external validations have reported
lower sensitivity than the original derivation.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskBand = Literal["low", "high"]

# Thresholds from Quinn 2004.
_HEMATOCRIT_THRESHOLD_PERCENT = 30.0
_SYSTOLIC_BP_THRESHOLD_MMHG = 90


@dataclass(frozen=True)
class SfsrFeatures:
    """Clinical features for the San Francisco Syncope Rule (CHESS).

    The two measured values (hematocrit and systolic blood pressure) are
    entered raw, so their thresholds are applied in one auditable place. The
    other three criteria are clinical judgements expressed as booleans.

    Attributes:
        congestive_heart_failure_history: History of congestive heart failure
            (the "C" criterion). Positive finding.
        hematocrit_percent: Hematocrit as a percentage (the "H" criterion).
            Positive when < 30%.
        abnormal_ecg: Abnormal ECG (the "E" criterion) — any new change or a
            non-sinus rhythm compared with a prior ECG when available.
            Positive finding.
        shortness_of_breath: Complaint of shortness of breath (the first "S"
            criterion). Positive finding.
        systolic_bp_mmhg: Systolic blood pressure at triage in mmHg (the
            second "S" criterion). Positive when < 90 mmHg.
    """

    congestive_heart_failure_history: bool
    hematocrit_percent: float
    abnormal_ecg: bool
    shortness_of_breath: bool
    systolic_bp_mmhg: int


@dataclass(frozen=True)
class SfsrResult:
    """San Francisco Syncope Rule assessment result.

    Attributes:
        high_risk: True if any CHESS criterion is present.
        positive_criteria: Labels of the criteria that are present.
        risk_band: "high" if any criterion is present, otherwise "low".
        recommended_disposition: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the rule must be
            interpreted with care.
        citations: Source short tags.
    """

    high_risk: bool
    positive_criteria: tuple[str, ...]
    risk_band: RiskBand
    recommended_disposition: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "Predicts short-term serious outcomes (death, myocardial infarction, "
    "arrhythmia, pulmonary embolism, stroke, subarachnoid hemorrhage, "
    "significant hemorrhage, or a return ED visit and admission for a related "
    "event).",
    "The derivation reported about 96% sensitivity (Quinn 2004) and the "
    "authors' prospective validation about 98% (Quinn 2006), but independent "
    "external validations have reported lower sensitivity (Sun 2007; Birnbaum "
    "2008). The rule is a screening aid, not a discharge guarantee.",
    "Applies to patients presenting with syncope or near-syncope; it does not "
    "apply to syncope clearly attributable to a non-cardiac cause such as "
    "seizure, intoxication, or hypoglycemia.",
    "Abnormal ECG means any new change or a non-sinus rhythm relative to a "
    "prior ECG when available, and requires clinical interpretation.",
    "Hematocrit is entered as a percentage; convert if local results are "
    "reported as a fraction (e.g., 0.30).",
)


def _check_values(features: SfsrFeatures) -> None:
    if not 0 <= features.hematocrit_percent <= 100:
        raise ValueError("hematocrit_percent must be between 0 and 100")
    if features.systolic_bp_mmhg < 0:
        raise ValueError("systolic_bp_mmhg must not be negative")


def sfsr_positive_criteria(features: SfsrFeatures) -> tuple[str, ...]:
    """Return labels of the CHESS criteria that are present.

    Args:
        features: Clinical features. See `SfsrFeatures`.

    Returns:
        A tuple of labels for each positive criterion (empty if none).

    Raises:
        ValueError: If a measured value is out of range.
    """
    _check_values(features)
    criteria: list[str] = []
    if features.congestive_heart_failure_history:
        criteria.append("history of congestive heart failure")
    if features.hematocrit_percent < _HEMATOCRIT_THRESHOLD_PERCENT:
        criteria.append(f"hematocrit < 30% ({features.hematocrit_percent}%)")
    if features.abnormal_ecg:
        criteria.append("abnormal ECG")
    if features.shortness_of_breath:
        criteria.append("shortness of breath")
    if features.systolic_bp_mmhg < _SYSTOLIC_BP_THRESHOLD_MMHG:
        criteria.append(
            f"systolic BP < 90 mmHg ({features.systolic_bp_mmhg} mmHg)"
        )
    return tuple(criteria)


def sfsr_assessment(features: SfsrFeatures) -> SfsrResult:
    """Apply the San Francisco Syncope Rule.

    Args:
        features: Clinical features. See `SfsrFeatures`.

    Returns:
        An `SfsrResult`. `high_risk` is True if any CHESS criterion is present.

    Raises:
        ValueError: If a measured value is out of range.
    """
    criteria = sfsr_positive_criteria(features)
    citations = ("Quinn 2004", "Quinn 2006")

    if criteria:
        return SfsrResult(
            high_risk=True,
            positive_criteria=criteria,
            risk_band="high",
            recommended_disposition=(
                "High risk for a short-term serious outcome. Admission or a "
                "period of monitored observation with further cardiac "
                "evaluation is warranted."
            ),
            rationale="At least one San Francisco Syncope Rule (CHESS) criterion is present.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return SfsrResult(
        high_risk=False,
        positive_criteria=(),
        risk_band="low",
        recommended_disposition=(
            "No CHESS criteria are present. The rule classifies this as low "
            "risk for a short-term serious outcome, and outpatient evaluation "
            "may be considered. The rule is a screening aid, not a discharge "
            "guarantee; apply clinical judgement, and note that external "
            "validations have reported lower sensitivity than the derivation."
        ),
        rationale="No San Francisco Syncope Rule (CHESS) criterion is present.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
