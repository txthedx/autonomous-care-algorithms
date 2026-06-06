# Appendicitis: Alvarado score (MANTRELS)

The **Alvarado score** (Alvarado 1986) stratifies the probability of acute appendicitis in patients with suspected appendicitis. It uses eight clinical and laboratory findings — the **MANTRELS** mnemonic — for a total of 0 to 10, and supports decisions about imaging, surgical consultation, and discharge.

## Clinical context

Right-lower-quadrant abdominal pain is a common presentation with a broad differential. The Alvarado score structures the early decision: who is low enough probability for observation or discharge, who needs imaging, and who warrants surgical consultation. It is widely used and externally validated (Ohle 2011), though it performs less well in women of reproductive age and in children.

## Scope of this module

- Computes the **Alvarado score** (integer, range 0 to 10).
- Returns the **contributing factors** (each component that scored, with its points) for auditability.
- Returns the **risk band** (low / moderate / high), a narrative disposition, and population caveats.

It does **not**:

- Diagnose appendicitis; that rests on imaging, operative findings, or histology.
- Replace serial examination, imaging, or clinical judgement.
- Apply a pediatric-specific weighting (a separate pediatric appendicitis score exists; see Samuel 2002).
- Recommend specific operative or antibiotic management.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Units

The laboratory and vital findings are entered as raw measured values in Canadian/SI units: **temperature in °C**, **white cell count in 10⁹/L**, and **neutrophils as a percentage**. The module applies the thresholds. Convert before use if local results are reported in °F or cells/µL.

## Components (MANTRELS)

| Letter | Component | Points | Threshold |
|---|---|---|---|
| **M** | Migration of pain to RLQ | +1 | — |
| **A** | Anorexia | +1 | — |
| **N** | Nausea / vomiting | +1 | — |
| **T** | Tenderness in RLQ | +2 | — |
| **R** | Rebound tenderness | +1 | — |
| **E** | Elevated temperature | +1 | ≥ 37.3 °C |
| **L** | Leukocytosis | +2 | WCC > 10 × 10⁹/L |
| **S** | Shift of WBC to left | +1 | neutrophils > 75% |

Total range: 0 to 10.

## Interpretation

| Score | Risk band | Disposition |
|---|---|---|
| ≤ 4 | Low | Consider alternative diagnoses; observation or discharge with safety-netting |
| 5–6 | Moderate | Imaging (ultrasound first-line in children and women of reproductive age, otherwise CT) and/or active observation |
| ≥ 7 | High | Surgical consultation |

## Inputs

| Input | Type |
|---|---|
| `migration_of_pain_to_rlq` | bool |
| `anorexia` | bool |
| `nausea_or_vomiting` | bool |
| `tenderness_in_rlq` | bool |
| `rebound_tenderness` | bool |
| `temperature_celsius` | float |
| `white_cell_count_x10e9_per_l` | float |
| `neutrophil_percent` | float |

## Outputs

- `score` (int, 0 to 10).
- `contributing_factors` (tuple of labels, each with its points).
- `risk_band` (`"low"`, `"moderate"`, or `"high"`).
- `recommended_disposition`, `rationale`.
- `population_caveats`, `citations`.

## Usage

```python
from conditions.appendicitis import AlvaradoFeatures, alvarado_assessment

features = AlvaradoFeatures(
    migration_of_pain_to_rlq=True,
    anorexia=True,
    nausea_or_vomiting=True,
    tenderness_in_rlq=True,
    rebound_tenderness=False,
    temperature_celsius=37.6,
    white_cell_count_x10e9_per_l=12.5,
    neutrophil_percent=80.0,
)
result = alvarado_assessment(features)
print(result.score, result.risk_band, result.recommended_disposition)
```

## See also

- [algorithm.md](algorithm.md) — components and bands with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
