"""Canadian CT Head Rule for CT imaging after minor head injury.

References:
    Stiell IG, Wells GA, Vandemheen K, et al.
        The Canadian CT Head Rule for patients with minor head injury.
        Lancet. 2001;357(9266):1391-1396. PMID: 11356436.
    Stiell IG, Clement CM, Rowe BH, et al.
        Comparison of the Canadian CT Head Rule and the New Orleans Criteria
        in patients with minor head injury. JAMA. 2005;294(12):1511-1518.
        PMID: 16189364.

The Canadian CT Head Rule identifies which adults with minor head injury need
CT of the head. CT is required if **any** of seven factors is present: five
high-risk factors (which predict the need for neurosurgical intervention) and
two medium-risk factors (which add detection of clinically important brain
injury on CT).

The rule applies to minor head injury — witnessed loss of consciousness,
definite amnesia, or witnessed disorientation — with an initial emergency-
department GCS of 13-15 and injury within the past 24 hours. It does not apply
to several excluded groups (see the population caveats). It supports, and does
not replace, clinical judgement. See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanadianCtHeadFeatures:
    """Factors for the Canadian CT Head Rule.

    Attributes:
        gcs_below_15_at_2_hours: GCS less than 15 at 2 hours after injury.
            High-risk factor.
        suspected_open_or_depressed_skull_fracture: Suspected open or depressed
            skull fracture. High-risk factor.
        sign_of_basal_skull_fracture: Any sign of basal skull fracture
            (hemotympanum, raccoon eyes, CSF otorrhea or rhinorrhea, Battle's
            sign). High-risk factor.
        vomiting_2_or_more_episodes: Two or more episodes of vomiting.
            High-risk factor.
        age_65_or_older: Age 65 years or older. High-risk factor.
        retrograde_amnesia_30_min_or_more: Retrograde amnesia to the event of
            30 minutes or more (amnesia before impact). Medium-risk factor.
        dangerous_mechanism: A dangerous mechanism — pedestrian struck by a
            motor vehicle, an occupant ejected from a motor vehicle, or a fall
            from an elevation of 3 or more feet or 5 stairs. Medium-risk factor.
    """

    gcs_below_15_at_2_hours: bool
    suspected_open_or_depressed_skull_fracture: bool
    sign_of_basal_skull_fracture: bool
    vomiting_2_or_more_episodes: bool
    age_65_or_older: bool
    retrograde_amnesia_30_min_or_more: bool
    dangerous_mechanism: bool


@dataclass(frozen=True)
class CanadianCtHeadResult:
    """Canadian CT Head Rule assessment result.

    Attributes:
        ct_indicated: True if any high- or medium-risk factor is present.
        high_risk_factors_present: Labels of the high-risk factors present
            (predict need for neurosurgical intervention).
        medium_risk_factors_present: Labels of the medium-risk factors present
            (predict clinically important brain injury on CT).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Inclusion and exclusion conditions.
        citations: Source short tags.
    """

    ct_indicated: bool
    high_risk_factors_present: tuple[str, ...]
    medium_risk_factors_present: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_HIGH_RISK_LABELS: dict[str, str] = {
    "gcs_below_15_at_2_hours": "GCS < 15 at 2 hours after injury",
    "suspected_open_or_depressed_skull_fracture": "suspected open or depressed skull fracture",
    "sign_of_basal_skull_fracture": "sign of basal skull fracture",
    "vomiting_2_or_more_episodes": "vomiting >= 2 episodes",
    "age_65_or_older": "age 65 or older",
}
_MEDIUM_RISK_LABELS: dict[str, str] = {
    "retrograde_amnesia_30_min_or_more": "retrograde amnesia >= 30 minutes",
    "dangerous_mechanism": "dangerous mechanism",
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "Applies to minor head injury — witnessed loss of consciousness, definite "
    "amnesia, or witnessed disorientation — with an initial ED GCS of 13-15 and "
    "injury within the past 24 hours.",
    "Does not apply to patients under 16 years of age.",
    "Does not apply to patients on oral anticoagulants or with a bleeding "
    "disorder.",
    "Does not apply to non-traumatic cases, GCS < 13, an obvious open skull "
    "fracture, a post-traumatic seizure, a focal neurologic deficit, unstable "
    "vital signs, or pregnancy; these were excluded from the derivation.",
    "The five high-risk factors target the need for neurosurgical intervention; "
    "the two medium-risk factors add detection of clinically important brain "
    "injury. The rule supports but does not replace clinical judgement.",
)


def _present(features: CanadianCtHeadFeatures, labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(label for attr, label in labels.items() if getattr(features, attr))


def canadian_ct_head_assessment(
    features: CanadianCtHeadFeatures,
) -> CanadianCtHeadResult:
    """Apply the Canadian CT Head Rule.

    Args:
        features: Factors. See `CanadianCtHeadFeatures`.

    Returns:
        A `CanadianCtHeadResult`. `ct_indicated` is True if any factor is present.
    """
    citations = ("Stiell 2001",)
    high_risk = _present(features, _HIGH_RISK_LABELS)
    medium_risk = _present(features, _MEDIUM_RISK_LABELS)

    if high_risk:
        return CanadianCtHeadResult(
            ct_indicated=True,
            high_risk_factors_present=high_risk,
            medium_risk_factors_present=medium_risk,
            recommended_action=(
                "CT head is indicated. A high-risk factor is present, predicting "
                "risk of requiring neurosurgical intervention."
            ),
            rationale="At least one high-risk Canadian CT Head Rule factor is present.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    if medium_risk:
        return CanadianCtHeadResult(
            ct_indicated=True,
            high_risk_factors_present=(),
            medium_risk_factors_present=medium_risk,
            recommended_action=(
                "CT head is indicated. A medium-risk factor is present, "
                "predicting clinically important brain injury on CT."
            ),
            rationale="At least one medium-risk Canadian CT Head Rule factor is present.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return CanadianCtHeadResult(
        ct_indicated=False,
        high_risk_factors_present=(),
        medium_risk_factors_present=(),
        recommended_action=(
            "No Canadian CT Head Rule factor is present; CT is not required by "
            "the rule. Apply clinical judgement and the rule's exclusions."
        ),
        rationale="No high- or medium-risk Canadian CT Head Rule factor is present.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
