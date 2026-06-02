"""Ottawa Ankle and Foot Rules for selective radiography in acute injury.

References:
    Stiell IG, Greenberg GH, McKnight RD, Nair RC, McDowell I, Worthington JR.
        A study to develop clinical decision rules for the use of radiography
        in acute ankle injuries. Ann Emerg Med. 1992;21(4):384-390.
        PMID: 1554175.
    Stiell IG, McKnight RD, Greenberg GH, et al.
        Implementation of the Ottawa ankle rules.
        JAMA. 1993;269(9):1127-1132. PMID: 8433468.
    Stiell IG, McKnight RD, Greenberg GH, et al.
        Decision rules for the use of radiography in acute ankle injuries.
        Refinement and prospective validation. JAMA. 1993;269(9):1127-1132.
    Bachmann LM, Kolb E, Koller MT, Steurer J, ter Riet G.
        Accuracy of Ottawa ankle rules to exclude fractures of the ankle and
        mid-foot: systematic review. BMJ. 2003;326(7386):417. PMID: 12595378.

The Ottawa Rules are sensitive but not specific. A positive result is an
indication for radiography; it does not diagnose a fracture. The rules were
derived in adult patients and should not be applied to children, intoxicated
patients, or patients with the other excluding factors enumerated in
`ApplicabilityFactors`.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnkleAssessmentFeatures:
    """Findings for the Ottawa Ankle Rule.

    Attributes:
        pain_in_malleolar_zone: Pain located around the medial or lateral
            malleolus.
        tender_lateral_malleolus_distal_6cm: Bone tenderness at the posterior
            edge or tip of the lateral malleolus, including the distal 6 cm.
        tender_medial_malleolus_distal_6cm: Bone tenderness at the posterior
            edge or tip of the medial malleolus, including the distal 6 cm.
        unable_to_bear_weight_immediately_and_now: Inability to bear weight
            (four steps) both immediately after injury and at presentation.
    """

    pain_in_malleolar_zone: bool
    tender_lateral_malleolus_distal_6cm: bool
    tender_medial_malleolus_distal_6cm: bool
    unable_to_bear_weight_immediately_and_now: bool


@dataclass(frozen=True)
class FootAssessmentFeatures:
    """Findings for the Ottawa Foot Rule.

    Attributes:
        pain_in_midfoot_zone: Pain located in the midfoot zone.
        tender_5th_metatarsal_base: Bone tenderness at the base of the
            fifth metatarsal.
        tender_navicular: Bone tenderness at the navicular bone.
        unable_to_bear_weight_immediately_and_now: Inability to bear weight
            (four steps) both immediately after injury and at presentation.
    """

    pain_in_midfoot_zone: bool
    tender_5th_metatarsal_base: bool
    tender_navicular: bool
    unable_to_bear_weight_immediately_and_now: bool


@dataclass(frozen=True)
class ApplicabilityFactors:
    """Factors that take a patient out of the validated population.

    Attributes:
        age_under_18: Patient is under 18 years of age.
        intoxication: Clinical intoxication.
        distracting_injury: A distracting injury elsewhere that may mask
            local tenderness or weight-bearing assessment.
        decreased_sensation_or_neurologic_deficit: Decreased sensation or
            focal neurologic deficit in the affected limb.
        gross_deformity: Gross deformity of the ankle or foot.
        isolated_skin_injury: An isolated skin injury without bony concern.
        head_injury_or_decreased_consciousness: Head injury or decreased
            level of consciousness.
    """

    age_under_18: bool
    intoxication: bool
    distracting_injury: bool
    decreased_sensation_or_neurologic_deficit: bool
    gross_deformity: bool
    isolated_skin_injury: bool
    head_injury_or_decreased_consciousness: bool


@dataclass(frozen=True)
class OttawaResult:
    """Result of an Ottawa rule assessment.

    Attributes:
        rule_applies: True if the rule applies (no applicability factors
            present); False if any excluding factor is present.
        excluded_by: Names of any applicability factors triggering exclusion.
        imaging_indicated: True if the relevant zone pain is present and at
            least one positive criterion is met. False if `rule_applies` is
            False (the rule does not determine imaging in that case).
        indicating_criteria: Names of the criteria that triggered imaging.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        citations: Source short tags.
    """

    rule_applies: bool
    excluded_by: tuple[str, ...]
    imaging_indicated: bool
    indicating_criteria: tuple[str, ...]
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


_APPLICABILITY_LABELS: dict[str, str] = {
    "age_under_18": "age under 18",
    "intoxication": "intoxication",
    "distracting_injury": "distracting injury",
    "decreased_sensation_or_neurologic_deficit": "decreased sensation or neurologic deficit",
    "gross_deformity": "gross deformity",
    "isolated_skin_injury": "isolated skin injury",
    "head_injury_or_decreased_consciousness": "head injury or decreased consciousness",
}


def _exclusions_present(applicability: ApplicabilityFactors) -> tuple[str, ...]:
    return tuple(
        label
        for attr, label in _APPLICABILITY_LABELS.items()
        if getattr(applicability, attr)
    )


def _rule_does_not_apply_result(
    excluded_by: tuple[str, ...],
    citations: tuple[str, ...],
) -> OttawaResult:
    return OttawaResult(
        rule_applies=False,
        excluded_by=excluded_by,
        imaging_indicated=False,
        indicating_criteria=(),
        recommended_action=(
            "The Ottawa rules do not apply in this patient. "
            "Use clinical judgment and consider imaging based on the specific clinical context."
        ),
        rationale="One or more excluding factors are present; the rule was not validated in this population.",
        citations=citations,
    )


def ottawa_ankle_assessment(
    features: AnkleAssessmentFeatures,
    applicability: ApplicabilityFactors,
) -> OttawaResult:
    """Apply the Ottawa Ankle Rule.

    Args:
        features: Clinical findings. See `AnkleAssessmentFeatures`.
        applicability: Applicability factors. See `ApplicabilityFactors`.

    Returns:
        An `OttawaResult` describing whether the rule applies and, if so,
        whether ankle radiography is indicated.
    """
    excluded_by = _exclusions_present(applicability)
    citations = ("Stiell 1992", "Stiell 1993", "Bachmann 2003")

    if excluded_by:
        return _rule_does_not_apply_result(excluded_by, citations)

    if not features.pain_in_malleolar_zone:
        return OttawaResult(
            rule_applies=True,
            excluded_by=(),
            imaging_indicated=False,
            indicating_criteria=(),
            recommended_action=(
                "Ankle radiography is not indicated by the Ottawa Ankle Rule. "
                "Reassess if pain develops in the malleolar zone."
            ),
            rationale="No pain in the malleolar zone; the rule does not indicate imaging.",
            citations=citations,
        )

    indicating: list[str] = []
    if features.tender_lateral_malleolus_distal_6cm:
        indicating.append("bone tenderness at lateral malleolus (distal 6 cm)")
    if features.tender_medial_malleolus_distal_6cm:
        indicating.append("bone tenderness at medial malleolus (distal 6 cm)")
    if features.unable_to_bear_weight_immediately_and_now:
        indicating.append("inability to bear weight (four steps) both immediately and now")

    if indicating:
        return OttawaResult(
            rule_applies=True,
            excluded_by=(),
            imaging_indicated=True,
            indicating_criteria=tuple(indicating),
            recommended_action=(
                "Ankle radiography is indicated by the Ottawa Ankle Rule. "
                "A negative radiograph does not exclude all soft tissue injury; "
                "treat clinically and arrange appropriate follow-up."
            ),
            rationale="Pain in the malleolar zone is present and at least one Ottawa Ankle criterion is positive.",
            citations=citations,
        )

    return OttawaResult(
        rule_applies=True,
        excluded_by=(),
        imaging_indicated=False,
        indicating_criteria=(),
        recommended_action=(
            "Ankle radiography is not indicated by the Ottawa Ankle Rule. "
            "Treat soft tissue injury clinically; reassess if symptoms worsen or do not resolve on the expected trajectory."
        ),
        rationale="Pain in the malleolar zone is present but no Ottawa Ankle criterion is positive.",
        citations=citations,
    )


def ottawa_foot_assessment(
    features: FootAssessmentFeatures,
    applicability: ApplicabilityFactors,
) -> OttawaResult:
    """Apply the Ottawa Foot Rule.

    Args:
        features: Clinical findings. See `FootAssessmentFeatures`.
        applicability: Applicability factors. See `ApplicabilityFactors`.

    Returns:
        An `OttawaResult` describing whether the rule applies and, if so,
        whether foot radiography is indicated.
    """
    excluded_by = _exclusions_present(applicability)
    citations = ("Stiell 1992", "Stiell 1993", "Bachmann 2003")

    if excluded_by:
        return _rule_does_not_apply_result(excluded_by, citations)

    if not features.pain_in_midfoot_zone:
        return OttawaResult(
            rule_applies=True,
            excluded_by=(),
            imaging_indicated=False,
            indicating_criteria=(),
            recommended_action=(
                "Foot radiography is not indicated by the Ottawa Foot Rule. "
                "Reassess if pain develops in the midfoot zone."
            ),
            rationale="No pain in the midfoot zone; the rule does not indicate imaging.",
            citations=citations,
        )

    indicating: list[str] = []
    if features.tender_5th_metatarsal_base:
        indicating.append("bone tenderness at base of 5th metatarsal")
    if features.tender_navicular:
        indicating.append("bone tenderness at navicular")
    if features.unable_to_bear_weight_immediately_and_now:
        indicating.append("inability to bear weight (four steps) both immediately and now")

    if indicating:
        return OttawaResult(
            rule_applies=True,
            excluded_by=(),
            imaging_indicated=True,
            indicating_criteria=tuple(indicating),
            recommended_action=(
                "Foot radiography is indicated by the Ottawa Foot Rule. "
                "A negative radiograph does not exclude all soft tissue injury; "
                "treat clinically and arrange appropriate follow-up."
            ),
            rationale="Pain in the midfoot zone is present and at least one Ottawa Foot criterion is positive.",
            citations=citations,
        )

    return OttawaResult(
        rule_applies=True,
        excluded_by=(),
        imaging_indicated=False,
        indicating_criteria=(),
        recommended_action=(
            "Foot radiography is not indicated by the Ottawa Foot Rule. "
            "Treat soft tissue injury clinically; reassess if symptoms worsen or do not resolve on the expected trajectory."
        ),
        rationale="Pain in the midfoot zone is present but no Ottawa Foot criterion is positive.",
        citations=citations,
    )
