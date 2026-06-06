# Chronic kidney disease: KDIGO staging

KDIGO classifies chronic kidney disease by **Cause**, **GFR category (G1–G5)**, and **Albuminuria category (A1–A3)** — the "CGA" framework. The GFR and albuminuria categories combine into a colour-coded **heat map** of risk (low / moderately increased / high / very high) that drives monitoring frequency and nephrology-referral decisions.

## Clinical context

CKD is common, often asymptomatic, and a major cardiovascular-risk multiplier. Staging by GFR alone misses the prognostic weight of albuminuria; the KDIGO heat map combines the two so that, for example, a patient with preserved GFR but heavy albuminuria is correctly flagged as higher risk. The risk band guides how often to monitor and when to involve nephrology.

## Scope of this module

- Computes the **GFR category** from a supplied eGFR (it does **not** estimate GFR from creatinine — that is a separate calculation).
- Computes the **albuminuria category** from a urine albumin-to-creatinine ratio (ACR) in mg/mmol.
- Returns the **risk band** and heat-map colour, a combined stage label (e.g. `G3bA2`), a monitoring recommendation, and whether nephrology referral is indicated.
- Takes an explicit **chronicity flag** (`persistent_over_3_months`): a single measurement cannot establish CKD.

It does **not**:

- Estimate GFR from serum creatinine (use a CKD-EPI calculation upstream).
- Determine the cause of CKD (the "C" of CGA).
- Replace clinical judgement; eGFR equations are unreliable at the extremes of muscle mass and in acute illness.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## GFR categories

| Category | eGFR (mL/min/1.73 m²) |
|---|---|
| G1 | ≥ 90 |
| G2 | 60–89 |
| G3a | 45–59 |
| G3b | 30–44 |
| G4 | 15–29 |
| G5 | < 15 |

## Albuminuria categories

| Category | ACR (mg/mmol) | ACR (mg/g) |
|---|---|---|
| A1 | < 3 | < 30 |
| A2 | 3–30 | 30–300 |
| A3 | > 30 | > 300 |

This module takes ACR in **mg/mmol** (Canadian/SI units). To convert from mg/g, divide by approximately 8.84.

## Risk heat map

| GFR \ Albuminuria | A1 | A2 | A3 |
|---|---|---|---|
| **G1** | Low (green) | Moderate (yellow) | High (orange) |
| **G2** | Low (green) | Moderate (yellow) | High (orange) |
| **G3a** | Moderate (yellow) | High (orange) | Very high (red) |
| **G3b** | High (orange) | Very high (red) | Very high (red) |
| **G4** | Very high (red) | Very high (red) | Very high (red) |
| **G5** | Very high (red) | Very high (red) | Very high (red) |

## Inputs

| Input | Type |
|---|---|
| `egfr_ml_min_1_73m2` | float |
| `acr_mg_per_mmol` | float |
| `persistent_over_3_months` | bool |

## Outputs

- `gfr_category` (`"G1"`–`"G5"`), `albuminuria_category` (`"A1"`–`"A3"`), `stage_label` (e.g. `"G3bA2"`).
- `risk_band` (`"low"`, `"moderately_increased"`, `"high"`, `"very_high"`), `risk_color` (`green`/`yellow`/`orange`/`red`).
- `meets_ckd_chronicity_criterion` (echo of the chronicity flag).
- `nephrology_referral_indicated` (True for G4, G5, or A3).
- `recommended_monitoring`, `recommended_disposition`, `rationale`.
- `population_caveats`, `citations`.

## Usage

```python
from conditions.chronic_kidney_disease import KdigoFeatures, kdigo_assessment

features = KdigoFeatures(
    egfr_ml_min_1_73m2=35.0,
    acr_mg_per_mmol=12.0,
    persistent_over_3_months=True,
)
result = kdigo_assessment(features)
print(result.stage_label, result.risk_band, result.nephrology_referral_indicated)
# G3bA2 very_high False  (very-high risk, but referral here triggers only on G4/G5 or A3)
```

## See also

- [algorithm.md](algorithm.md) — categories and heat map with citations.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests and the full 18-cell heat map.
