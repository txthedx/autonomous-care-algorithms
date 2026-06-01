"""HAS-BLED score for bleeding risk on antithrombotic therapy.

References:
    Pisters R, Lane DA, Nieuwlaat R, de Vos CB, Crijns HJ, Lip GY.
        A novel user-friendly score (HAS-BLED) to assess 1-year risk of
        major bleeding in patients with atrial fibrillation: the Euro Heart
        Survey. Chest. 2010;138(5):1093-1100. PMID: 20299623.
    Hindricks G, Potpara T, Dagres N, et al.
        2020 ESC Guidelines for the diagnosis and management of atrial
        fibrillation. Eur Heart J. 2021;42(5):373-498. PMID: 32860505.

Per ESC 2020: a high HAS-BLED score identifies modifiable bleeding risk
factors that should be addressed and indicates a need for closer
monitoring. It is **not** a tool to withhold anticoagulation in otherwise
eligible patients.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskBand = Literal["low_to_moderate", "high"]


@dataclass(frozen=True)
class HasBledFeatures:
    """Clinical features for HAS-BLED.

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
            Scores 1 point if greater than 65.
        uncontrolled_hypertension: Systolic blood pressure > 160 mmHg.
        abnormal_renal_function: Chronic dialysis, renal transplantation,
            or serum creatinine > 200 micromol/L.
        abnormal_liver_function: Chronic liver disease (e.g., cirrhosis) or
            biochemical evidence of significant hepatic derangement
            (bilirubin > 2x ULN with AST/ALT/ALP > 3x ULN).
        prior_stroke: Prior stroke.
        bleeding_history_or_predisposition: Previous major bleeding history
            or predisposition to bleeding (e.g., anemia).
        labile_inr: For warfarin therapy: time in therapeutic range
            (TTR) < 60%. Set to False if not on warfarin.
        on_drugs_predisposing_to_bleeding: Concurrent use of antiplatelet
            agents or NSAIDs.
        alcohol_use_8_or_more_units_per_week: Alcohol use of 8 or more
            units per week.
    """

    age_years: int
    uncontrolled_hypertension: bool
    abnormal_renal_function: bool
    abnormal_liver_function: bool
    prior_stroke: bool
    bleeding_history_or_predisposition: bool
    labile_inr: bool
    on_drugs_predisposing_to_bleeding: bool
    alcohol_use_8_or_more_units_per_week: bool


@dataclass(frozen=True)
class HasBledResult:
    """HAS-BLED score and management recommendation.

    Attributes:
        score: Total score, range 0 to 9.
        criteria_present: Tuple of component labels that contributed to the score.
        risk_band: "low_to_moderate" or "high".
        recommended_management: Narrative aligned with ESC 2020, including
            the explicit caveat that a high score should not be used to
            withhold anticoagulation.
        modifiable_factors_present: Tuple of modifiable component labels
            that are currently positive, per ESC 2020.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: int
    criteria_present: tuple[str, ...]
    risk_band: RiskBand
    recommended_management: str
    modifiable_factors_present: tuple[str, ...]
    rationale: str
    citations: tuple[str, ...]


_MODIFIABLE_FIELDS: dict[str, str] = {
    "uncontrolled_hypertension": "uncontrolled hypertension",
    "labile_inr": "labile INR (review warfarin management; consider DOAC)",
    "on_drugs_predisposing_to_bleeding": "concurrent antiplatelet or NSAID use",
    "alcohol_use_8_or_more_units_per_week": "alcohol use >= 8 units/week",
}


def _validate(features: HasBledFeatures) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")


def has_bled_criteria(features: HasBledFeatures) -> tuple[str, ...]:
    """Return labels of HAS-BLED components that contributed to the score."""
    _validate(features)
    present: list[str] = []
    if features.uncontrolled_hypertension:
        present.append("uncontrolled hypertension")
    if features.abnormal_renal_function:
        present.append("abnormal renal function")
    if features.abnormal_liver_function:
        present.append("abnormal liver function")
    if features.prior_stroke:
        present.append("prior stroke")
    if features.bleeding_history_or_predisposition:
        present.append("bleeding history or predisposition")
    if features.labile_inr:
        present.append("labile INR")
    if features.age_years > 65:
        present.append("age > 65")
    if features.on_drugs_predisposing_to_bleeding:
        present.append("drugs predisposing to bleeding")
    if features.alcohol_use_8_or_more_units_per_week:
        present.append("alcohol use >= 8 units/week")
    return tuple(present)


def has_bled_score(features: HasBledFeatures) -> int:
    """Compute the HAS-BLED score, range 0 to 9."""
    return len(has_bled_criteria(features))


def _modifiable_present(features: HasBledFeatures) -> tuple[str, ...]:
    return tuple(
        label for attr, label in _MODIFIABLE_FIELDS.items() if getattr(features, attr)
    )


def has_bled_assessment(features: HasBledFeatures) -> HasBledResult:
    """Return the HAS-BLED score, risk band, and ESC-aligned management note.

    Args:
        features: The clinical features. See `HasBledFeatures`.

    Returns:
        A `HasBledResult` with score, criteria present, risk band,
        management language, and the list of modifiable factors currently
        positive in this patient.
    """
    criteria = has_bled_criteria(features)
    score = len(criteria)
    modifiable = _modifiable_present(features)

    if score <= 2:
        band: RiskBand = "low_to_moderate"
        management = (
            "Low-to-moderate bleeding risk. Standard monitoring while on anticoagulation. "
            "Continue to address any modifiable factors."
        )
        rationale = "HAS-BLED of 2 or less indicates low-to-moderate bleeding risk."
    else:
        band = "high"
        management = (
            "High bleeding risk. Identify and address modifiable bleeding risk factors. "
            "Schedule closer follow-up. "
            "Per ESC 2020: do not withhold anticoagulation on the basis of HAS-BLED alone in otherwise eligible patients."
        )
        rationale = "HAS-BLED of 3 or more indicates high bleeding risk and warrants modifiable-factor review per ESC 2020."

    return HasBledResult(
        score=score,
        criteria_present=criteria,
        risk_band=band,
        recommended_management=management,
        modifiable_factors_present=modifiable,
        rationale=rationale,
        citations=("Pisters 2010", "ESC 2020"),
    )
