# HEART score

A bedside score for short-term cardiac risk stratification of emergency-department chest pain.

Derived: Six 2008 (*Neth Heart J*). Prospectively validated in a multicenter cohort: Backus 2013 (*Int J Cardiol*). An early-discharge pathway combining a low score with serial troponin was tested in a randomized trial: Mahler 2015 (*Circ Cardiovasc Qual Outcomes*).

The acronym maps to its five components: **H**istory, **E**CG, **A**ge, **R**isk factors, **T**roponin. Each scores 0, 1, or 2 for a total of 0 to 10.

## Components

| Component | 0 | 1 | 2 |
|---|---|---|---|
| History | Slightly suspicious | Moderately suspicious | Highly suspicious |
| ECG | Normal | Non-specific repolarization disturbance (e.g. LBBB, LVH, repolarization changes, digoxin effect) | Significant ST deviation not due to LBBB/LVH/digoxin |
| Age | < 45 | 45–64 | ≥ 65 |
| Risk factors | No risk factors | 1–2 risk factors | ≥ 3 risk factors, or history of atherosclerotic disease |
| Troponin | ≤ normal limit | 1–3× normal limit | > 3× normal limit |

### Risk factors

Hypertension, hypercholesterolemia, diabetes mellitus, current or recent smoking (cessation ≤ 90 days), family history of coronary artery disease, and obesity (BMI > 30).

A history of established atherosclerotic disease — prior myocardial infarction, percutaneous coronary intervention or coronary artery bypass grafting, stroke or transient ischemic attack, or peripheral arterial disease — scores the risk-factor component **+2** regardless of the number of risk factors present.

### Troponin

Graded against the local assay's 99th-percentile upper reference limit. With high-sensitivity assays, the score is still calculable, but accelerated 0/1-hour ESC pathways may outperform a single measurement.

## Interpretation

Bands and approximate 6-week MACE (all-cause death, acute myocardial infarction, or coronary revascularization) from the Backus 2013 validation cohort:

| Score | Risk band | 6-week MACE | Action |
|---|---|---|---|
| 0–3 | Low | ~1.7% | Candidate for early discharge with outpatient follow-up, within a validated serial-troponin pathway. |
| 4–6 | Moderate | ~16.6% | Admit or observe; serial troponin and further risk stratification. |
| 7–10 | High | ~50.1% | Admit; cardiology involvement, consider early invasive strategy. |

## Use restrictions

The HEART score does **not** apply to patients with ST-elevation myocardial infarction, hemodynamic instability, or an obvious non-cardiac cause of chest pain. It predicts MACE rather than diagnosing acute coronary syndrome, and a low score is generally not sufficient for discharge on its own — validated early-discharge protocols (e.g., the HEART Pathway, Mahler 2015) pair a score of 0–3 with serial troponin.

## Implementation note

The History, ECG, and Troponin components are passed as named levels. Age is passed as a raw value and mapped to 0/1/2 internally. The Risk-factor component is derived from the six individual risk-factor booleans plus a `history_of_atherosclerotic_disease` flag, so the +2 override and the 0 / 1–2 / ≥3 thresholds are applied in one place rather than relying on the caller to pre-count. `heart_assessment` also returns the per-component breakdown (`HeartComponentScores`) so the total can be audited against each input. A negative `age_years` raises `ValueError`.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Six 2008` — Six AJ et al., *Neth Heart J* 2008 (derivation).
- `Backus 2013` — Backus BE et al., *Int J Cardiol* 2013 (validation; MACE rates).
- `Mahler 2015` — Mahler SA et al., *Circ Cardiovasc Qual Outcomes* 2015 (HEART Pathway trial).
