"""CHA2DS2-VASc score for stroke risk in non-valvular atrial fibrillation.

References:
    Lip GY, Nieuwlaat R, Pisters R, Lane DA, Crijns HJ.
        Refining clinical risk stratification for predicting stroke and
        thromboembolism in atrial fibrillation using a novel risk
        factor-based approach: the Euro Heart Survey on atrial fibrillation.
        Chest. 2010;137(2):263-272. PMID: 19762550.
    Hindricks G, Potpara T, Dagres N, et al.
        2020 ESC Guidelines for the diagnosis and management of atrial
        fibrillation developed in collaboration with the European
        Association for Cardio-Thoracic Surgery (EACTS).
        Eur Heart J. 2021;42(5):373-498. PMID: 32860505.
    Andrade JG, Aguilar M, Atzema C, et al.
        The 2020 Canadian Cardiovascular Society/Canadian Heart Rhythm
        Society Comprehensive Guidelines for the Management of Atrial
        Fibrillation. Can J Cardiol. 2020;36(12):1847-1948.

This module applies to non-valvular atrial fibrillation. It does not apply
to patients with moderate-to-severe mitral stenosis or mechanical heart
valves, who require anticoagulation regardless of score.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Sex = Literal["male", "female"]


@dataclass(frozen=True)
class Cha2ds2VascFeatures:
    """Clinical features for CHA2DS2-VASc.

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
        sex: "male" or "female". The score was derived in cisgender
            populations; application to transgender and non-binary patients
            requires individualized clinical judgment.
        congestive_heart_failure: Symptomatic heart failure or
            moderate-to-severe LV dysfunction.
        hypertension: Treated hypertension or on antihypertensive therapy.
        diabetes: Diabetes mellitus.
        prior_stroke_tia_or_thromboembolism: Prior stroke, TIA, or systemic
            thromboembolism.
        vascular_disease: Prior myocardial infarction, peripheral arterial
            disease, or complex aortic plaque.
    """

    age_years: int
    sex: Sex
    congestive_heart_failure: bool
    hypertension: bool
    diabetes: bool
    prior_stroke_tia_or_thromboembolism: bool
    vascular_disease: bool


@dataclass(frozen=True)
class Cha2ds2VascResult:
    """CHA2DS2-VASc score and anticoagulation recommendation.

    Attributes:
        score: Total score, range 0 to 9.
        criteria_present: Tuple of "(label, points)" entries for components
            that contributed to the score.
        annual_stroke_risk_band: Approximate annual stroke risk from Lip 2010.
        recommended_anticoagulation: Narrative recommendation aligned with
            the ESC 2020 framing.
        rationale: Short justification.
        citations: Source short tags.
    """

    score: int
    criteria_present: tuple[tuple[str, int], ...]
    annual_stroke_risk_band: str
    recommended_anticoagulation: str
    rationale: str
    citations: tuple[str, ...]


_STROKE_RISK_BY_SCORE: dict[int, str] = {
    0: "approximately 0% per year (Lip 2010)",
    1: "approximately 1.3% per year (Lip 2010)",
    2: "approximately 2.2% per year (Lip 2010)",
    3: "approximately 3.2% per year (Lip 2010)",
    4: "approximately 4.0% per year (Lip 2010)",
    5: "approximately 6.7% per year (Lip 2010)",
    6: "approximately 9.8% per year (Lip 2010)",
    7: "approximately 9.6% per year (Lip 2010)",
    8: "approximately 6.7% per year (Lip 2010)",
    9: "approximately 15.2% per year (Lip 2010)",
}


def _validate(features: Cha2ds2VascFeatures) -> None:
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")
    if features.sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")


def cha2ds2_vasc_criteria(features: Cha2ds2VascFeatures) -> tuple[tuple[str, int], ...]:
    """Return labeled (component, points) entries that contributed to the score.

    Age 65 to 74 and Age >= 75 are mutually exclusive; the higher band
    supersedes when both could apply.
    """
    _validate(features)
    items: list[tuple[str, int]] = []
    if features.congestive_heart_failure:
        items.append(("congestive heart failure", 1))
    if features.hypertension:
        items.append(("hypertension", 1))
    if features.age_years >= 75:
        items.append(("age >= 75", 2))
    elif features.age_years >= 65:
        items.append(("age 65-74", 1))
    if features.diabetes:
        items.append(("diabetes", 1))
    if features.prior_stroke_tia_or_thromboembolism:
        items.append(("prior stroke / TIA / thromboembolism", 2))
    if features.vascular_disease:
        items.append(("vascular disease", 1))
    if features.sex == "female":
        items.append(("female sex", 1))
    return tuple(items)


def cha2ds2_vasc_score(features: Cha2ds2VascFeatures) -> int:
    """Compute the CHA2DS2-VASc score, range 0 to 9."""
    return sum(points for _, points in cha2ds2_vasc_criteria(features))


def cha2ds2_vasc_assessment(features: Cha2ds2VascFeatures) -> Cha2ds2VascResult:
    """Return the CHA2DS2-VASc score and anticoagulation recommendation.

    The recommendation follows the ESC 2020 framing, which interprets the
    score differently for male and female patients to avoid awarding
    anticoagulation on the basis of sex alone.

    Args:
        features: The clinical features. See `Cha2ds2VascFeatures`.

    Returns:
        A `Cha2ds2VascResult`.
    """
    criteria = cha2ds2_vasc_criteria(features)
    score = sum(points for _, points in criteria)
    stroke_risk = _STROKE_RISK_BY_SCORE[score]

    if features.sex == "male":
        if score == 0:
            recommendation = "Anticoagulation not recommended."
            rationale = "CHA2DS2-VASc of 0 in a male patient indicates low stroke risk."
        elif score == 1:
            recommendation = (
                "Consider anticoagulation after shared decision-making (ESC Class IIa). "
                "Weigh patient preferences and HAS-BLED bleeding risk."
            )
            rationale = "CHA2DS2-VASc of 1 in a male patient is the borderline category in ESC 2020."
        else:
            recommendation = (
                "Anticoagulation recommended (ESC Class I). "
                "Assess bleeding risk with HAS-BLED and address modifiable factors."
            )
            rationale = "CHA2DS2-VASc of 2 or more in a male patient meets the ESC threshold for anticoagulation."
    else:
        if score <= 1:
            recommendation = "Anticoagulation not recommended."
            rationale = (
                "CHA2DS2-VASc of 0 or 1 in a female patient (sex point alone or no points) "
                "does not meet the ESC threshold for anticoagulation."
            )
        elif score == 2:
            recommendation = (
                "Consider anticoagulation after shared decision-making (ESC Class IIa). "
                "Weigh patient preferences and HAS-BLED bleeding risk."
            )
            rationale = "CHA2DS2-VASc of 2 in a female patient (sex plus one risk factor) is the borderline category in ESC 2020."
        else:
            recommendation = (
                "Anticoagulation recommended (ESC Class I). "
                "Assess bleeding risk with HAS-BLED and address modifiable factors."
            )
            rationale = "CHA2DS2-VASc of 3 or more in a female patient meets the ESC threshold for anticoagulation."

    return Cha2ds2VascResult(
        score=score,
        criteria_present=criteria,
        annual_stroke_risk_band=stroke_risk,
        recommended_anticoagulation=recommendation,
        rationale=rationale,
        citations=("Lip 2010", "ESC 2020", "CCS 2020"),
    )
