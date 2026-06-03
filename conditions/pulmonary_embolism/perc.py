"""PERC (Pulmonary Embolism Rule-out Criteria).

References:
    Kline JA, Mitchell AM, Kabrhel C, Richman PB, Courtney DM.
        Clinical criteria to prevent unnecessary diagnostic testing in
        emergency department patients with suspected pulmonary embolism.
        J Thromb Haemost. 2004;2(8):1247-1255. PMID: 15304025.
    Kline JA, Courtney DM, Kabrhel C, et al.
        Prospective multicenter evaluation of the pulmonary embolism
        rule-out criteria. J Thromb Haemost. 2008;6(5):772-780.
        PMID: 18318689.

PERC may be used **only** in patients with low pretest probability of PE
(Wells PE < 2, two-tier "unlikely", or clinical gestalt of < 15%). The
function in this module requires the caller to pass an explicit
`pretest_probability_is_low: bool`; if False, the function refuses to
rule out PE.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PercFeatures:
    """Clinical features for PERC.

    Each field is the *positive finding*. PERC passes (PE may be ruled out
    in a low-pretest-probability patient) only when **all eight fields are
    False**.

    Attributes:
        age_50_or_older: Age 50 years or older. Positive finding.
        heart_rate_100_or_more: Heart rate 100/min or greater. Positive finding.
        spo2_below_95_on_room_air: SpO2 less than 95% on room air. Positive
            finding.
        hemoptysis: Hemoptysis present. Positive finding.
        estrogen_use: Estrogen use (oral contraceptives or hormone
            replacement therapy). Positive finding.
        prior_dvt_or_pe: Previously documented DVT or PE. Positive finding.
        unilateral_leg_swelling: Unilateral leg swelling on examination.
            Positive finding.
        recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization:
            Recent surgery or trauma within the past 4 weeks that required
            hospitalization. Positive finding.
    """

    age_50_or_older: bool
    heart_rate_100_or_more: bool
    spo2_below_95_on_room_air: bool
    hemoptysis: bool
    estrogen_use: bool
    prior_dvt_or_pe: bool
    unilateral_leg_swelling: bool
    recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization: bool


@dataclass(frozen=True)
class PercResult:
    """PERC assessment result.

    Attributes:
        pretest_probability_is_low: Echoed back from input. PERC may only
            be applied when this is True.
        perc_failure_criteria_present: Labels of positive criteria. PERC
            "fails" if this is non-empty.
        pe_ruled_out: True only when `pretest_probability_is_low` is True
            and `perc_failure_criteria_present` is empty.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        citations: Source short tags.
    """

    pretest_probability_is_low: bool
    perc_failure_criteria_present: tuple[str, ...]
    pe_ruled_out: bool
    recommended_action: str
    rationale: str
    citations: tuple[str, ...]


_FIELD_LABELS: dict[str, str] = {
    "age_50_or_older": "age 50 or older",
    "heart_rate_100_or_more": "heart rate 100 or more",
    "spo2_below_95_on_room_air": "SpO2 below 95% on room air",
    "hemoptysis": "hemoptysis",
    "estrogen_use": "estrogen use",
    "prior_dvt_or_pe": "prior DVT or PE",
    "unilateral_leg_swelling": "unilateral leg swelling",
    "recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization": "recent surgery or trauma requiring hospitalization within 4 weeks",
}


def perc_failure_criteria(features: PercFeatures) -> tuple[str, ...]:
    """Return labels of positive PERC criteria (which cause PERC to fail)."""
    return tuple(label for attr, label in _FIELD_LABELS.items() if getattr(features, attr))


def perc_assessment(
    features: PercFeatures,
    pretest_probability_is_low: bool,
) -> PercResult:
    """Apply PERC.

    PERC may only be used when pretest probability is low; the caller must
    pass `pretest_probability_is_low=True` to allow rule-out. If
    `pretest_probability_is_low` is False, the function returns
    `pe_ruled_out=False` and recommends the Wells PE / D-dimer pathway.

    Args:
        features: Clinical features. See `PercFeatures`.
        pretest_probability_is_low: True if the patient has low pretest
            probability of PE (Wells PE < 2, two-tier "unlikely", or
            clinical gestalt of < 15%).

    Returns:
        A `PercResult`.
    """
    failure_criteria = perc_failure_criteria(features)
    citations = ("Kline 2004", "Kline 2008")

    if not pretest_probability_is_low:
        return PercResult(
            pretest_probability_is_low=False,
            perc_failure_criteria_present=failure_criteria,
            pe_ruled_out=False,
            recommended_action=(
                "PERC was not applied. PERC is validated only at low pretest probability "
                "(Wells PE < 2, two-tier 'unlikely', or clinical gestalt < 15%). "
                "Use the Wells PE / sensitive D-dimer pathway: D-dimer for moderate probability, CT-PA directly for high probability."
            ),
            rationale="Pretest probability is not low; applying PERC at higher probabilities misses PE.",
            citations=citations,
        )

    if not failure_criteria:
        return PercResult(
            pretest_probability_is_low=True,
            perc_failure_criteria_present=(),
            pe_ruled_out=True,
            recommended_action=(
                "PE is excluded by PERC. No further testing for PE is required."
            ),
            rationale="All eight PERC criteria are negative in a patient with low pretest probability.",
            citations=citations,
        )

    return PercResult(
        pretest_probability_is_low=True,
        perc_failure_criteria_present=failure_criteria,
        pe_ruled_out=False,
        recommended_action=(
            "PERC fails. Obtain a sensitive D-dimer; proceed to CT pulmonary angiography if positive."
        ),
        rationale="At least one PERC criterion is positive; PERC may not be used to rule out PE.",
        citations=citations,
    )
