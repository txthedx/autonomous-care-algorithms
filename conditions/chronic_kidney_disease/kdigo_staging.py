"""KDIGO chronic kidney disease staging (GFR and albuminuria heat map).

References:
    Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group.
        KDIGO 2024 Clinical Practice Guideline for the Evaluation and
        Management of Chronic Kidney Disease. Kidney Int. 2024;105(4S):
        S117-S314.
    Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group.
        KDIGO 2012 Clinical Practice Guideline for the Evaluation and
        Management of Chronic Kidney Disease. Kidney Int Suppl. 2013;3:1-150.

KDIGO classifies CKD by Cause, GFR category (G1-G5), and Albuminuria category
(A1-A3) — the "CGA" framework. The GFR and albuminuria categories combine into
a colour-coded heat map of risk (low / moderately increased / high / very high)
that drives monitoring frequency and nephrology-referral decisions.

This module computes the GFR category from a supplied eGFR (it does not estimate
GFR from creatinine), the albuminuria category from a urine albumin-to-creatinine
ratio (ACR) in Canadian/SI units (mg/mmol), and the resulting risk band.

CKD is defined by abnormalities of kidney structure or function present for more
than three months. This module takes an explicit `persistent_over_3_months`
flag; a single measurement cannot establish CKD, and acute kidney injury must be
excluded. See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GfrCategory = Literal["G1", "G2", "G3a", "G3b", "G4", "G5"]
AlbuminuriaCategory = Literal["A1", "A2", "A3"]
RiskBand = Literal["low", "moderately_increased", "high", "very_high"]


@dataclass(frozen=True)
class KdigoFeatures:
    """Inputs for KDIGO CKD staging.

    Attributes:
        egfr_ml_min_1_73m2: Estimated GFR in mL/min/1.73 m². Determines the
            GFR category (G1 >= 90, G2 60-89, G3a 45-59, G3b 30-44,
            G4 15-29, G5 < 15).
        acr_mg_per_mmol: Urine albumin-to-creatinine ratio in mg/mmol.
            Determines the albuminuria category (A1 < 3, A2 3-30, A3 > 30).
        persistent_over_3_months: True if the abnormalities have persisted
            for more than three months. CKD cannot be diagnosed without this;
            a single measurement reflects a point-in-time category only.
    """

    egfr_ml_min_1_73m2: float
    acr_mg_per_mmol: float
    persistent_over_3_months: bool


@dataclass(frozen=True)
class KdigoResult:
    """KDIGO CKD staging result.

    Attributes:
        gfr_category: GFR category, "G1" through "G5".
        albuminuria_category: Albuminuria category, "A1", "A2", or "A3".
        stage_label: Combined CGA-style label, e.g. "G3bA2".
        risk_band: "low", "moderately_increased", "high", or "very_high".
        risk_color: KDIGO heat-map colour: "green", "yellow", "orange", "red".
        meets_ckd_chronicity_criterion: Echo of `persistent_over_3_months`.
        nephrology_referral_indicated: True for G4, G5, or A3.
        recommended_monitoring: Suggested minimum monitoring frequency.
        recommended_disposition: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the staging must be
            interpreted with care.
        citations: Source short tags.
    """

    gfr_category: GfrCategory
    albuminuria_category: AlbuminuriaCategory
    stage_label: str
    risk_band: RiskBand
    risk_color: str
    meets_ckd_chronicity_criterion: bool
    nephrology_referral_indicated: bool
    recommended_monitoring: str
    recommended_disposition: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


# The KDIGO heat map: (GFR category, albuminuria category) -> risk band.
_RISK_HEAT_MAP: dict[tuple[str, str], RiskBand] = {
    ("G1", "A1"): "low", ("G1", "A2"): "moderately_increased", ("G1", "A3"): "high",
    ("G2", "A1"): "low", ("G2", "A2"): "moderately_increased", ("G2", "A3"): "high",
    ("G3a", "A1"): "moderately_increased", ("G3a", "A2"): "high", ("G3a", "A3"): "very_high",
    ("G3b", "A1"): "high", ("G3b", "A2"): "very_high", ("G3b", "A3"): "very_high",
    ("G4", "A1"): "very_high", ("G4", "A2"): "very_high", ("G4", "A3"): "very_high",
    ("G5", "A1"): "very_high", ("G5", "A2"): "very_high", ("G5", "A3"): "very_high",
}

_RISK_COLOR: dict[RiskBand, str] = {
    "low": "green",
    "moderately_increased": "yellow",
    "high": "orange",
    "very_high": "red",
}

_MONITORING: dict[RiskBand, str] = {
    "low": "If CKD is confirmed, monitor eGFR and ACR at least once per year.",
    "moderately_increased": "Monitor eGFR and ACR at least once per year.",
    "high": "Monitor eGFR and ACR at least twice per year.",
    "very_high": "Monitor eGFR and ACR at least three times per year (more often in advanced disease).",
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "CKD requires abnormalities of kidney structure or function present for "
    "more than three months. A single measurement cannot establish CKD, and "
    "acute kidney injury must be excluded.",
    "G1 and G2 are CKD only when another marker of kidney damage is present "
    "(albuminuria, urine-sediment abnormalities, electrolyte or histologic "
    "abnormalities, structural abnormalities, or transplantation). G1A1 or "
    "G2A1 without such a marker is not CKD.",
    "Albuminuria is entered as ACR in mg/mmol (Canadian/SI units). To convert "
    "from mg/g, divide by approximately 8.84 (A2 = 30-300 mg/g = 3-30 mg/mmol; "
    "A3 = > 300 mg/g = > 30 mg/mmol).",
    "eGFR equations are less reliable at the extremes of muscle mass, in acute "
    "illness, and near the normal range; interpret borderline categories with "
    "the clinical context.",
    "Beyond G4/G5 and A3, nephrology referral is also indicated for rapidly "
    "progressive CKD, persistent hematuria, suspected hereditary kidney "
    "disease, refractory hypertension, or recurrent nephrolithiasis.",
)


def _check_values(features: KdigoFeatures) -> None:
    if features.egfr_ml_min_1_73m2 < 0:
        raise ValueError("egfr_ml_min_1_73m2 must not be negative")
    if features.acr_mg_per_mmol < 0:
        raise ValueError("acr_mg_per_mmol must not be negative")


def kdigo_gfr_category(egfr_ml_min_1_73m2: float) -> GfrCategory:
    """Return the GFR category for an eGFR in mL/min/1.73 m²."""
    if egfr_ml_min_1_73m2 < 0:
        raise ValueError("egfr_ml_min_1_73m2 must not be negative")
    if egfr_ml_min_1_73m2 >= 90:
        return "G1"
    if egfr_ml_min_1_73m2 >= 60:
        return "G2"
    if egfr_ml_min_1_73m2 >= 45:
        return "G3a"
    if egfr_ml_min_1_73m2 >= 30:
        return "G3b"
    if egfr_ml_min_1_73m2 >= 15:
        return "G4"
    return "G5"


def kdigo_albuminuria_category(acr_mg_per_mmol: float) -> AlbuminuriaCategory:
    """Return the albuminuria category for an ACR in mg/mmol."""
    if acr_mg_per_mmol < 0:
        raise ValueError("acr_mg_per_mmol must not be negative")
    if acr_mg_per_mmol < 3:
        return "A1"
    if acr_mg_per_mmol <= 30:
        return "A2"
    return "A3"


def kdigo_risk_band(
    gfr_category: GfrCategory,
    albuminuria_category: AlbuminuriaCategory,
) -> RiskBand:
    """Return the KDIGO heat-map risk band for a GFR and albuminuria category."""
    return _RISK_HEAT_MAP[(gfr_category, albuminuria_category)]


def kdigo_assessment(features: KdigoFeatures) -> KdigoResult:
    """Stage CKD by the KDIGO GFR and albuminuria heat map.

    Args:
        features: Inputs. See `KdigoFeatures`.

    Returns:
        A `KdigoResult`.

    Raises:
        ValueError: If eGFR or ACR is negative.
    """
    _check_values(features)
    gfr_category = kdigo_gfr_category(features.egfr_ml_min_1_73m2)
    albuminuria_category = kdigo_albuminuria_category(features.acr_mg_per_mmol)
    risk_band = kdigo_risk_band(gfr_category, albuminuria_category)
    referral = gfr_category in ("G4", "G5") or albuminuria_category == "A3"
    citations = ("KDIGO 2024", "KDIGO 2012")

    disposition_by_band: dict[RiskBand, str] = {
        "low": (
            "Low risk. G1 or G2 with A1 is CKD only when another marker of "
            "kidney damage is present and persistent. If CKD is confirmed, "
            "address cardiovascular risk and review nephrotoxic exposures."
        ),
        "moderately_increased": (
            "Moderately increased risk. Manage blood pressure, glycemia, and "
            "cardiovascular risk; review nephrotoxic exposures and consider "
            "renoprotective therapy."
        ),
        "high": (
            "High risk. Optimize renoprotective therapy and cardiovascular-risk "
            "management; nephrology referral is indicated for G4-G5 or A3 and "
            "should be considered otherwise."
        ),
        "very_high": (
            "Very high risk. Nephrology referral is recommended; optimize "
            "renoprotective therapy, plan for complications, and consider "
            "preparation for kidney replacement therapy where appropriate."
        ),
    }
    disposition = disposition_by_band[risk_band]
    if not features.persistent_over_3_months:
        disposition += (
            " Note: chronicity is not yet established — confirm that the "
            "abnormalities persist beyond three months and exclude acute "
            "kidney injury before diagnosing CKD."
        )

    return KdigoResult(
        gfr_category=gfr_category,
        albuminuria_category=albuminuria_category,
        stage_label=f"{gfr_category}{albuminuria_category}",
        risk_band=risk_band,
        risk_color=_RISK_COLOR[risk_band],
        meets_ckd_chronicity_criterion=features.persistent_over_3_months,
        nephrology_referral_indicated=referral,
        recommended_monitoring=_MONITORING[risk_band],
        recommended_disposition=disposition,
        rationale=(
            f"eGFR {features.egfr_ml_min_1_73m2} -> {gfr_category}; "
            f"ACR {features.acr_mg_per_mmol} mg/mmol -> {albuminuria_category}; "
            f"KDIGO heat map -> {risk_band} risk."
        ),
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
