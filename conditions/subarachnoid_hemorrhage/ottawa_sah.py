"""Ottawa Subarachnoid Hemorrhage (SAH) Rule for acute headache.

References:
    Perry JJ, Stiell IG, Sivilotti MLA, et al.
        Clinical decision rules to rule out subarachnoid hemorrhage for acute
        headache. JAMA. 2013;310(12):1248-1255. PMID: 24065011.
    Perry JJ, Sivilotti MLA, Stiell IG, et al.
        Validation of the Ottawa Subarachnoid Hemorrhage Rule in patients with
        acute headache. CMAJ. 2017;189(45):E1379-E1385. PMID: 29133539.

The Ottawa SAH Rule is a highly sensitive rule-out tool for subarachnoid
hemorrhage in alert (GCS 15) patients 15 years or older with a new severe
non-traumatic headache reaching maximum intensity within 1 hour. If **any** of
six criteria is present, SAH cannot be excluded by the rule and further
investigation is warranted. If none is present, SAH is effectively ruled out.

The rule applies only to its defined population (see `SahApplicability`). It is
deliberately high-sensitivity and low-specificity: a negative rule reliably
excludes SAH, but a positive rule does **not** mean SAH is present — most
positive patients will not have SAH, and the decision to image rests on clinical
judgement.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SahApplicability:
    """Whether the Ottawa SAH Rule applies to this patient.

    The rule applies only when all three inclusion conditions are True and none
    of the three exclusions is True.

    Attributes:
        new_severe_atraumatic_headache_peaking_within_1_hour: New, severe,
            non-traumatic headache reaching maximum intensity within 1 hour.
            Inclusion condition.
        alert_gcs_15: Patient is alert with a Glasgow Coma Scale of 15.
            Inclusion condition.
        age_15_or_older: Age 15 years or older. Inclusion condition.
        new_neurologic_deficit: A new neurologic deficit. Exclusion.
        prior_aneurysm_sah_or_brain_tumor: Known prior aneurysm, previous
            subarachnoid hemorrhage, or known brain tumor. Exclusion.
        chronic_recurrent_headache: Chronic recurrent headaches (at least 3
            episodes of the same character and intensity over more than 6
            months). Exclusion.
    """

    new_severe_atraumatic_headache_peaking_within_1_hour: bool
    alert_gcs_15: bool
    age_15_or_older: bool
    new_neurologic_deficit: bool
    prior_aneurysm_sah_or_brain_tumor: bool
    chronic_recurrent_headache: bool


@dataclass(frozen=True)
class SahFeatures:
    """The six Ottawa SAH Rule criteria.

    Each is a *positive finding*; investigation is warranted if any is True.

    Attributes:
        age_40_or_older: Age 40 years or older.
        neck_pain_or_stiffness: Complaint of neck pain or stiffness.
        witnessed_loss_of_consciousness: Witnessed loss of consciousness.
        onset_during_exertion: Headache onset during exertion.
        thunderclap_headache: Thunderclap headache (instantly peaking pain).
        limited_neck_flexion_on_exam: Limited neck flexion on examination
            (inability to touch chin to chest or raise the head 8 cm off the bed
            when supine).
    """

    age_40_or_older: bool
    neck_pain_or_stiffness: bool
    witnessed_loss_of_consciousness: bool
    onset_during_exertion: bool
    thunderclap_headache: bool
    limited_neck_flexion_on_exam: bool


@dataclass(frozen=True)
class SahResult:
    """Ottawa SAH Rule assessment result.

    Attributes:
        rule_applicable: True if the rule applies to this patient.
        investigation_indicated: True if any criterion is present, False if none
            is present, or None if the rule does not apply.
        positive_criteria: Labels of the criteria that are present.
        inapplicability_reasons: Why the rule does not apply (empty if it does).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the rule must be interpreted
            with care.
        citations: Source short tags.
    """

    rule_applicable: bool
    investigation_indicated: bool | None
    positive_criteria: tuple[str, ...]
    inapplicability_reasons: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_CRITERIA_LABELS: dict[str, str] = {
    "age_40_or_older": "age 40 or older",
    "neck_pain_or_stiffness": "neck pain or stiffness",
    "witnessed_loss_of_consciousness": "witnessed loss of consciousness",
    "onset_during_exertion": "onset during exertion",
    "thunderclap_headache": "thunderclap headache",
    "limited_neck_flexion_on_exam": "limited neck flexion on exam",
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "Applies only to alert (GCS 15) patients 15 years or older with a new "
    "severe non-traumatic headache reaching maximum intensity within 1 hour.",
    "Highly sensitive but low specificity (about 100% sensitivity, 15% "
    "specificity). A negative rule reliably excludes SAH; a positive rule does "
    "not mean SAH is present, and most positive patients will not have it.",
    "A positive rule indicates SAH cannot be excluded clinically; the decision "
    "to image (CT, and lumbar puncture or CT angiography as indicated) rests on "
    "clinical judgement.",
    "Does not apply to new neurologic deficit, prior aneurysm / SAH / brain "
    "tumor, or chronic recurrent headache; these were excluded from the "
    "derivation.",
)


def sah_positive_criteria(features: SahFeatures) -> tuple[str, ...]:
    """Return labels of the criteria that are present."""
    return tuple(
        label for attr, label in _CRITERIA_LABELS.items() if getattr(features, attr)
    )


def sah_inapplicability_reasons(applicability: SahApplicability) -> tuple[str, ...]:
    """Return reasons the rule does not apply (empty tuple if it applies)."""
    reasons: list[str] = []
    if not applicability.new_severe_atraumatic_headache_peaking_within_1_hour:
        reasons.append(
            "headache does not meet inclusion (new, severe, non-traumatic, "
            "peak intensity within 1 hour)"
        )
    if not applicability.alert_gcs_15:
        reasons.append("not alert (GCS < 15)")
    if not applicability.age_15_or_older:
        reasons.append("age under 15")
    if applicability.new_neurologic_deficit:
        reasons.append("new neurologic deficit")
    if applicability.prior_aneurysm_sah_or_brain_tumor:
        reasons.append("prior aneurysm, SAH, or brain tumor")
    if applicability.chronic_recurrent_headache:
        reasons.append("chronic recurrent headache")
    return tuple(reasons)


def ottawa_sah_assessment(
    features: SahFeatures,
    applicability: SahApplicability,
) -> SahResult:
    """Apply the Ottawa SAH Rule.

    Args:
        features: The six criteria. See `SahFeatures`.
        applicability: Inclusion and exclusion factors. See `SahApplicability`.

    Returns:
        A `SahResult`.
    """
    citations = ("Perry 2013", "Perry 2017")
    reasons = sah_inapplicability_reasons(applicability)

    if reasons:
        return SahResult(
            rule_applicable=False,
            investigation_indicated=None,
            positive_criteria=(),
            inapplicability_reasons=reasons,
            recommended_action=(
                "The Ottawa SAH Rule does not apply to this patient. Use "
                "clinical judgement and standard headache evaluation."
            ),
            rationale="The patient falls outside the rule's validated population.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    positive = sah_positive_criteria(features)

    if positive:
        return SahResult(
            rule_applicable=True,
            investigation_indicated=True,
            positive_criteria=positive,
            inapplicability_reasons=(),
            recommended_action=(
                "One or more criteria are present; subarachnoid hemorrhage "
                "cannot be excluded by the rule. Investigate further per "
                "clinical judgement (CT head, and lumbar puncture or CT "
                "angiography as indicated)."
            ),
            rationale="At least one Ottawa SAH Rule criterion is present.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return SahResult(
        rule_applicable=True,
        investigation_indicated=False,
        positive_criteria=(),
        inapplicability_reasons=(),
        recommended_action=(
            "No criteria are present. The rule classifies subarachnoid "
            "hemorrhage as effectively excluded. Apply clinical judgement."
        ),
        rationale="No Ottawa SAH Rule criterion is present in an eligible patient.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
