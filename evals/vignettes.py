"""Synthetic primary-care vignettes for the end-to-end eval harness.

Each vignette is a (note, pre-extracted features, expected outcome) triple. The
notes are fictional and contain no patient-identifiable data. The pre-extracted
features let the harness run the full stack deterministically with `DictExtractor`
(no LLM) in CI; the same vignettes can be run with a live extractor for an
LLM-in-the-loop eval.

Expected result values were captured from the deterministic algorithms, so a
vignette failing means the stack changed behavior — a regression signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Vignette:
    """One end-to-end case.

    Attributes:
        name: Identifier.
        presentation: Presentation tag to focus the catalog (or None for all).
        note: Fictional clinical note (no PHI).
        features: Pre-extracted features as (name, value) pairs.
        expect_applicable: Condition keys that must appear in `applicable`.
        expect_results: (condition, result_field, expected_value) assertions.
    """

    name: str
    presentation: str | None
    note: str
    features: tuple[tuple[str, Any], ...]
    expect_applicable: tuple[str, ...]
    expect_results: tuple[tuple[str, str, Any], ...]


VIGNETTES: tuple[Vignette, ...] = (
    Vignette(
        name="chest_pain_heart_low",
        presentation="chest pain",
        note=(
            "A 58-year-old presents with two hours of chest pain, moderately "
            "suspicious in character. ECG is normal. History of hypertension and "
            "hypercholesterolemia, no diabetes or known vascular disease. Initial "
            "troponin is at or below the normal limit."
        ),
        features=(
            ("history", "moderately_suspicious"), ("ecg", "normal"),
            ("age_years", 58), ("hypertension", True),
            ("hypercholesterolemia", True), ("diabetes_mellitus", False),
            ("current_or_recent_smoking", False), ("family_history_of_cad", False),
            ("obesity_bmi_over_30", False),
            ("history_of_atherosclerotic_disease", False),
            ("troponin", "at_or_below_normal_limit"),
        ),
        expect_applicable=("heart",),
        expect_results=(("heart", "score", 3), ("heart", "risk_band", "low")),
    ),
    Vignette(
        name="pneumonia_crb65_moderate",
        presentation="pneumonia",
        note=(
            "A 72-year-old with cough and breathlessness. Not confused. "
            "Respiratory rate 24/min, blood pressure 110/70 mmHg."
        ),
        features=(
            ("age_years", 72), ("confusion", False),
            ("respiratory_rate_per_minute", 24), ("systolic_bp_mmhg", 110),
            ("diastolic_bp_mmhg", 70),
        ),
        expect_applicable=("crb_65",),
        expect_results=(("crb_65", "score", 1), ("crb_65", "severity_band", "moderate")),
    ),
    Vignette(
        name="dvt_wells_likely",
        presentation="deep vein thrombosis",
        note=(
            "Unilateral leg pain and swelling. Localized tenderness along the "
            "deep venous system, the entire leg is swollen, and calf swelling is "
            "more than 3 cm greater than the other side. No active cancer, no "
            "immobilization, and no alternative diagnosis is as likely."
        ),
        features=(
            ("active_cancer", False),
            ("paralysis_paresis_or_recent_lower_limb_immobilization", False),
            ("recently_bedridden_3_days_or_major_surgery_within_12_weeks", False),
            ("localized_tenderness_along_deep_venous_system", True),
            ("entire_leg_swollen", True), ("calf_swelling_more_than_3cm", True),
            ("pitting_edema_in_symptomatic_leg", False),
            ("collateral_superficial_veins_non_varicose", False),
            ("previously_documented_dvt", False),
            ("alternative_diagnosis_at_least_as_likely", False),
        ),
        expect_applicable=("wells_dvt_2t",),
        expect_results=(("wells_dvt_2t", "score", 3), ("wells_dvt_2t", "risk_band", "likely")),
    ),
    Vignette(
        name="syncope_sfsr_high",
        presentation="syncope",
        note=(
            "Transient loss of consciousness. No history of heart failure, no "
            "shortness of breath. Hematocrit 42%. The ECG is abnormal. Systolic "
            "blood pressure 128 mmHg at triage."
        ),
        features=(
            ("congestive_heart_failure_history", False),
            ("hematocrit_percent", 42.0), ("abnormal_ecg", True),
            ("shortness_of_breath", False), ("systolic_bp_mmhg", 128),
        ),
        expect_applicable=("sfsr",),
        expect_results=(("sfsr", "high_risk", True), ("sfsr", "risk_band", "high")),
    ),
    Vignette(
        name="delirium_4at_possible",
        presentation="delirium",
        note=(
            "An older inpatient, normal alertness. One mistake on the AMT4. "
            "Starts the months-of-the-year-backwards task but gets fewer than "
            "seven. There is an acute change in cognition over the last day."
        ),
        features=(
            ("alertness", "normal"), ("amt4", "one_mistake"),
            ("attention_months_backwards", "fewer_than_seven_or_refuses"),
            ("acute_change_or_fluctuating_course", True),
        ),
        expect_applicable=("four_at",),
        expect_results=(
            ("four_at", "score", 6),
            ("four_at", "interpretation_band", "possible_delirium"),
        ),
    ),
    Vignette(
        name="head_injury_ct_indicated",
        presentation="head injury",
        note=(
            "Minor head injury with brief loss of consciousness, now alert. "
            "Aged 65. No vomiting, no skull-fracture signs, no dangerous "
            "mechanism, no prolonged amnesia."
        ),
        features=(
            ("gcs_below_15_at_2_hours", False),
            ("suspected_open_or_depressed_skull_fracture", False),
            ("sign_of_basal_skull_fracture", False),
            ("vomiting_2_or_more_episodes", False), ("age_65_or_older", True),
            ("retrograde_amnesia_30_min_or_more", False),
            ("dangerous_mechanism", False),
        ),
        expect_applicable=("canadian_ct_head",),
        expect_results=(("canadian_ct_head", "ct_indicated", True),),
    ),
    Vignette(
        name="ckd_kdigo_very_high",
        presentation="chronic kidney disease",
        note=(
            "Stable outpatient with an eGFR of 35 mL/min/1.73 m2 and a urine "
            "albumin-to-creatinine ratio of 12 mg/mmol, both persistent beyond "
            "three months."
        ),
        features=(
            ("egfr_ml_min_1_73m2", 35.0), ("acr_mg_per_mmol", 12.0),
            ("persistent_over_3_months", True),
        ),
        expect_applicable=("kdigo",),
        expect_results=(
            ("kdigo", "stage_label", "G3bA2"),
            ("kdigo", "risk_band", "very_high"),
        ),
    ),
    Vignette(
        name="multi_renal_and_syncope",
        presentation=None,  # search the whole catalog
        note=(
            "An older patient with both chronic kidney disease (eGFR 35, ACR 12, "
            "persistent) and a syncopal episode (no heart failure, hematocrit "
            "42%, abnormal ECG, no dyspnea, systolic BP 128)."
        ),
        features=(
            ("egfr_ml_min_1_73m2", 35.0), ("acr_mg_per_mmol", 12.0),
            ("persistent_over_3_months", True),
            ("congestive_heart_failure_history", False),
            ("hematocrit_percent", 42.0), ("abnormal_ecg", True),
            ("shortness_of_breath", False), ("systolic_bp_mmhg", 128),
        ),
        expect_applicable=("kdigo", "sfsr"),
        expect_results=(
            ("kdigo", "stage_label", "G3bA2"),
            ("sfsr", "high_risk", True),
        ),
    ),
)
