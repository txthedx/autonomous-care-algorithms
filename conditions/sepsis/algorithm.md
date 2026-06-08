# qSOFA (quick SOFA)

A rapid bedside prompt for higher risk of poor outcome in patients with suspected infection.

Source: Singer 2016 (*JAMA*, Sepsis-3 definitions); derivation of the criteria in Seymour 2016 (*JAMA*).

## Criteria (1 point each)

| Criterion | Scores when |
|---|---|
| Respiratory rate | ≥ 22/min |
| Altered mentation | GCS < 15 |
| Systolic blood pressure | ≤ 100 mmHg |

Total range: 0 to 3.

## Interpretation

- **≥ 2** — higher risk of in-hospital mortality or prolonged ICU stay. In a patient with suspected infection, assess for organ dysfunction (full SOFA, lactate) and consider escalation.
- **< 2** — does **not** rule out sepsis or organ dysfunction.

## Use restrictions

qSOFA is a prognostic prompt, not a diagnosis of sepsis, and is applied in the context of suspected or confirmed infection. It is not itself a treatment trigger.

## Implementation note

Respiratory rate, GCS, and systolic BP are entered as raw values; the ≥ 22, < 15, and ≤ 100 thresholds are applied internally. Out-of-range values raise `ValueError` (GCS must be 3–15).

## Citations

- `Singer 2016` — Singer M et al., *JAMA* 2016 (Sepsis-3).
- `Seymour 2016` — Seymour CW et al., *JAMA* 2016 (criteria derivation).
