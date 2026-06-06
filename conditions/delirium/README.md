# Delirium: 4AT screen

The **4AT** (Bellelli 2014) is a four-item bedside instrument for **rapid delirium screening** in older adults. It takes about two minutes, requires no special training, and — unlike many cognitive tests — can be applied to patients who are too drowsy or agitated to complete formal testing. It is endorsed by SIGN, NICE, and the European Delirium Association.

## Clinical context

Delirium is common, serious, and frequently missed. A short, sensitive screen that works even in uncooperative patients helps flag those who need a full delirium assessment. The 4AT combines a brief orientation test and an attention task with two observational items (alertness and acute change), so a score can be obtained even when the patient cannot engage — inability to test is itself scored.

## Scope of this module

- Computes the **4AT score** (integer, range 0 to 12).
- Returns the **per-item breakdown** (Alertness, AMT4, Attention, Acute change).
- Returns the **interpretation band** (unlikely / possible cognitive impairment / possible delirium) with a narrative action and caveats.

It does **not**:

- Diagnose delirium; a score ≥ 4 is a screening signal that warrants full clinical assessment.
- Distinguish delirium from dementia in a single application — trajectory, serial assessment, and collateral history matter.
- Identify the cause of delirium or recommend specific treatment.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Items

| Item | Levels and points |
|---|---|
| **1. Alertness** | Normal (0); Altered — clearly abnormal, markedly drowsy/stuporous or agitated (4) |
| **2. AMT4** (age, date of birth, place, current year) | No mistakes (0); 1 mistake (1); ≥ 2 mistakes or untestable (2) |
| **3. Attention** (months of the year backwards from December) | 7 or more correct (0); starts but < 7, or refuses (1); untestable (2) |
| **4. Acute change or fluctuating course** | No (0); Yes (4) |

Total range: 0 to 12. "Normal" alertness includes mild sleepiness for under 10 seconds after waking that then resolves.

## Interpretation

| Score | Band | Meaning |
|---|---|---|
| 0 | Unlikely | Delirium and moderate-to-severe cognitive impairment unlikely |
| 1–3 | Possible cognitive impairment | More often chronic cognitive impairment than delirium |
| ≥ 4 | Possible delirium | Possible delirium ± cognitive impairment — full assessment |

The 3/4 cut-off was pre-specified in the design of the instrument, not derived statistically.

## Inputs

| Input | Type |
|---|---|
| `alertness` | `"normal"` / `"altered"` |
| `amt4` | `"no_mistakes"` / `"one_mistake"` / `"two_or_more_mistakes_or_untestable"` |
| `attention_months_backwards` | `"seven_or_more_correct"` / `"fewer_than_seven_or_refuses"` / `"untestable"` |
| `acute_change_or_fluctuating_course` | bool |

## Outputs

- `score` (int, 0 to 12).
- `components` (`FourATComponentScores`: `alertness`, `amt4`, `attention`, `acute_change`).
- `interpretation_band` (`"unlikely"`, `"possible_cognitive_impairment"`, or `"possible_delirium"`).
- `recommended_action`, `rationale`.
- `population_caveats`, `citations`.

## Usage

```python
from conditions.delirium import FourATFeatures, four_at_assessment

features = FourATFeatures(
    alertness="normal",
    amt4="one_mistake",
    attention_months_backwards="fewer_than_seven_or_refuses",
    acute_change_or_fluctuating_course=True,
)
result = four_at_assessment(features)
print(result.score, result.interpretation_band)
# 6 possible_delirium
```

## See also

- [algorithm.md](algorithm.md) — items and bands with citations.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
