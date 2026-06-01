"""Bent 2002 decision rule for acute uncomplicated cystitis in women.

References:
    Bent S, Nallamothu BK, Simel DL, Fihn SD, Saint S.
        Does this woman have an acute uncomplicated urinary tract infection?
        JAMA. 2002;287(20):2701-2710. PMID: 12020306.
    Gupta K, Hooton TM, Naber KG, et al.
        International clinical practice guidelines for the treatment of
        acute uncomplicated cystitis and pyelonephritis in women: A 2010
        update by the Infectious Diseases Society of America and the
        European Society for Microbiology and Infectious Diseases.
        Clin Infect Dis. 2011;52(5):e103-e120. PMID: 21292654.
    NICE Guideline NG109. Urinary tract infection (lower): antimicrobial
        prescribing. 2018.

This module applies to non-pregnant adult women with suspected acute
uncomplicated cystitis. It does not apply to men, pregnant patients,
children, catheterized patients, or any of the complicating factors
enumerated in `UtiComplicatingFactors`.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProbabilityBand = Literal[
    "not_applicable_complicated",
    "alternative_diagnoses_considered",
    "low",
    "intermediate",
    "high",
]


@dataclass(frozen=True)
class UtiPresentingFeatures:
    """Presenting symptoms used by the Bent rule.

    Attributes:
        dysuria: Pain or burning on urination.
        urinary_frequency: Increased urinary frequency.
        hematuria: Visible or reported blood in urine.
        suprapubic_or_back_pain: Suprapubic pain or low back pain.
        vaginal_discharge: Abnormal vaginal discharge.
        vaginal_irritation: Vaginal itching or irritation.
    """

    dysuria: bool
    urinary_frequency: bool
    hematuria: bool
    suprapubic_or_back_pain: bool
    vaginal_discharge: bool
    vaginal_irritation: bool


@dataclass(frozen=True)
class UtiComplicatingFactors:
    """Factors that take the patient out of the uncomplicated cystitis frame.

    Attributes:
        pregnancy: Currently pregnant.
        male: Male anatomy or assigned male at birth with intact urinary anatomy.
        diabetes_uncontrolled_or_immunocompromise: Uncontrolled diabetes or
            immunocompromised state.
        indwelling_catheter_or_recent_instrumentation: Indwelling urinary
            catheter or recent urinary tract instrumentation.
        known_urinary_tract_abnormality: Known anatomic or functional
            abnormality of the urinary tract.
        recent_antibiotic_use: Recent antibiotic exposure.
        symptoms_more_than_7_days: Symptom duration greater than 7 days.
        recurrent_uti: Three or more UTIs in 12 months, or two or more in
            6 months.
        flank_pain_or_fever_or_systemic_symptoms: Features suggesting
            pyelonephritis.
    """

    pregnancy: bool
    male: bool
    diabetes_uncontrolled_or_immunocompromise: bool
    indwelling_catheter_or_recent_instrumentation: bool
    known_urinary_tract_abnormality: bool
    recent_antibiotic_use: bool
    symptoms_more_than_7_days: bool
    recurrent_uti: bool
    flank_pain_or_fever_or_systemic_symptoms: bool


@dataclass(frozen=True)
class UtiAssessment:
    """Bent 2002 decision rule output.

    Attributes:
        is_complicated_pattern: True if any complicating factor is present.
        complicating_factors_present: Labels of complicating factors that
            are present.
        vaginal_symptoms_present: True if vaginal discharge or irritation
            is present.
        uti_symptom_count: Number of cardinal UTI symptoms (range 0 to 4).
        pretest_probability_band: One of "not_applicable_complicated",
            "alternative_diagnoses_considered", "low", "intermediate",
            or "high".
        recommended_action: Narrative recommendation aligned with Bent 2002
            and IDSA 2010.
        rationale: Short justification.
        citations: Source short tags.
    """

    is_complicated_pattern: bool
    complicating_factors_present: tuple[str, ...]
    vaginal_symptoms_present: bool
    uti_symptom_count: int
    pretest_probability_band: ProbabilityBand
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


_COMPLICATING_LABELS: dict[str, str] = {
    "pregnancy": "pregnancy",
    "male": "male sex",
    "diabetes_uncontrolled_or_immunocompromise": "uncontrolled diabetes or immunocompromise",
    "indwelling_catheter_or_recent_instrumentation": "indwelling catheter or recent instrumentation",
    "known_urinary_tract_abnormality": "known urinary tract abnormality",
    "recent_antibiotic_use": "recent antibiotic use",
    "symptoms_more_than_7_days": "symptoms more than 7 days",
    "recurrent_uti": "recurrent UTI pattern",
    "flank_pain_or_fever_or_systemic_symptoms": "flank pain, fever, or systemic symptoms (?pyelonephritis)",
}


def _complicating_factors_present(
    factors: UtiComplicatingFactors,
) -> tuple[str, ...]:
    return tuple(
        label for attr, label in _COMPLICATING_LABELS.items() if getattr(factors, attr)
    )


def _uti_symptom_count(symptoms: UtiPresentingFeatures) -> int:
    return sum(
        [
            int(symptoms.dysuria),
            int(symptoms.urinary_frequency),
            int(symptoms.hematuria),
            int(symptoms.suprapubic_or_back_pain),
        ]
    )


def uti_assessment(
    symptoms: UtiPresentingFeatures,
    factors: UtiComplicatingFactors,
) -> UtiAssessment:
    """Apply the Bent 2002 decision rule with the complicating-factors gate.

    Args:
        symptoms: Presenting symptoms. See `UtiPresentingFeatures`.
        factors: Complicating factors. See `UtiComplicatingFactors`.

    Returns:
        A `UtiAssessment` describing the pretest probability band and the
        recommended action.
    """
    complicating = _complicating_factors_present(factors)
    vaginal = symptoms.vaginal_discharge or symptoms.vaginal_irritation
    symptom_count = _uti_symptom_count(symptoms)

    if complicating:
        return UtiAssessment(
            is_complicated_pattern=True,
            complicating_factors_present=complicating,
            vaginal_symptoms_present=vaginal,
            uti_symptom_count=symptom_count,
            pretest_probability_band="not_applicable_complicated",
            recommended_action=(
                "The Bent decision rule does not apply. "
                "Obtain urine culture and pursue broader workup based on the complicating factor present. "
                "Consider pyelonephritis if flank pain, fever, or systemic symptoms; consider alternative diagnoses as indicated."
            ),
            rationale="One or more complicating factors take the patient out of the uncomplicated cystitis frame.",
            citations=("Bent 2002", "Gupta 2011", "NICE NG109"),
        )

    if vaginal:
        return UtiAssessment(
            is_complicated_pattern=False,
            complicating_factors_present=(),
            vaginal_symptoms_present=True,
            uti_symptom_count=symptom_count,
            pretest_probability_band="alternative_diagnoses_considered",
            recommended_action=(
                "Vaginal symptoms reduce the likelihood of UTI. "
                "Evaluate for vaginitis and sexually transmitted infections; pelvic examination is typically recommended. "
                "If UTI remains a concern after pelvic evaluation, obtain urinalysis or culture."
            ),
            rationale="Vaginal discharge or irritation has a negative likelihood ratio for UTI (Bent 2002).",
            citations=("Bent 2002",),
        )

    if symptom_count == 0:
        return UtiAssessment(
            is_complicated_pattern=False,
            complicating_factors_present=(),
            vaginal_symptoms_present=False,
            uti_symptom_count=0,
            pretest_probability_band="low",
            recommended_action=(
                "UTI is unlikely on history alone. Consider alternative causes for the presenting concern."
            ),
            rationale="No cardinal UTI symptoms reported.",
            citations=("Bent 2002",),
        )

    if symptom_count == 1:
        return UtiAssessment(
            is_complicated_pattern=False,
            complicating_factors_present=(),
            vaginal_symptoms_present=False,
            uti_symptom_count=1,
            pretest_probability_band="intermediate",
            recommended_action=(
                "Pretest probability is approximately 50%. "
                "Obtain urinalysis dipstick or urine culture; treat empirically if positive."
            ),
            rationale="A single cardinal symptom yields an intermediate pretest probability (Bent 2002).",
            citations=("Bent 2002", "Gupta 2011"),
        )

    return UtiAssessment(
        is_complicated_pattern=False,
        complicating_factors_present=(),
        vaginal_symptoms_present=False,
        uti_symptom_count=symptom_count,
        pretest_probability_band="high",
        recommended_action=(
            "Pretest probability is approximately 90%. "
            "Empirical treatment for acute uncomplicated cystitis is reasonable without dipstick or culture in most settings (IDSA 2010). "
            "Choose antibiotic per local resistance patterns. "
            "Reassess and culture if symptoms persist after treatment."
        ),
        rationale="Two or more cardinal symptoms without vaginal symptoms yields high pretest probability (Bent 2002).",
        citations=("Bent 2002", "Gupta 2011", "NICE NG109"),
    )
