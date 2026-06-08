# Croup: Westley Croup Score

The **Westley Croup Score** (Westley 1978) grades croup severity in children from five clinical items (level of consciousness, cyanosis, stridor, air entry, retractions) for a total of 0 to 17.

It is a grading tool, not a diagnosis, and does not exclude other causes of stridor. Severe (6–11) and impending-respiratory-failure (≥ 12) scores warrant urgent intervention. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Bands

| Score | Band |
|---|---|
| ≤ 2 | Mild |
| 3–5 | Moderate |
| 6–11 | Severe |
| ≥ 12 | Impending respiratory failure |

## Inputs

`WestleyFeatures` (named levels): `level_of_consciousness`, `cyanosis`, `stridor`, `air_entry`, `retractions`.

## Usage

```python
from conditions.croup import WestleyFeatures, westley_assessment

r = westley_assessment(WestleyFeatures(
    level_of_consciousness="normal", cyanosis="none", stridor="at_rest",
    air_entry="decreased", retractions="mild",
))
print(r.score, r.severity_band)  # 4 moderate
```

See [algorithm.md](algorithm.md), [references.bib](references.bib), and [tests/](tests/).
