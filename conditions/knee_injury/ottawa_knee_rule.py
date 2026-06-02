"""Ottawa Knee Rule for selective radiography in acute knee injury.

References:
    Stiell IG, Greenberg GH, Wells GA, et al.
        Derivation of a decision rule for the use of radiography in acute
        knee injuries. Ann Emerg Med. 1995;26(4):405-413. PMID: 7574121.
    Stiell IG, Greenberg GH, Wells GA, et al.
        Prospective validation of a decision rule for the use of radiography
        in acute knee injuries. JAMA. 1996;275(8):611-615. PMID: 8594242.
    Bachmann LM, Haberzeth S, Steurer J, ter Riet G.
        The accuracy of the Ottawa knee rule to rule out knee fractures: a
        systematic review. Ann Intern Med. 2004;140(2):121-124.
        PMID: 14734335.

The Ottawa Knee Rule is sensitive but not specific. A positive result is
an indication for radiography; it does not diagnose a fracture. The rule
was derived in adults and should not be applied to children or patients
with the other excluding factors enumerated in `ApplicabilityFactors`.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OttawaKneeFeatures:
    """Clinical findings for the Ottawa Knee Rule.

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
        isolated_patellar_tenderness: Bone tenderness of the patella that
            is the only bony tender point on examination of the knee. If
            other bone tenderness is also present, this criterion is not
            met (but the other tenderness, if at the fibular head, is
            captured by `tender_fibular_head`).
        tender_fibular_head: Bone tenderness at the head of the fibula.
        unable_to_flex_to_90_degrees: Inability to actively flex the
            affected knee to 90 degrees.
        unable_to_bear_weight_immediately_and_now: Inability to bear weight
            (four steps, with or without a limp) both immediately after
            injury and at presentation.
    """

    age_years: int
    isolated_patellar_tenderness: bool
    tender_fibular_head: bool
    unable_to_flex_to_90_degrees: bool
    unable_to_bear_weight_immediately_and_now: bool


@dataclass(frozen=True)
class ApplicabilityFactors:
    """Factors that take a patient out of the validated population.

    Attributes:
        age_under_18: Patient is under 18 years of age.
        isolated_skin_injury: An isolated skin injury without bony concern.
        gross_deformity: Gross deformity of the knee.
        decreased_consciousness: Decreased level of consciousness.
        paraplegia_or_multiple_injuries: Paraplegia or multiple injuries.
        re_presentation_more_than_7_days: Re-presentation more than 7 days
            after the initial injury.
    """

    age_under_18: bool
    isolated_skin_injury: bool
    gross_deformity: bool
    decreased_consciousness: bool
    paraplegia_or_multiple_injuries: bool
    re_presentation_more_than_7_days: bool


@dataclass(frozen=True)
class OttawaKneeResult:
    """Result of an Ottawa Knee Rule assessment.

    Attributes:
        rule_applies: True if the rule applies (no applicability factors
            present); False if any excluding factor is present.
        excluded_by: Names of any applicability factors triggering exclusion.
        imaging_indicated: True if at least one positive criterion is met.
            False if `rule_applies` is False.
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
    "isolated_skin_injury": "isolated skin injury",
    "gross_deformity": "gross deformity",
    "decreased_consciousness": "decreased consciousness",
    "paraplegia_or_multiple_injuries": "paraplegia or multiple injuries",
    "re_presentation_more_than_7_days": "re-presentation more than 7 days after injury",
}


def _exclusions_present(applicability: ApplicabilityFactors) -> tuple[str, ...]:
    return tuple(
        label
        for attr, label in _APPLICABILITY_LABELS.items()
        if getattr(applicability, attr)
    )


def _validate(features: OttawaKneeFeatures) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")


def ottawa_knee_assessment(
    features: OttawaKneeFeatures,
    applicability: ApplicabilityFactors,
) -> OttawaKneeResult:
    """Apply the Ottawa Knee Rule.

    Args:
        features: Clinical findings. See `OttawaKneeFeatures`.
        applicability: Applicability factors. See `ApplicabilityFactors`.

    Returns:
        An `OttawaKneeResult` describing whether the rule applies and, if
        so, whether knee radiography is indicated.

    Raises:
        ValueError: If `age_years` is negative.
    """
    _validate(features)

    excluded_by = _exclusions_present(applicability)
    citations = ("Stiell 1995", "Stiell 1996", "Bachmann 2004")

    if excluded_by:
        return OttawaKneeResult(
            rule_applies=False,
            excluded_by=excluded_by,
            imaging_indicated=False,
            indicating_criteria=(),
            recommended_action=(
                "The Ottawa Knee Rule does not apply in this patient. "
                "Use clinical judgment and consider imaging based on the specific clinical context. "
                "For pediatric patients, the Pittsburgh Knee Rules are a validated alternative."
            ),
            rationale="One or more excluding factors are present; the rule was not validated in this population.",
            citations=citations,
        )

    indicating: list[str] = []
    if features.age_years >= 55:
        indicating.append("age >= 55 years")
    if features.isolated_patellar_tenderness:
        indicating.append("isolated patellar tenderness")
    if features.tender_fibular_head:
        indicating.append("tenderness at head of fibula")
    if features.unable_to_flex_to_90_degrees:
        indicating.append("inability to flex knee to 90 degrees")
    if features.unable_to_bear_weight_immediately_and_now:
        indicating.append("inability to bear weight (four steps) both immediately and now")

    if indicating:
        return OttawaKneeResult(
            rule_applies=True,
            excluded_by=(),
            imaging_indicated=True,
            indicating_criteria=tuple(indicating),
            recommended_action=(
                "Knee radiography is indicated by the Ottawa Knee Rule. "
                "A negative radiograph does not exclude all soft tissue injury (ligament, meniscal, or tendinous); "
                "treat clinically and arrange appropriate follow-up."
            ),
            rationale="At least one Ottawa Knee criterion is positive.",
            citations=citations,
        )

    return OttawaKneeResult(
        rule_applies=True,
        excluded_by=(),
        imaging_indicated=False,
        indicating_criteria=(),
        recommended_action=(
            "Knee radiography is not indicated by the Ottawa Knee Rule. "
            "Treat soft tissue injury clinically; reassess if symptoms worsen or do not resolve on the expected trajectory."
        ),
        rationale="No Ottawa Knee criterion is positive.",
        citations=citations,
    )
