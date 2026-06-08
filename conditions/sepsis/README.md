# Sepsis: qSOFA (quick SOFA)

The **qSOFA** (Singer 2016, Sepsis-3) is a rapid bedside prompt that flags patients with suspected infection at higher risk of a poor outcome. One point each for respiratory rate ≥ 22/min, altered mentation (GCS < 15), and systolic BP ≤ 100 mmHg. A score ≥ 2 should prompt assessment for organ dysfunction; a score < 2 does **not** rule out sepsis.

It is a prognostic prompt, not a diagnosis, and applies in the context of suspected or confirmed infection. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Inputs

`QsofaFeatures`: `respiratory_rate_per_minute` (int), `glasgow_coma_scale` (int, 3–15), `systolic_bp_mmhg` (int). Raw values; thresholds applied internally.

## Outputs

`score` (0–3), `contributing_factors`, `risk_band` (`"higher_risk"` ≥ 2 / `"lower_risk"`), `recommended_action`, `rationale`, `population_caveats`, `citations`.

## Usage

```python
from conditions.sepsis import QsofaFeatures, qsofa_assessment

result = qsofa_assessment(QsofaFeatures(
    respiratory_rate_per_minute=24, glasgow_coma_scale=14, systolic_bp_mmhg=95,
))
print(result.score, result.risk_band)  # 3 higher_risk
```

See [algorithm.md](algorithm.md), [references.bib](references.bib), and [tests/](tests/).
