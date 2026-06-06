"""Canadian C-Spine Rule for cervical-spine imaging in alert, stable trauma.

Reference:
    Stiell IG, Wells GA, Vandemheen KL, et al.
        The Canadian C-Spine Rule for radiography in alert and stable trauma
        patients. JAMA. 2001;286(15):1841-1848. PMID: 11597285.

The Canadian C-Spine Rule (CCR) is a three-step algorithm for deciding whether
cervical-spine radiography is required after blunt trauma in patients who are
alert (GCS 15) and stable:

    1. Is there a high-risk factor that mandates radiography?
       (age >= 65, a dangerous mechanism, or paresthesias in the extremities)
       -> if yes, imaging is required.
    2. Is there a low-risk factor that allows safe assessment of range of
       motion? (simple rear-end MVC, sitting position in the ED, ambulatory at
       any time, delayed onset of neck pain, or absence of midline cervical
       tenderness) -> if none, imaging is required.
    3. Is the patient able to actively rotate the neck 45 degrees left and
       right? -> if unable, imaging is required; if able, imaging is not
       required.

A "dangerous mechanism" includes a fall from >= 1 metre or 5 stairs; an axial
load to the head (e.g., diving); a high-speed motor-vehicle collision
(> 100 km/h), rollover, or ejection; a motorized recreational-vehicle crash; or
a bicycle collision. A "simple rear-end MVC" excludes being pushed into oncoming
traffic, being hit by a bus or large truck, a rollover, or being hit by a
high-speed vehicle.

See the population caveats and DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DeterminingStep = Literal[
    "high_risk_factor",
    "no_low_risk_factor",
    "unable_to_rotate",
    "rule_satisfied",
]


@dataclass(frozen=True)
class CanadianCSpineFeatures:
    """Inputs for the Canadian C-Spine Rule.

    Attributes:
        age_65_or_older: Age 65 years or older. High-risk factor.
        dangerous_mechanism: A dangerous mechanism of injury (fall >= 1 m or 5
            stairs; axial load to the head; high-speed MVC > 100 km/h,
            rollover, or ejection; motorized recreational-vehicle crash; or
            bicycle collision). High-risk factor.
        paresthesias_in_extremities: Paresthesias in the extremities. High-risk
            factor.
        simple_rear_end_mvc: A simple rear-end motor-vehicle collision
            (excluding being pushed into oncoming traffic, hit by a bus or
            large truck, a rollover, or hit by a high-speed vehicle).
            Low-risk factor.
        sitting_position_in_ed: Sitting position in the emergency department.
            Low-risk factor.
        ambulatory_at_any_time: Ambulatory at any time since the injury.
            Low-risk factor.
        delayed_onset_of_neck_pain: Neck pain that was not immediate (delayed
            onset). Low-risk factor.
        absence_of_midline_c_spine_tenderness: No midline cervical-spine
            tenderness. Low-risk factor.
        able_to_rotate_neck_45_degrees: Able to actively rotate the neck 45
            degrees to the left and right. Assessed only if reached step 3.
    """

    age_65_or_older: bool
    dangerous_mechanism: bool
    paresthesias_in_extremities: bool
    simple_rear_end_mvc: bool
    sitting_position_in_ed: bool
    ambulatory_at_any_time: bool
    delayed_onset_of_neck_pain: bool
    absence_of_midline_c_spine_tenderness: bool
    able_to_rotate_neck_45_degrees: bool


@dataclass(frozen=True)
class CanadianCSpineResult:
    """Canadian C-Spine Rule assessment result.

    Attributes:
        imaging_indicated: True if cervical-spine radiography is required.
        determining_step: Which step decided the outcome —
            "high_risk_factor", "no_low_risk_factor", "unable_to_rotate", or
            "rule_satisfied".
        high_risk_factors_present: Labels of the high-risk factors present.
        low_risk_factors_present: Labels of the low-risk factors present.
        rotation_assessed: True if step 3 (active rotation) was reached.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the rule must not be applied
            or must be interpreted with care.
        citations: Source short tags.
    """

    imaging_indicated: bool
    determining_step: DeterminingStep
    high_risk_factors_present: tuple[str, ...]
    low_risk_factors_present: tuple[str, ...]
    rotation_assessed: bool
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_HIGH_RISK_LABELS: dict[str, str] = {
    "age_65_or_older": "age 65 or older",
    "dangerous_mechanism": "dangerous mechanism",
    "paresthesias_in_extremities": "paresthesias in extremities",
}
_LOW_RISK_LABELS: dict[str, str] = {
    "simple_rear_end_mvc": "simple rear-end MVC",
    "sitting_position_in_ed": "sitting position in ED",
    "ambulatory_at_any_time": "ambulatory at any time",
    "delayed_onset_of_neck_pain": "delayed onset of neck pain",
    "absence_of_midline_c_spine_tenderness": "absence of midline C-spine tenderness",
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "Applies only to alert (GCS 15) and stable adult patients with blunt "
    "trauma in whom cervical-spine injury is a concern.",
    "Does not apply to patients under 16 years of age.",
    "Does not apply to penetrating trauma, unstable vital signs, a reduced "
    "level of consciousness (GCS < 15), acute paralysis, known vertebral "
    "disease, or previous cervical-spine surgery.",
    "The rule supports but does not replace clinical judgement; the mechanism "
    "and low-risk definitions require clinical interpretation.",
)


def _present(features: CanadianCSpineFeatures, labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(label for attr, label in labels.items() if getattr(features, attr))


def canadian_c_spine_assessment(
    features: CanadianCSpineFeatures,
) -> CanadianCSpineResult:
    """Apply the Canadian C-Spine Rule.

    Args:
        features: Inputs. See `CanadianCSpineFeatures`.

    Returns:
        A `CanadianCSpineResult`.
    """
    citations = ("Stiell 2001",)
    high_risk = _present(features, _HIGH_RISK_LABELS)
    low_risk = _present(features, _LOW_RISK_LABELS)

    # Step 1: any high-risk factor mandates radiography.
    if high_risk:
        return CanadianCSpineResult(
            imaging_indicated=True,
            determining_step="high_risk_factor",
            high_risk_factors_present=high_risk,
            low_risk_factors_present=low_risk,
            rotation_assessed=False,
            recommended_action=(
                "A high-risk factor is present; cervical-spine radiography is "
                "indicated. Do not test range of motion."
            ),
            rationale="Step 1: a high-risk factor mandates radiography.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    # Step 2: a low-risk factor must be present to allow safe ROM assessment.
    if not low_risk:
        return CanadianCSpineResult(
            imaging_indicated=True,
            determining_step="no_low_risk_factor",
            high_risk_factors_present=(),
            low_risk_factors_present=(),
            rotation_assessed=False,
            recommended_action=(
                "No low-risk factor is present to permit safe assessment of "
                "range of motion; cervical-spine radiography is indicated."
            ),
            rationale="Step 2: no low-risk factor is present, so range of motion cannot be safely assessed.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    # Step 3: active rotation of 45 degrees left and right.
    if not features.able_to_rotate_neck_45_degrees:
        return CanadianCSpineResult(
            imaging_indicated=True,
            determining_step="unable_to_rotate",
            high_risk_factors_present=(),
            low_risk_factors_present=low_risk,
            rotation_assessed=True,
            recommended_action=(
                "The patient is unable to actively rotate the neck 45 degrees "
                "left and right; cervical-spine radiography is indicated."
            ),
            rationale="Step 3: the patient cannot actively rotate the neck 45 degrees left and right.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return CanadianCSpineResult(
        imaging_indicated=False,
        determining_step="rule_satisfied",
        high_risk_factors_present=(),
        low_risk_factors_present=low_risk,
        rotation_assessed=True,
        recommended_action=(
            "No high-risk factor, at least one low-risk factor, and the patient "
            "can actively rotate the neck 45 degrees left and right; "
            "cervical-spine radiography is not required by the Canadian C-Spine "
            "Rule."
        ),
        rationale="No high-risk factor, a low-risk factor present, and active rotation of 45 degrees is possible.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
