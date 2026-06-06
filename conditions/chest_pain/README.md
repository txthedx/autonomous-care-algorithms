# Chest pain: HEART score

The **HEART score** (Six 2008; validated Backus 2013) stratifies adults presenting to the emergency department with chest pain by their short-term (6-week) risk of a **major adverse cardiac event** (MACE: all-cause death, acute myocardial infarction, or coronary revascularization). It is one of the most widely used and best-validated chest-pain risk tools.

## Clinical context

Chest pain is among the most common and highest-stakes presentations in emergency and primary care. Most patients do not have acute coronary syndrome, but missing those who do is a major source of preventable death and litigation. The HEART score structures the disposition decision — who is low enough risk for early discharge with follow-up, who needs observation and serial troponin, and who needs admission and an early invasive strategy.

## Scope of this module

- Computes the **HEART score** (integer, range 0 to 10).
- Returns a **per-component breakdown** (History, ECG, Age, Risk factors, Troponin) for auditability.
- Returns the **risk band** (low / moderate / high) with the approximate 6-week MACE estimate from the Backus 2013 validation cohort and a narrative disposition.

It does **not**:

- Apply to ST-elevation myocardial infarction, hemodynamic instability, or an obvious non-cardiac cause of chest pain; those patients are managed independently of the score.
- Diagnose acute coronary syndrome; only serial troponin, ECG, and clinical synthesis do.
- Replace a validated serial-troponin discharge pathway. A low score alone is generally not sufficient for discharge.
- Recommend specific anticoagulant, antiplatelet, or anti-ischemic regimens.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Components

| Component | 0 points | 1 point | 2 points |
|---|---|---|---|
| **H**istory | Slightly suspicious | Moderately suspicious | Highly suspicious |
| **E**CG | Normal | Non-specific repolarization disturbance | Significant ST deviation |
| **A**ge | < 45 | 45–64 | ≥ 65 |
| **R**isk factors | None | 1–2 risk factors | ≥ 3 risk factors, or known atherosclerotic disease |
| **T**roponin | ≤ normal limit | 1–3× normal limit | > 3× normal limit |

Risk factors counted: hypertension, hypercholesterolemia, diabetes mellitus, current or recent smoking (cessation ≤ 90 days), family history of coronary artery disease, and obesity (BMI > 30). A history of established atherosclerotic disease (prior MI, PCI or CABG, stroke or TIA, or peripheral arterial disease) scores the risk-factor component **+2** regardless of the count.

## Inputs

| Input | Type |
|---|---|
| `history` | `"slightly_suspicious"` / `"moderately_suspicious"` / `"highly_suspicious"` |
| `ecg` | `"normal"` / `"nonspecific_repolarization_disturbance"` / `"significant_st_deviation"` |
| `age_years` | int |
| `hypertension` | bool |
| `hypercholesterolemia` | bool |
| `diabetes_mellitus` | bool |
| `current_or_recent_smoking` | bool |
| `family_history_of_cad` | bool |
| `obesity_bmi_over_30` | bool |
| `history_of_atherosclerotic_disease` | bool |
| `troponin` | `"at_or_below_normal_limit"` / `"one_to_three_times_normal_limit"` / `"above_three_times_normal_limit"` |

The risk-factor booleans are reduced to the risk-factor component internally, so the +2 atherosclerotic-disease override and the 0 / 1–2 / ≥3 count thresholds are applied consistently rather than left to the caller.

## Interpretation

| Score | Risk band | Approximate 6-week MACE (Backus 2013) | Disposition |
|---|---|---|---|
| 0–3 | Low | ~1.7% | Candidate for early discharge within a serial-troponin pathway |
| 4–6 | Moderate | ~16.6% | Observation, serial troponin, further risk stratification |
| 7–10 | High | ~50.1% | Admit; cardiology, consider early invasive strategy |

## Outputs

- `score` (int, 0 to 10).
- `components` (`HeartComponentScores`: `history`, `ecg`, `age`, `risk_factors`, `troponin`).
- `risk_band` (`"low"`, `"moderate"`, or `"high"`).
- `estimated_6_week_mace_band` (approximate from Backus 2013).
- `recommended_disposition`, `rationale`.
- `population_caveats` (where the score does not apply or needs care).
- `citations`.

## Usage

```python
from conditions.chest_pain import HeartFeatures, heart_assessment

features = HeartFeatures(
    history="moderately_suspicious",
    ecg="normal",
    age_years=58,
    hypertension=True,
    hypercholesterolemia=True,
    diabetes_mellitus=False,
    current_or_recent_smoking=False,
    family_history_of_cad=False,
    obesity_bmi_over_30=False,
    history_of_atherosclerotic_disease=False,
    troponin="at_or_below_normal_limit",
)
result = heart_assessment(features)
print(result.score, result.risk_band, result.estimated_6_week_mace_band)
# 3 low approximately 1.7% (Backus 2013)
```

## See also

- [algorithm.md](algorithm.md) — components and bands with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
