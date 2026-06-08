# Early warning: NEWS2

The **NEWS2** (RCP 2017) aggregates seven physiological parameters (respiration, SpO₂, supplemental oxygen, systolic BP, pulse, consciousness, temperature) to detect and respond to acute deterioration in adults. A single parameter scoring 3 (a "red score") warrants urgent review even at a low aggregate.

Validated in adults only — not children or pregnancy. SpO₂ **Scale 2** is for confirmed hypercapnic (type 2) respiratory failure with a target of 88–92%; otherwise use Scale 1. Clinical judgement overrides the score. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Bands (aggregate)

| Aggregate | Band |
|---|---|
| 0–4 (no parameter = 3) | low |
| any single parameter = 3 | low-medium (red score) |
| 5–6 | medium |
| ≥ 7 | high |

## Inputs

`NewsFeatures`: `respiratory_rate_per_minute`, `spo2_percent`, `on_supplemental_oxygen`, `use_spo2_scale_2`, `systolic_bp_mmhg`, `pulse_per_minute`, `consciousness` (`"alert"` / `"confusion_or_vpu"`), `temperature_celsius`. Raw values; bands applied internally.

## Outputs

`score`, `components` (per-parameter), `any_parameter_scored_3`, `monitoring_band`, `recommended_response`, `rationale`, `population_caveats`, `citations`.

## Usage

```python
from conditions.early_warning import NewsFeatures, news2_assessment

r = news2_assessment(NewsFeatures(
    respiratory_rate_per_minute=26, spo2_percent=95, on_supplemental_oxygen=True,
    use_spo2_scale_2=False, systolic_bp_mmhg=88, pulse_per_minute=110,
    consciousness="alert", temperature_celsius=38.2,
))
print(r.score, r.monitoring_band, r.any_parameter_scored_3)
```

See [algorithm.md](algorithm.md) for the full tables, [references.bib](references.bib), and [tests/](tests/).
