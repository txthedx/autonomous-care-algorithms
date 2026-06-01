# Community-acquired pneumonia (CAP) severity

Two complementary severity scores used by primary care and emergency clinicians to guide disposition (outpatient versus inpatient versus higher-acuity) in adults with community-acquired pneumonia:

1. **CRB-65** — four-item clinical score (no labs). Best suited to primary care and community settings where urea is not immediately available. Validated in Lim 2003.
2. **CURB-65** — the five-item score adding serum urea. Standard in emergency and inpatient settings. Endorsed by the British Thoracic Society and used widely in NICE guidance.

This module implements both. The intended pattern: use **CRB-65** in primary care without labs; use **CURB-65** when serum urea is available.

## Clinical context

Community-acquired pneumonia is a frequent reason for primary care visits and one of the leading infectious causes of death in adults. Disposition decisions (treat at home, refer to hospital, escalate to ICU) materially affect outcomes and resource use. The CURB-65 and CRB-65 scores stratify 30-day mortality risk using a small number of clinical and laboratory variables, providing a structured frame for the disposition decision.

Scores do **not** replace clinical judgment. They are decision aids that perform best when synthesized with the items they do not capture: oxygenation, radiographic extent, comorbidity burden, social factors, and the patient's own preferences.

## Scope of this module

This module:

- Computes the CURB-65 score (0 to 5) and assigns a severity band.
- Computes the CRB-65 score (0 to 4) and assigns a severity band.
- Returns recommended disposition language aligned with Lim 2003 and the BTS 2009 guideline, with explicit acknowledgement of factors the scores do not capture.

It does **not**:

- Apply to pediatric pneumonia. CURB-65 and CRB-65 are adult tools.
- Apply to hospital-acquired pneumonia, ventilator-associated pneumonia, or aspiration pneumonia in distinct clinical contexts.
- Apply to immunocompromised hosts without independent clinical synthesis.
- Provide ICU admission criteria. The IDSA/ATS 2007 criteria are the standard tool for that question and are not implemented here.
- Recommend specific antibiotics, doses, or routes.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Factors the scores do not capture

The published scores were derived to predict 30-day mortality from a small number of variables and deliberately omit several factors that change disposition in practice. These should be assessed independently:

- **Oxygenation.** Hypoxia (commonly SpO₂ < 92% on room air in non-COPD patients) is a well-recognized indication for hospital assessment regardless of CURB-65 score.
- **Radiographic extent.** Multilobar or bilateral involvement increases risk.
- **Comorbidities.** CHF, COPD, CKD, liver disease, diabetes, and immunocompromise raise risk independent of the score.
- **Social factors.** Inability to take oral medications, lives alone without support, homelessness, or substance use can shift disposition toward admission.
- **Pregnancy.** Pregnant patients typically warrant lower thresholds for hospital assessment.

## Inputs

### CRB-65

| Input | Type | Definition |
|---|---|---|
| `age_years` | int | Patient age in completed years. |
| `confusion` | bool | New disorientation in person, place, or time, or AMTS ≤ 8. |
| `respiratory_rate_per_minute` | int | Resting respiratory rate. |
| `systolic_bp_mmhg` | int | Systolic blood pressure. |
| `diastolic_bp_mmhg` | int | Diastolic blood pressure. |

### CURB-65

All of the CRB-65 inputs, plus:

| Input | Type | Definition |
|---|---|---|
| `urea_mmol_per_l` | float | Serum urea in mmol/L (Canadian and UK units). For US BUN in mg/dL, multiply by 0.357 to convert to mmol/L (urea) approximately. |

## Outputs

The score functions return a result dataclass with:

- `score` (int).
- `criteria_present` (tuple of the score components that were met).
- `severity_band` (`"low"`, `"moderate"`, or `"high"`).
- `recommended_disposition` (narrative aligned to Lim 2003 / BTS 2009).
- `mortality_band` (approximate 30-day mortality band from Lim 2003).
- `rationale`.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — both rules with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests and disposition tests.
