# Upper GI bleeding: Glasgow-Blatchford score

The **Glasgow-Blatchford score (GBS)** (Blatchford 2000) is a pre-endoscopy risk score for acute upper gastrointestinal bleeding. It predicts the need for hospital-based intervention (transfusion, endoscopic therapy, or surgery) or death, and its principal validated use is identifying very low-risk patients who can be managed as outpatients.

## Clinical context

Upper GI bleeding is a common emergency presentation with a wide range of severity. Many patients are at very low risk and could avoid admission, while others need urgent resuscitation and endoscopy. The GBS uses only clinical and laboratory data available at first assessment — no endoscopic findings — so it can be applied immediately on arrival. A score of **0** identifies patients at very low risk of needing intervention; Stanley 2009 and Stanley 2017 validated outpatient management for low-risk patients, with Stanley 2017 finding **≤ 1** the optimum threshold.

## Scope of this module

- Computes the **GBS** (integer, range 0 to 23).
- Returns the **contributing factors** (each component that scored, with its points) for auditability.
- Returns the **risk band** (very low / intermediate / high), an explicit `outpatient_management_candidate` flag (score 0), a narrative disposition, and population caveats.

It does **not**:

- Diagnose the bleeding source; only endoscopy does.
- Apply to lower GI bleeding, or to hemodynamically unstable patients, who warrant immediate resuscitation regardless of score.
- Replace timely endoscopy or clinical judgement.
- Recommend specific transfusion thresholds or endoscopic therapies.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Units

This module uses Canadian/SI units: **blood urea in mmol/L** and **hemoglobin in g/L**. Convert before use if local results are reported in mg/dL (urea/BUN) or g/dL (hemoglobin).

## Components

| Component | Bands and points |
|---|---|
| Blood urea (mmol/L) | 6.5–7.9 (+2), 8.0–9.9 (+3), 10.0–24.9 (+4), ≥ 25.0 (+6) |
| Hemoglobin (g/L), **men** | 120–129 (+1), 100–119 (+3), < 100 (+6) |
| Hemoglobin (g/L), **women** | 100–119 (+1), < 100 (+6) |
| Systolic BP (mmHg) | 100–109 (+1), 90–99 (+2), < 90 (+3) |
| Pulse ≥ 100/min | +1 |
| Presentation with melena | +1 |
| Presentation with syncope | +2 |
| Hepatic disease | +2 |
| Cardiac failure | +2 |

Total range: 0 to 23.

## Interpretation

| Score | Risk band | Disposition |
|---|---|---|
| 0 | Very low | Outpatient management with early outpatient endoscopy may be considered |
| 1–5 | Intermediate | Admission generally warranted (a score of 1 falls at the validated ≤ 1 outpatient threshold) |
| ≥ 6 | High | Admit, resuscitate as required, expedite endoscopy, consider higher-acuity setting |

## Inputs

| Input | Type |
|---|---|
| `sex` | `"male"` / `"female"` |
| `urea_mmol_per_l` | float |
| `hemoglobin_g_per_l` | float |
| `systolic_bp_mmhg` | int |
| `pulse_per_minute` | int |
| `melena` | bool |
| `syncope` | bool |
| `hepatic_disease` | bool |
| `cardiac_failure` | bool |

## Outputs

- `score` (int, 0 to 23).
- `contributing_factors` (tuple of labels, each with its points).
- `risk_band` (`"very_low"`, `"intermediate"`, or `"high"`).
- `outpatient_management_candidate` (True only at score 0).
- `recommended_disposition`, `rationale`.
- `population_caveats`, `citations`.

## Usage

```python
from conditions.upper_gi_bleeding import (
    GlasgowBlatchfordFeatures,
    glasgow_blatchford_assessment,
)

features = GlasgowBlatchfordFeatures(
    sex="male",
    urea_mmol_per_l=5.0,
    hemoglobin_g_per_l=150.0,
    systolic_bp_mmhg=120,
    pulse_per_minute=80,
    melena=False,
    syncope=False,
    hepatic_disease=False,
    cardiac_failure=False,
)
result = glasgow_blatchford_assessment(features)
print(result.score, result.risk_band, result.outpatient_management_candidate)
# 0 very_low True
```

## See also

- [algorithm.md](algorithm.md) — components and bands with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
