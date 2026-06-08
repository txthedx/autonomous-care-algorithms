"""NEWS2 (National Early Warning Score 2) for acute-illness severity.

Reference:
    Royal College of Physicians.
        National Early Warning Score (NEWS) 2: Standardising the assessment of
        acute-illness severity in the NHS. Updated report of a working party.
        London: RCP; 2017.

NEWS2 aggregates seven physiological parameters (each scored 0-3) to track and
respond to acute deterioration in adults. Vitals are entered as raw values and
the bands are applied internally. SpO2 has two scales: Scale 1 for the majority
of patients, and Scale 2 only for patients with confirmed hypercapnic (type 2)
respiratory failure and an agreed target of 88-92%.

A single parameter scoring 3 (a "red score") warrants urgent review even when
the aggregate is low. NEWS2 is not validated for children or pregnancy. Not a
medical device; clinical judgement overrides the score. See DISCLAIMER.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Consciousness = Literal["alert", "confusion_or_vpu"]
MonitoringBand = Literal["low", "low_medium", "medium", "high"]


@dataclass(frozen=True)
class NewsFeatures:
    """Inputs for NEWS2.

    Attributes:
        respiratory_rate_per_minute: Respiratory rate.
        spo2_percent: Oxygen saturation (0-100).
        on_supplemental_oxygen: True if on any supplemental oxygen (+2).
        use_spo2_scale_2: Use SpO2 Scale 2 (only for confirmed hypercapnic
            respiratory failure with a target of 88-92%); otherwise Scale 1.
        systolic_bp_mmhg: Systolic blood pressure.
        pulse_per_minute: Pulse rate.
        consciousness: "alert" (A) scores 0; "confusion_or_vpu" (new confusion
            or responding only to Voice/Pain/Unresponsive) scores 3.
        temperature_celsius: Temperature in degrees Celsius.
    """

    respiratory_rate_per_minute: int
    spo2_percent: int
    on_supplemental_oxygen: bool
    use_spo2_scale_2: bool
    systolic_bp_mmhg: int
    pulse_per_minute: int
    consciousness: Consciousness
    temperature_celsius: float


@dataclass(frozen=True)
class NewsComponentScores:
    """Per-parameter NEWS2 points (each 0-3)."""

    respiratory_rate: int
    spo2: int
    supplemental_oxygen: int
    systolic_bp: int
    pulse: int
    consciousness: int
    temperature: int


@dataclass(frozen=True)
class NewsResult:
    """NEWS2 assessment result.

    Attributes:
        score: Aggregate NEWS2 score.
        components: Per-parameter breakdown.
        any_parameter_scored_3: True if any single parameter scored 3 (a red
            score) — warrants review even at a low aggregate.
        monitoring_band: "low", "low_medium", "medium", or "high".
        recommended_response: Narrative clinical response.
        rationale: Short justification.
        population_caveats: Conditions under which the score must be interpreted
            with care.
        citations: Source short tags.
    """

    score: int
    components: NewsComponentScores
    any_parameter_scored_3: bool
    monitoring_band: MonitoringBand
    recommended_response: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_POPULATION_CAVEATS: tuple[str, ...] = (
    "NEWS2 is validated in adults; it is not validated for children (under 16) "
    "or in pregnancy, where age- or pregnancy-specific tools should be used.",
    "Use SpO2 Scale 2 only for patients with confirmed hypercapnic (type 2) "
    "respiratory failure and an agreed target of 88-92%; otherwise use Scale 1.",
    "A single parameter scoring 3 (a red score) warrants urgent review even at "
    "a low aggregate; clinical judgement overrides the score.",
    "The supplemental-oxygen parameter scores for any added oxygen; record the "
    "device and flow separately. Temperature is in degrees Celsius.",
)


def _check(features: NewsFeatures) -> None:
    if not 0 <= features.spo2_percent <= 100:
        raise ValueError("spo2_percent must be between 0 and 100")
    for value, name in (
        (features.respiratory_rate_per_minute, "respiratory_rate_per_minute"),
        (features.systolic_bp_mmhg, "systolic_bp_mmhg"),
        (features.pulse_per_minute, "pulse_per_minute"),
    ):
        if value < 0:
            raise ValueError(f"{name} must not be negative")


def _rr_points(rr: int) -> int:
    if rr <= 8:
        return 3
    if rr <= 11:
        return 1
    if rr <= 20:
        return 0
    if rr <= 24:
        return 2
    return 3


def _spo2_points(spo2: int, scale_2: bool, on_oxygen: bool) -> int:
    if not scale_2:
        if spo2 <= 91:
            return 3
        if spo2 <= 93:
            return 2
        if spo2 <= 95:
            return 1
        return 0
    # Scale 2
    if spo2 <= 83:
        return 3
    if spo2 <= 85:
        return 2
    if spo2 <= 87:
        return 1
    if spo2 <= 92:
        return 0
    if not on_oxygen:
        return 0
    if spo2 <= 94:
        return 1
    if spo2 <= 96:
        return 2
    return 3


def _sbp_points(sbp: int) -> int:
    if sbp <= 90:
        return 3
    if sbp <= 100:
        return 2
    if sbp <= 110:
        return 1
    if sbp <= 219:
        return 0
    return 3


def _pulse_points(pulse: int) -> int:
    if pulse <= 40:
        return 3
    if pulse <= 50:
        return 1
    if pulse <= 90:
        return 0
    if pulse <= 110:
        return 1
    if pulse <= 130:
        return 2
    return 3


def _temp_points(temp: float) -> int:
    if temp <= 35.0:
        return 3
    if temp <= 36.0:
        return 1
    if temp <= 38.0:
        return 0
    if temp <= 39.0:
        return 1
    return 2


def news2_component_scores(features: NewsFeatures) -> NewsComponentScores:
    """Return the per-parameter NEWS2 breakdown.

    Raises:
        ValueError: If a value is out of range.
    """
    _check(features)
    return NewsComponentScores(
        respiratory_rate=_rr_points(features.respiratory_rate_per_minute),
        spo2=_spo2_points(features.spo2_percent, features.use_spo2_scale_2,
                          features.on_supplemental_oxygen),
        supplemental_oxygen=2 if features.on_supplemental_oxygen else 0,
        systolic_bp=_sbp_points(features.systolic_bp_mmhg),
        pulse=_pulse_points(features.pulse_per_minute),
        consciousness=3 if features.consciousness == "confusion_or_vpu" else 0,
        temperature=_temp_points(features.temperature_celsius),
    )


def news2_score(features: NewsFeatures) -> int:
    """Compute the aggregate NEWS2 score."""
    c = news2_component_scores(features)
    return (c.respiratory_rate + c.spo2 + c.supplemental_oxygen + c.systolic_bp
            + c.pulse + c.consciousness + c.temperature)


def news2_assessment(features: NewsFeatures) -> NewsResult:
    """Compute NEWS2 and its monitoring band and response.

    Args:
        features: Vitals and observations. See `NewsFeatures`.

    Returns:
        A `NewsResult`.

    Raises:
        ValueError: If a value is out of range.
    """
    components = news2_component_scores(features)
    score = (components.respiratory_rate + components.spo2
             + components.supplemental_oxygen + components.systolic_bp
             + components.pulse + components.consciousness + components.temperature)
    red = any(p == 3 for p in (
        components.respiratory_rate, components.spo2, components.supplemental_oxygen,
        components.systolic_bp, components.pulse, components.consciousness,
        components.temperature))
    citations = ("RCP 2017",)

    if score >= 7:
        band: MonitoringBand = "high"
        response = ("High score. Emergency assessment by a clinical team with "
                    "critical-care competencies; continuous monitoring.")
    elif score >= 5:
        band = "medium"
        response = ("Medium score. Urgent review by a clinician able to assess "
                    "acutely ill patients; increase monitoring frequency.")
    elif red:
        band = "low_medium"
        response = ("A single parameter scored 3 (red score). Urgent review by "
                    "a clinician to decide on escalation and monitoring.")
    else:
        band = "low"
        response = ("Low score. Continue routine ward-based monitoring per local "
                    "protocol.")

    return NewsResult(
        score=score,
        components=components,
        any_parameter_scored_3=red,
        monitoring_band=band,
        recommended_response=response,
        rationale=f"Aggregate NEWS2 score of {score}{' with a red score' if red else ''} corresponds to the {band.replace('_', '-')} band.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
