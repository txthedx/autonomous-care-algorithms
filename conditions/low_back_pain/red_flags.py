"""Red flag screening for serious underlying pathology in low back pain.

References:
    Downie A, Williams CM, Henschke N, et al.
        Red flags to screen for malignancy and fracture in patients with low
        back pain: systematic review. BMJ. 2013;347:f7095. PMID: 24335669.
    Henschke N, Maher CG, Ostelo RW, de Vet HC, Macaskill P, Irwig L.
        Red flags to screen for malignancy in patients with low-back pain.
        Cochrane Database Syst Rev. 2013;(2):CD008686. PMID: 23450586.
    Verhagen AP, Downie A, Popal N, Maher C, Koes BW.
        Red flags presented in current low back pain guidelines: a review.
        Eur Spine J. 2016;25(9):2788-2802. PMID: 27376890.
    NICE Guideline NG59. Low back pain and sciatica in over 16s:
        assessment and management. 2016, updated 2020.

This module reports which red flags are present and assigns an urgency band.
It does not diagnose, prescribe, or replace clinical judgment.
See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RedFlagFeatures:
    """Explicit assessment of red flag features.

    All fields are required. A `False` value means the feature was assessed
    and not present. The module does not distinguish "not assessed" from
    "absent"; the assessing clinician is responsible for completeness.

    Attributes (cauda equina / emergency):
        saddle_anesthesia: Perineal or perianal sensory loss.
        new_urinary_retention: New urinary retention or overflow incontinence.
        new_fecal_incontinence: New fecal incontinence.
        bilateral_leg_weakness: Bilateral lower-extremity weakness.
        progressive_neurologic_deficit: Severe or progressive lower-extremity
            neurologic deficit.

    Attributes (malignancy or infection):
        history_of_cancer_with_new_pain: Known cancer history with new back pain.
        unexplained_weight_loss: Unexplained loss of body weight.
        pain_unrelieved_by_rest: Pain worse at night or not relieved by rest.
        fever: Fever associated with back pain.
        intravenous_drug_use: Recent or current intravenous drug use.
        immunosuppression: Immunocompromised state.
        recent_spinal_procedure_or_bacteremia: Recent spinal procedure or a
            known source of bacteremia.

    Attributes (fracture or otherwise concerning):
        significant_trauma: Significant trauma at any age.
        minor_trauma_with_osteoporosis_risk: Minor trauma in a patient with
            osteoporosis risk (age over 50, prolonged corticosteroid use,
            known osteoporosis).
        long_term_corticosteroid_use: Long-term systemic corticosteroid use.
        age_over_50_new_severe_pain: Age over 50 with new severe pain.
        age_under_18_significant_pain: Age under 18 with significant pain.
        no_improvement_after_4_to_6_weeks: Persistent symptoms without
            improvement after 4 to 6 weeks of conservative care.
    """

    saddle_anesthesia: bool
    new_urinary_retention: bool
    new_fecal_incontinence: bool
    bilateral_leg_weakness: bool
    progressive_neurologic_deficit: bool

    history_of_cancer_with_new_pain: bool
    unexplained_weight_loss: bool
    pain_unrelieved_by_rest: bool
    fever: bool
    intravenous_drug_use: bool
    immunosuppression: bool
    recent_spinal_procedure_or_bacteremia: bool

    significant_trauma: bool
    minor_trauma_with_osteoporosis_risk: bool
    long_term_corticosteroid_use: bool
    age_over_50_new_severe_pain: bool
    age_under_18_significant_pain: bool
    no_improvement_after_4_to_6_weeks: bool


@dataclass(frozen=True)
class RedFlagAssessment:
    """Structured red flag screen result.

    Attributes:
        emergency_flags: Cauda equina-suggestive features present.
        high_concern_flags: Malignancy or infection-suggestive features present.
        moderate_flags: Fracture-suggestive or otherwise concerning features present.
        recommended_urgency: Narrative urgency band.
        rationale: Short justification, including the known limitation that
            individual red flags often have high false-positive rates.
        citations: Source short tags. See references.bib for full entries.
    """

    emergency_flags: tuple[str, ...]
    high_concern_flags: tuple[str, ...]
    moderate_flags: tuple[str, ...]
    recommended_urgency: str
    rationale: str
    citations: tuple[str, ...]


_EMERGENCY_LABELS: dict[str, str] = {
    "saddle_anesthesia": "saddle anesthesia",
    "new_urinary_retention": "new urinary retention or overflow incontinence",
    "new_fecal_incontinence": "new fecal incontinence",
    "bilateral_leg_weakness": "bilateral leg weakness",
    "progressive_neurologic_deficit": "progressive lower-extremity neurologic deficit",
}

_HIGH_CONCERN_LABELS: dict[str, str] = {
    "history_of_cancer_with_new_pain": "history of cancer with new back pain",
    "unexplained_weight_loss": "unexplained weight loss",
    "pain_unrelieved_by_rest": "pain worse at night or unrelieved by rest",
    "fever": "fever with back pain",
    "intravenous_drug_use": "intravenous drug use",
    "immunosuppression": "immunosuppression",
    "recent_spinal_procedure_or_bacteremia": "recent spinal procedure or bacteremia source",
}

_MODERATE_LABELS: dict[str, str] = {
    "significant_trauma": "significant trauma",
    "minor_trauma_with_osteoporosis_risk": "minor trauma with osteoporosis risk",
    "long_term_corticosteroid_use": "long-term corticosteroid use",
    "age_over_50_new_severe_pain": "age over 50 with new severe pain",
    "age_under_18_significant_pain": "age under 18 with significant pain",
    "no_improvement_after_4_to_6_weeks": "no improvement after 4 to 6 weeks",
}


def _present(features: RedFlagFeatures, labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(label for attr, label in labels.items() if getattr(features, attr))


def red_flag_assessment(features: RedFlagFeatures) -> RedFlagAssessment:
    """Categorize red flag features and return an urgency band.

    Args:
        features: The clinical features. See `RedFlagFeatures`.

    Returns:
        A `RedFlagAssessment` listing flags by category and recommending an
        urgency band.
    """
    emergency = _present(features, _EMERGENCY_LABELS)
    high_concern = _present(features, _HIGH_CONCERN_LABELS)
    moderate = _present(features, _MODERATE_LABELS)

    if emergency:
        return RedFlagAssessment(
            emergency_flags=emergency,
            high_concern_flags=high_concern,
            moderate_flags=moderate,
            recommended_urgency=(
                "Same-day emergency assessment with MRI. "
                "Cauda equina syndrome is a surgical emergency; do not delay for completion of other workup."
            ),
            rationale="One or more features are suggestive of cauda equina syndrome.",
            citations=("NICE NG59", "Verhagen 2016"),
        )

    if high_concern:
        return RedFlagAssessment(
            emergency_flags=emergency,
            high_concern_flags=high_concern,
            moderate_flags=moderate,
            recommended_urgency=(
                "Urgent workup within days, including imaging and laboratory studies appropriate to the suspected etiology. "
                "Do not stratify with STarT Back."
            ),
            rationale="Features suggestive of malignancy or spinal infection are present; individual flags have low specificity, so the clinician must synthesize context.",
            citations=("Downie 2013", "Henschke 2013", "Verhagen 2016", "NICE NG59"),
        )

    if moderate:
        return RedFlagAssessment(
            emergency_flags=emergency,
            high_concern_flags=high_concern,
            moderate_flags=moderate,
            recommended_urgency=(
                "Targeted workup with short-interval follow-up. "
                "Once specific pathology is excluded, STarT Back stratification may apply."
            ),
            rationale="Moderate-concern features are present; isolated moderate flags in an otherwise well person carry low pretest probability of serious pathology and require clinical synthesis.",
            citations=("Downie 2013", "Verhagen 2016", "NICE NG59"),
        )

    return RedFlagAssessment(
        emergency_flags=emergency,
        high_concern_flags=high_concern,
        moderate_flags=moderate,
        recommended_urgency=(
            "No red flags identified. Proceed to STarT Back risk stratification for non-specific low back pain."
        ),
        rationale="No assessed red flag features are present.",
        citations=("NICE NG59",),
    )
